import logging
import marshal
import os
import shutil
import struct
import zlib

from subprocess import check_call
from tempfile import TemporaryDirectory

from PyInstaller.archive.writers import ZlibArchiveWriter, CArchiveWriter
from PyInstaller.archive.readers import CArchiveReader
try:
    from PyInstaller.loader.pyimod02_archive import ZlibArchiveReader
    from PyInstaller.loader.pyimod02_archive import PYZ_TYPE_PKG
except ModuleNotFoundError:
    from PyInstaller.loader.pyimod01_archive import ZlibArchiveReader
    from PyInstaller.loader.pyimod01_archive import PYZ_TYPE_PKG
from PyInstaller.compat import is_darwin, is_linux, is_win


logger = logging.getLogger('Packer')


class ZlibArchive(ZlibArchiveReader):

    def checkmagic(self):
        """ Overridable.
            Check to see if the file object self.lib actually has a file
            we understand.
        """
        self.lib.seek(self.start)  # default - magic is at start of file.
        if self.lib.read(len(self.MAGIC)) != self.MAGIC:
            raise RuntimeError("%s is not a valid %s archive file"
                               % (self.path, self.__class__.__name__))
        if self.lib.read(len(self.pymagic)) != self.pymagic:
            logger.warning("pyz is from a different Python version")
        self.lib.read(4)


class CArchiveWriter2(CArchiveWriter):

    def add(self, entry):
        patched, dlen, ulen, flag, typcd, nm, pathnm = entry
        where = self.lib.tell()

        logger.debug('add item "%s"', nm)

        fh = open(pathnm, 'rb')
        filedata = fh.read()
        fh.close()

        if patched:
            logger.info('replace item with "%s"(%s)', pathnm, typcd)
            if typcd.lower() in ('s', 'm'):
                code = compile(filedata, '<%s>' % nm, 'exec')
                filedata = marshal.dumps(code)
                ulen = len(filedata)
            else:
                ulen = len(filedata)

        if flag == 1 and patched:
            comprobj = zlib.compressobj(self.LEVEL)
            self.lib.write(comprobj.compress(filedata))
            self.lib.write(comprobj.flush())
        else:
            self.lib.write(filedata)

        dlen = self.lib.tell() - where
        self.toc.add(where, dlen, ulen, flag, typcd, nm)


def makedirs(path, exist_ok=False):
    if not (exist_ok and os.path.exists(path)):
        os.makedirs(path)


def get_cookie_pos(fp, filesize):
    MAGIC = b'MEI\014\013\012\013\016'
    blocksize = 8192
    end_pos = filesize
    result = -1

    if end_pos < len(MAGIC):
        raise RuntimeError('invalid PyInstaller bundle')

    while True:
        start_pos = end_pos - blocksize if end_pos >= blocksize else 0
        chunksize = end_pos - start_pos

        if chunksize < len(MAGIC):
            break

        fp.seek(start_pos, os.SEEK_SET)
        data = fp.read(chunksize)

        offs = data.rfind(MAGIC)
        if offs != -1:
            result = start_pos + offs
            break

        end_pos = start_pos + len(MAGIC) - 1

        if start_pos == 0:
            break

    if result == -1:
        raise RuntimeError('invalid PyInstaller bundle')

    return result


def get_carchive_info(filepath):
    PYINST_COOKIE_SIZE = 24 + 64        # For pyinstaller 2.1+
    fp = open(filepath, 'rb')
    filesize = os.stat(filepath).st_size
    pos = get_cookie_pos(fp, filesize)
    fp.seek(pos, os.SEEK_SET)

    # Read CArchive cookie
    magic, lengthofPackage, toc, tocLen, pyver, pylibname = \
        struct.unpack('!8sIIii64s', fp.read(PYINST_COOKIE_SIZE))
    fp.close()

    # Overlay is the data appended at the end of the PE
    pos = filesize - lengthofPackage
    return pos, pylibname.decode()


def append_runtime_files(obfpath, rtname):
    logger.info('appending runtime files to archive')
    logic_toc = []

    def add_toc(typcd, name, pathnm):
        logger.info('add "%s"(%s)', pathnm, typcd)
        logic_toc.append((1, 0, 0, 1, typcd, name, pathnm))

    for name in os.listdir(os.path.join(obfpath, rtname)):
        if name.endswith('.py'):
            continue
        typcd = 'x' if name.endswith('key') else 'b'
        pathnm = os.path.join(obfpath, rtname, name)
        distname = '/'.join([rtname, name])
        add_toc(typcd, distname, pathnm)

        if is_darwin and typcd == 'b':
            from PyInstaller.depend import dylib
            logger.debug('mac_set_relative_dylib_deps "%s"', distname)
            dylib.mac_set_relative_dylib_deps(pathnm, distname)

    return logic_toc


def repack_pyz(pyz, obfpath, rtname, cipher=None, clean=False):
    code_dict = {}
    obflist = []

    n = len(obfpath) + 1
    for dirpath, dirnames, filenames in os.walk(obfpath):
        for pyfile in [x for x in filenames if x.endswith('.py')]:
            pyfile = os.path.join(dirpath, pyfile)
            logger.info('compile %s', pyfile)
            name = pyfile[n:].replace('\\', '.').replace('/', '.')[:-3]
            if name.endswith('__init__.py'):
                name = name[:-len('__init__.py')].strip('.')
            with open(pyfile, 'r') as f:
                source = f.read()
            logger.debug('got obfuscated item: %s', name)
            code_dict[name] = compile(source, '<%s>' % name, 'exec')
            obflist.append(name)
    logger.info('got %d obfuscated items', len(obflist))

    logger.info('patching PYZ file "%s"', pyz)
    arch = ZlibArchive(pyz)

    logic_toc = []
    for name in arch.toc:
        logger.debug('extract %s', name)
        typ, obj = arch.extract(name)
        if name in obflist:
            logger.info('replace item "%s" with obfsucated one', name)
            obflist.remove(name)
        else:
            code_dict[name] = obj
        pathname = '__init__.py' if typ == PYZ_TYPE_PKG else name
        logic_toc.append((name, pathname, 'PYMODULE'))

        if name == rtname:
            raise RuntimeError('this bundle has been patched by Pyarmor')

    logic_toc.append((rtname, '__init__.py', 'PYMODULE'))
    pathname = os.path.join(obfpath, rtname, '__init__.py')
    with open(pathname, 'r') as f:
        source = f.read()
    code_dict[rtname] = compile(source, '<%s>' % rtname, 'exec')

    logger.debug('unhandled obfuscated items are %s', obflist)

    ZlibArchiveWriter(pyz, logic_toc, code_dict=code_dict, cipher=cipher)
    logger.info('patch PYZ done')


def repack_exe(path, obfname, logic_toc, obfentry, codesign=None):
    logger.info('repacking EXE "%s"', obfname)

    if is_darwin:
        import PyInstaller.utils.osx as osxutils
        if hasattr(osxutils, 'remove_signature_from_binary'):
            logger.info("removing signature(s) from EXE")
            osxutils.remove_signature_from_binary(obfname)

    offset, pylib_name = get_carchive_info(obfname)
    logger.info('get archive info (%d, "%s")', offset, pylib_name)

    pkgname = os.path.join(path, 'PKG-pyarmor-patched')
    logging.info('patching PKG file "%s"', pkgname)
    CArchiveWriter2(pkgname, logic_toc, pylib_name=pylib_name)
    logging.info('patch PKG done')

    if is_linux:
        logger.info('replace section "pydata" with "%s" in EXE', pkgname)
        check_call(['objcopy', '--update-section', 'pydata=%s' % pkgname,
                    obfname])
    else:
        logger.info('replace PKG with "%s" in EXE', pkgname)
        with open(obfname, 'r+b') as outf:
            # Keep bootloader
            outf.seek(offset, os.SEEK_SET)

            # Write the patched archive
            with open(pkgname, 'rb') as infh:
                shutil.copyfileobj(infh, outf, length=64*1024)

            outf.truncate()

    if is_darwin:
        # Fix Mach-O header for codesigning on OS X.
        logger.info('fixing EXE for code signing "%s"', obfname)
        import PyInstaller.utils.osx as osxutils
        osxutils.fix_exe_for_code_signing(obfname)

        if hasattr(osxutils, 'sign_binary'):
            logger.info("re-signing the EXE")
            osxutils.sign_binary(obfname, identity=codesign)

    if is_win:
        # Set checksum to appease antiviral software.
        from PyInstaller.utils.win32 import winutils
        if hasattr(winutils, 'set_exe_checksum'):
            winutils.set_exe_checksum(obfname)

    logger.info('generate patched bundle "%s" successfully', obfname)


def repacker(executable, obfpath, buildpath='', entry=None, codesign=None):
    logger.info('repack bundle "%s"', executable)

    obfpath = os.path.normpath(obfpath)
    logger.info('obfuscated scripts at "%s"', obfpath)

    name, ext = os.path.splitext(os.path.basename(executable))
    entry = name if entry is None else entry
    logger.info('entry script name is "%s.py"', entry)

    arch = CArchiveReader(executable)
    logic_toc = []

    obfentry = os.path.join(obfpath, entry + '.py')
    if not os.path.exists(obfentry):
        raise RuntimeError('no obfuscated entry "%s" found', obfentry)

    for item in os.listdir(obfpath):
        if item.startswith('pyarmor_runtime_'):
            logger.info('runtime package is "%s"', item)
            rtname = item
            break
    else:
        raise RuntimeError('no runtime package found')

    path = os.path.join(buildpath, name + '_extracted')
    logger.info('extracted bundle files to "%s"', path)
    makedirs(path, exist_ok=True)

    for item in arch.toc:
        logger.debug('toc: %s', item)
        dpos, dlen, ulen, flag, typcd, nm = item
        pathnm = os.path.join(path, nm)
        makedirs(os.path.dirname(pathnm), exist_ok=True)
        with arch.lib:
            arch.lib.seek(arch.pkg_start + dpos)
            with open(pathnm, 'wb') as f:
                f.write(arch.lib.read(dlen))

            if nm.endswith('.pyz') and typcd in ('z', 'Z'):
                logger.info('extract pyz file "%s"', pathnm)
                repack_pyz(pathnm, obfpath, rtname)
                patched = 1
            elif name == nm:
                patched = 1
                pathnm = obfentry
            else:
                patched = 0
            logic_toc.append((patched, dlen, ulen, flag, typcd, nm, pathnm))

    extra_toc = append_runtime_files(obfpath, rtname)
    if len(logic_toc) > 10:
        logic_toc.extend(extra_toc)
    else:
        dest = os.path.dirname(executable)
        logger.info('copy runtime files to "%s"', dest)
        os.makedirs(os.path.join(dest, rtname), exist_ok=True)
        for item in extra_toc:
            shutil.copy2(item[-1], os.path.join(dest, item[-2]))

    obfname = os.path.join(buildpath, name + '_obf' + ext)
    shutil.copy2(executable, obfname)
    repack_exe(path, obfname, logic_toc, obfentry, codesign=codesign)

    logger.info('move "%s" to "%s"', obfname, executable)
    shutil.move(obfname, executable)


def list_modules(executable):
    modules = []
    arch = CArchiveReader(executable)

    def read_toc(nm, dlen):
        with TemporaryDirectory() as tmp:
            path = os.path.join(tmp, nm)
            with open(path, 'wb') as f:
                f.write(arch.lib.read(dlen))
            return ZlibArchiveReader(path).toc

    for item in arch.toc:
        logger.debug('toc: %s', item)
        dpos, dlen, ulen, flag, typcd, nm = item
        with arch.lib:
            arch.lib.seek(arch.pkg_start + dpos)
            if nm.endswith('.pyz') and typcd in ('z', 'Z'):
                modules.extend(read_toc(nm, dlen))

    return modules
