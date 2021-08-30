'''
This script is used to repack PyInstaller bundle with obfuscated scripts

First pack the script by PyInstaller, next obfuscate the scripts by PyArmor,
finally run this script to repack the bundle with obfuscated scripts.

* Pack the script with PyInstaller, make sure the final bundle works

    # One folder mode
    pyinstaller foo.py

    # Check it works
    dist/foo/foo

    # One file mode
    pyinstaller --onefile foo.py

    # Check it works
    dist/foo

* Obfuscate the scripts to "obfdist", make sure the obfuscated scripts
  work

    # Option --package-runtime should be set to 0
    pyarmor obfuscate -O obfdist --package-runtime 0 foo.py

    # For super mode
    pyarmor obfuscate -O obfdist --advanced 2 foo.py

    # Check it works
    python dist/foo.py

* Repack the final executable, use the same Python interpreter as PyInstaller using

    # One folder mode
    python repack.py -p obfdist dist/foo/foo

    # Overwrite the old one
    cp foo-obf dist/foo/foo

    # One file mode
    python repack.py -p obfdist dist/foo

    # Overwrite the old one
    cp foo-obf dist/foo

Here "foo-obf" is the patched bundle.

'''
import argparse
import logging
import marshal
import os
import shutil
import struct
import sys
import zlib

from subprocess import check_call

from PyInstaller.archive.writers import ZlibArchiveWriter, CArchiveWriter
from PyInstaller.archive.readers import CArchiveReader
from PyInstaller.loader.pyimod02_archive import ZlibArchiveReader
from PyInstaller.loader.pyimod02_archive import PYZ_TYPE_PKG
from PyInstaller.compat import is_darwin, is_linux, is_win


logger = logging.getLogger('repack')


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
            print("Warning: pyz is from a different Python version")
        self.lib.read(4)


class CArchiveWriter2(CArchiveWriter):

    def add(self, entry):
        patched, dlen, ulen, flag, typcd, nm, pathnm = entry
        where = self.lib.tell()

        logger.debug('Add item "%s"', nm)

        if is_darwin and patched and typcd == 'b':
            from PyInstaller.depend import dylib
            dylib.mac_set_relative_dylib_deps(pathnm, os.path.basename(pathnm))

        fh = open(pathnm, 'rb')
        filedata = fh.read()
        fh.close()

        if patched:
            logger.info('Replace item "%s" with "%s"', nm, pathnm)
            if typcd in ('s', 'M'):
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


def get_carchive_info(filepath):
    PYINST_COOKIE_SIZE = 24 + 64        # For pyinstaller 2.1+
    fp = open(filepath, 'rb')
    size = os.stat(filepath).st_size

    fp.seek(size - PYINST_COOKIE_SIZE, os.SEEK_SET)

    # Read CArchive cookie
    magic, lengthofPackage, toc, tocLen, pyver, pylibname = \
        struct.unpack('!8siiii64s', fp.read(PYINST_COOKIE_SIZE))
    fp.close()

    # Overlay is the data appended at the end of the PE
    pos = size - lengthofPackage
    return pos, pylibname.decode()


def append_runtime_files(logic_toc, obfpath):
    logger.info('Appending runtime files to archive')

    n = 0

    def add_toc(typcd, name, pathnm):
        logger.info('Add "%s"', pathnm)
        if os.path.isdir(pathnm):
            raise RuntimeError('It is not allowed to write path "%s" to '
                               'bundle. When obfuscating the scripts, '
                               'make sure "--package-runtime 0" is used',
                               pathnm)
        if n > 1:
            raise RuntimeError('In the path "%s", there are too many '
                               'files start with "pytransform" or '
                               '"_pytransform", there shuold be only one',
                               obfpath)
        logic_toc.append((1, 0, 0, 1, typcd, name, pathnm))

    for name in os.listdir(obfpath):
        pathnm = os.path.join(obfpath, name)
        if (name.startswith('pytransform') and name[-3:] != '.py') \
           or name.startswith('_pytransform'):
            n += 1
            add_toc('b', name, pathnm)
        elif name == 'license.lic':
            add_toc('x', name, pathnm)

    logger.info('Append runtime files OK')


def repack_pyz(pyz, obfpath, cipher=None, clean=False):
    code_dict = {}
    obflist = []

    n = len(obfpath) + 1
    for dirpath, dirnames, filenames in os.walk(obfpath):
        for pyfile in [x for x in filenames if x.endswith('.py')]:
            pyfile = os.path.join(dirpath, pyfile)
            logger.info('Compile %s', pyfile)
            name = pyfile[n:].replace('\\', '.').replace('/', '.')[:-3]
            if name.endswith('__init__.py'):
                name = name[:-len('__init__.py')].strip('.')
            with open(pyfile, 'r') as f:
                source = f.read()
            logger.debug('Got obfuscated item: %s', name)
            code_dict[name] = compile(source, '<%s>' % name, 'exec')
            obflist.append(name)
    logger.info('Got %d obfuscated items', len(obflist))

    logger.info('Patching PYZ file "%s"', pyz)
    arch = ZlibArchive(pyz)

    logic_toc = []
    for name in arch.toc:
        logger.debug('Extract %s', name)
        typ, obj = arch.extract(name)
        if name in obflist:
            logger.info('Replace item "%s" with obfsucated one', name)
            obflist.remove(name)
        else:
            code_dict[name] = obj
        pathname = '__init__.py' if typ == PYZ_TYPE_PKG else name
        logic_toc.append((name, pathname, 'PYMODULE'))
    logger.debug('unhandled obfuscated items are %s', obflist)

    ZlibArchiveWriter(pyz, logic_toc, code_dict=code_dict, cipher=cipher)
    logger.info('Patch PYZ done')


def repack_exe(path, obfname, logic_toc, obfentry, codesign=None):
    logger.info('Repacking EXE "%s"', obfname)

    if is_darwin:
        import PyInstaller.utils.osx as osxutils
        if hasattr(osxutils, 'remove_signature_from_binary'):
            logger.info("Removing signature(s) from EXE")
            osxutils.remove_signature_from_binary(obfname)

    offset, pylib_name = get_carchive_info(obfname)
    logger.info('Get archive info (%d, "%s")', offset, pylib_name)

    pkgname = os.path.join(path, 'PKG-pyarmor-patched')
    logging.info('Patching PKG file "%s"', pkgname)
    CArchiveWriter2(pkgname, logic_toc, pylib_name=pylib_name)
    logging.info('Patch PKG done')

    if is_linux:
        logger.info('Replace section "pydata" with "%s" in EXE', pkgname)
        check_call(['objcopy', '--update-section', 'pydata=%s' % pkgname,
                    obfname])
    else:
        logger.info('Replace PKG with "%s" in EXE', pkgname)
        with open(obfname, 'r+b') as outf:
            # Keep bootloader
            outf.seek(offset, os.SEEK_SET)

            # Write the patched archive
            with open(pkgname, 'rb') as infh:
                shutil.copyfileobj(infh, outf, length=64*1024)

            outf.truncate()

    if is_darwin:
        # Fix Mach-O header for codesigning on OS X.
        logger.info('Fixing EXE for code signing "%s"', obfname)
        import PyInstaller.utils.osx as osxutils
        osxutils.fix_exe_for_code_signing(obfname)

        if hasattr(osxutils, 'sign_binary'):
            logger.info("Re-signing the EXE")
            osxutils.sign_binary(obfname, identity=codesign)

    if is_win:
        # Set checksum to appease antiviral software.
        from PyInstaller.utils.win32 import winutils
        if hasattr(winutils, 'set_exe_checksum'):
            winutils.set_exe_checksum(obfname)

    logger.info('Generate patched bundle "%s" successfully', obfname)


def repacker(executable, obfpath, entry=None, codesign=None):
    logger.info('Repack PyInstaller bundle "%s"', executable)

    obfpath = os.path.normpath(obfpath)
    logger.info('Obfuscated scripts in the path "%s"', obfpath)

    name, ext = os.path.splitext(os.path.basename(executable))
    entry = name if entry is None else entry
    logger.info('Entry script name is "%s.py"', entry)

    arch = CArchiveReader(executable)
    logic_toc = []

    obfentry = os.path.join(obfpath, entry + '.py')
    if not os.path.exists(obfentry):
        raise RuntimeError('No obfuscated script "%s" found', obfentry)

    path = os.path.join(name + '_extracted')
    logger.info('Extracted bundle files to "%s"', path)
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
                logger.info('Extract pyz file "%s"', pathnm)
                repack_pyz(pathnm, obfpath)
                patched = 1
            elif name == nm:
                patched = 1
                pathnm = obfentry
            else:
                patched = 0
            logic_toc.append((patched, dlen, ulen, flag, typcd, nm, pathnm))

    append_runtime_files(logic_toc, obfpath)

    obfname = os.path.join(name + '_obf' + ext)
    shutil.copy2(executable, obfname)
    repack_exe(path, obfname, logic_toc, obfentry, codesign=codesign)


def excepthook(type, exc, traceback):
    try:
        msg = exc.args[0] % exc.args[1:]
    except Exception:
        msg = str(exc)
    logging.error(msg)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
                        default=False,
                        action='store_true',
                        dest='debug',
                        help='print debug log (default: %(default)s)')
    parser.add_argument('-p', '--path',
                        default='obfdist',
                        dest='obfpath',
                        help='obfuscated scripts path (default: %(default)s)')
    parser.add_argument('-e', '--entry',
                        help="Entry script if it's different from bundle name")
    parser.add_argument('--codesign-identity',
                        help="Code signing identity (macOS only).")
    parser.add_argument('executable', metavar='executable',
                        help="PyInstaller archive")

    args = parser.parse_args(sys.argv[1:])
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        sys.excepthook = excepthook
    repacker(args.executable, args.obfpath, args.entry, args.codesign_identity)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
    )
    main()
