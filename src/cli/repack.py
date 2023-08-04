import logging
import marshal
import os
import shutil
import struct
import tempfile

from importlib._bootstrap_external import _code_to_timestamp_pyc
from subprocess import check_call, check_output, DEVNULL

from PyInstaller.archive.writers import ZlibArchiveWriter, CArchiveWriter
from PyInstaller.archive.readers import CArchiveReader
try:
    from PyInstaller.loader.pyimod02_archive import ZlibArchiveReader
except ModuleNotFoundError:
    # Since 5.3
    from PyInstaller.loader.pyimod01_archive import ZlibArchiveReader
from PyInstaller.compat import is_darwin, is_linux, is_win


# Type codes for PYZ PYZ entries
PYZ_ITEM_MODULE = 0
PYZ_ITEM_PKG = 1
PYZ_ITEM_DATA = 2
PYZ_ITEM_NSPKG = 3  # PEP-420 namespace package

# Type codes for CArchive TOC entries
PKG_ITEM_BINARY = 'b'  # binary
PKG_ITEM_DEPENDENCY = 'd'  # runtime option
PKG_ITEM_PYZ = 'z'  # zlib (pyz) - frozen Python code
PKG_ITEM_ZIPFILE = 'Z'  # zlib (pyz) - frozen Python code
PKG_ITEM_PYPACKAGE = 'M'  # Python package (__init__.py)
PKG_ITEM_PYMODULE = 'm'  # Python module
PKG_ITEM_PYSOURCE = 's'  # Python script (v3)
PKG_ITEM_DATA = 'x'  # data
PKG_ITEM_RUNTIME_OPTION = 'o'  # runtime option
PKG_ITEM_SPLASH = 'l'  # splash resources

# Path suffix for extracted contents
EXTRACT_SUFFIX = '_extracted'


logger = logging.getLogger('repack')


class CArchiveReader2(CArchiveReader):

    def find_magic_pattern(self, fp, magic_pattern):
        # Start at the end of file, and scan back-to-start
        fp.seek(0, os.SEEK_END)
        end_pos = fp.tell()

        # Scan from back
        SEARCH_CHUNK_SIZE = 8192
        magic_offset = -1
        while end_pos >= len(magic_pattern):
            start_pos = max(end_pos - SEARCH_CHUNK_SIZE, 0)
            chunk_size = end_pos - start_pos
            # Is the remaining chunk large enough to hold the pattern?
            if chunk_size < len(magic_pattern):
                break
            # Read and scan the chunk
            fp.seek(start_pos, os.SEEK_SET)
            buf = fp.read(chunk_size)
            pos = buf.rfind(magic_pattern)
            if pos != -1:
                magic_offset = start_pos + pos
                break
            # Adjust search location for next chunk; ensure proper overlap
            end_pos = start_pos + len(magic_pattern) - 1

        return magic_offset

    def get_cookie_info(self, fp):
        magic = getattr(self, '_COOKIE_MAGIC_PATTERN',
                        getattr(self, 'MAGIC', b'MEI\014\013\012\013\016'))
        cookie_pos = self.find_magic_pattern(fp, magic)

        cookie_format = getattr(self, '_COOKIE_FORMAT',
                                getattr(self, '_cookie_format', '!8sIIii64s'))
        cookie_size = struct.calcsize(cookie_format)

        fp.seek(cookie_pos, os.SEEK_SET)
        return struct.unpack(cookie_format, fp.read(cookie_size))

    def get_toc(self):
        if isinstance(self.toc, dict):
            return self.toc
        return {entry[-1]: entry[:-1] for entry in self.toc}

    def open_pyzarchive(self, name):
        if hasattr(self, 'open_embedded_archive'):
            return self.open_embedded_archive(name)

        ndx = self.toc.find(name)
        (dpos, dlen, ulen, flag, typcd, nm) = self.toc.get(ndx)
        return ZlibArchiveReader(self.path, self.pkg_start + dpos)

    def get_logical_toc(self, buildpath, obfpath):
        logical_toc = []

        for name, entry in self.get_toc().items():
            *_, flag, typecode = entry
            if typecode == PKG_ITEM_PYMODULE:
                source = os.path.join(obfpath, name + '.py')
            elif typecode == PKG_ITEM_PYSOURCE:
                source = os.path.join(obfpath, name + '.py')
            elif typecode == PKG_ITEM_PYPACKAGE:
                source = os.path.join(obfpath, name, '__init__.py')
            elif typecode == PKG_ITEM_PYZ:
                source = os.path.join(buildpath, name)
            elif typecode in (PKG_ITEM_DEPENDENCY, PKG_ITEM_RUNTIME_OPTION):
                source = ''
            else:
                source = None
            if source and not os.path.exists(source):
                source = None
            logical_toc.append((name, source, flag, typecode))

        return logical_toc


class CArchiveWriter2(CArchiveWriter):

    def __init__(self, pkg_arch, archive_path, logical_toc, pylib_name):
        self._orgarch = pkg_arch
        super().__init__(archive_path, logical_toc, pylib_name)

    def _write_rawdata(self, name, typecode, compress):
        rawdata = fix_extract(self._orgarch.extract(name))
        if hasattr(self, '_write_blob'):
            # Since 5.0
            self._write_blob(rawdata, name, typecode, compress)
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            pathname = os.path.join(tmpdir,
                                    name.replace('/', '_').replace('\\', '_'))
            with open(pathname, 'wb') as f:
                f.write(rawdata)
            if typecode in (PKG_ITEM_PYSOURCE, PKG_ITEM_PYMODULE,
                            PKG_ITEM_PYPACKAGE):
                super().add((name, pathname, compress, PKG_ITEM_DATA))
                tc = self.toc.data[-1]
                self.toc.data[-1] = tc[:-2] + (typecode, tc[-1])
            else:
                super().add((name, pathname, compress, typecode))

    def add(self, entry):
        name, source, compress, typecode = entry[:4]
        if source is None:
            self._write_rawdata(name, typecode, compress)
        else:
            logger.info('replace entry "%s"', name)
            super().add(entry)

    def _write_entry(self, fp, entry):
        '''For PyInstaller 5.10+'''
        name, source, compress, typecode = entry[:4]
        if source is None:
            rawdata = self._orgarch.extract(name)
            return self._write_blob(fp, rawdata, name, typecode, compress)
        return super()._write_entry(fp, entry)


def fix_extract(data):
    return data[1] if isinstance(data, tuple) else data


def extract_pyzarchive(name, pyzarch, output):
    dirname = os.path.join(output, name + EXTRACT_SUFFIX)
    os.makedirs(dirname, exist_ok=True)

    for name, (typecode, offset, length) in pyzarch.toc.items():
        # Prevent writing outside dirName
        filename = name.replace('..', '__').replace('.', os.path.sep)
        if typecode == PYZ_ITEM_PKG:
            filepath = os.path.join(dirname, filename, '__init__.pyc')
        elif typecode == PYZ_ITEM_MODULE:
            filepath = os.path.join(dirname, filename + '.pyc')
        elif typecode == PYZ_ITEM_DATA:
            filepath = os.path.join(dirname, filename)
        elif typecode == PYZ_ITEM_NSPKG:
            filepath = os.path.join(dirname, filename, '__init__.pyc')
        else:
            continue
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(_code_to_timestamp_pyc(fix_extract(pyzarch.extract(name))))

    return dirname


def repack_pyzarchive(pyzpath, pyztoc, obfpath, rtname, cipher=None):
    # logic_toc tuples: (name, src_path, typecode)
    #   `name` is the name without suffix)
    #   `src_path` is name of the file from which the resource is read
    #   `typecode` is the Analysis-level TOC typecode (`PYMODULE` or `DATA`)
    logical_toc = []
    code_dict = {}
    extract_path = pyzpath + EXTRACT_SUFFIX

    def compile_item(name, filename):
        fullpath = os.path.join(obfpath, filename)
        if not os.path.exists(fullpath):
            fullpath = fullpath + 'c'
        if os.path.exists(fullpath):
            logger.info('replace item "%s"', name)
            with open(fullpath, 'r') as f:
                co = compile(f.read(), '<frozen %s>' % name, 'exec')
                code_dict[name] = co
        else:
            fullpath = os.path.join(extract_path, filename + 'c')
            with open(fullpath, 'rb') as f:
                f.seek(16)
                code_dict[name] = marshal.load(f)
        return fullpath

    fullpath = os.path.join(obfpath, rtname, '__init__.py')
    logical_toc.append((rtname, fullpath, 'PYMODULE'))
    compile_item(rtname, os.path.join(rtname, '__init__.py'))

    for name, (typecode, offset, length) in pyztoc.items():
        ptname = name.replace('..', '__').replace('.', os.path.sep)
        pytype = 'PYMODULE'
        if typecode == PYZ_ITEM_PKG:
            fullpath = compile_item(name, os.path.join(ptname, '__init__.py'))
        elif typecode == PYZ_ITEM_MODULE:
            fullpath = compile_item(name, ptname + '.py')
        elif typecode == PYZ_ITEM_DATA:
            fullpath = os.path.join(extract_path, ptname)
            pytype = 'DATA'
        elif typecode == PYZ_ITEM_NSPKG:
            fullpath = compile_item(name, os.path.join(ptname, '__init__.py'))
            fullpath = '-'
        else:
            raise ValueError('unknown PYZ item type "%s"' % typecode)
        logical_toc.append((name, fullpath, pytype))

    ZlibArchiveWriter(pyzpath, logical_toc, code_dict, cipher=cipher)


def repack_carchive(executable, pkgfile, buildpath, obfpath, rtentry):
    pkgarch = CArchiveReader2(executable)
    with open(executable, 'rb') as fp:
        *_, pylib_name = pkgarch.get_cookie_info(fp)
    logical_toc = pkgarch.get_logical_toc(buildpath, obfpath)
    if rtentry is not None:
        logical_toc.append(rtentry)
    pylib_name = pylib_name.strip(b'\x00').decode('utf-8')
    CArchiveWriter2(pkgarch, pkgfile, logical_toc, pylib_name)


def repack_executable(executable, buildpath, obfpath, rtentry, codesign=None):
    pkgname = 'PKG-patched'

    logger.info('repacking PKG "%s"', pkgname)
    pkgfile = os.path.join(buildpath, pkgname)
    repack_carchive(executable, pkgfile, buildpath, obfpath, rtentry)

    logger.info('repacking EXE "%s"', executable)

    if is_darwin:
        import PyInstaller.utils.osx as osxutils
        if hasattr(osxutils, 'remove_signature_from_binary'):
            logger.info("remove signature(s) from EXE")
            osxutils.remove_signature_from_binary(executable)

    if is_linux:
        logger.info('replace section "pydata" with "%s"', pkgname)
        check_call(['objcopy', '--update-section', 'pydata=%s' % pkgfile,
                    executable])
    else:
        reader = CArchiveReader2(executable)
        logger.info('replace PKG with "%s"', pkgname)
        with open(executable, 'r+b') as outf:
            info = reader.get_cookie_info(outf)
            offset = os.fstat(outf.fileno()).st_size - info[1]
            # Keep bootloader
            outf.seek(offset, os.SEEK_SET)

            # Write the patched archive
            with open(pkgfile, 'rb') as infh:
                shutil.copyfileobj(infh, outf, length=64*1024)

            outf.truncate()

        if is_darwin:
            # Fix Mach-O header for codesigning on OS X.
            logger.info('fixing EXE for code signing')
            import PyInstaller.utils.osx as osxutils
            osxutils.fix_exe_for_code_signing(executable)
            # Since PyInstaller 4.4
            if hasattr(osxutils, 'sign_binary'):
                logger.info("re-signing the EXE")
                osxutils.sign_binary(executable, identity=codesign)

        elif is_win:
            # Set checksum to appease antiviral software.
            from PyInstaller.utils.win32 import winutils
            if hasattr(winutils, 'set_exe_checksum'):
                winutils.set_exe_checksum(executable)

    logger.info('generate patched bundle "%s" successfully', executable)


class Repacker:

    def __init__(self, executable, buildpath, codesign=None):
        self.executable = executable
        self.buildpath = buildpath
        self.codesign = codesign
        self.extract_carchive(executable, buildpath)

    def extract_carchive(self, executable, buildpath, clean=True):
        logger.info('extracting bundle "%s"', executable)
        if os.path.exists(self.buildpath):
            shutil.rmtree(self.buildpath)
        os.makedirs(self.buildpath)

        contents = []
        pkgarch = CArchiveReader2(executable)
        pkgtoc = pkgarch.get_toc()

        with open(executable, 'rb') as fp:
            *_, pylib_name = pkgarch.get_cookie_info(fp)
        self.pylib_name = pylib_name.strip(b'\x00').decode('utf-8')
        logger.debug('pylib_name is "%s"', self.pylib_name)

        for name, toc_entry in pkgtoc.items():
            logger.debug('extract %s', name)
            *_, typecode = toc_entry

            if typecode == PKG_ITEM_PYZ:
                pyzarch = pkgarch.open_pyzarchive(name)
                self.pyztoc = pyzarch.toc
                contents.append(extract_pyzarchive(name, pyzarch, buildpath))

        self.contents = contents
        self.one_file_mode = len(pkgtoc) > 10 and not any([
            x.name == 'base_library.zip'
            for x in os.scandir(os.path.dirname(executable))])
        logger.debug('one file mode is %s', bool(self.one_file_mode))

    def repack(self, obfpath, rtname, entry=None):
        buildpath = self.buildpath
        executable = self.executable
        codesign = self.codesign
        logger.info('repacking bundle "%s"', executable)

        obfpath = os.path.normpath(obfpath)
        logger.info('obfuscated scripts at "%s"', obfpath)

        name, ext = os.path.splitext(os.path.basename(executable))
        entry = name if entry is None else entry
        logger.info('entry script name is "%s.py"', entry)

        rtpath = os.path.join(obfpath, rtname)
        logger.debug('runtime package at %s', rtpath)
        for item in self.contents:
            if item.endswith(EXTRACT_SUFFIX):
                pyzpath = item[:-len(EXTRACT_SUFFIX)]
                logger.info('repacking "%s"', os.path.basename(pyzpath))
                repack_pyzarchive(pyzpath, self.pyztoc, obfpath, rtname)

        for x in os.listdir(rtpath):
            ext = os.path.splitext(x)[-1]
            if x.startswith('pyarmor_runtime') and ext in ('.so', '.pyd'):
                rtbinary = os.path.join(rtpath, x)
                rtbinname = os.path.join(rtname, x)
                break
        else:
            raise RuntimeError('no pyarmor runtime files found')

        if is_darwin:
            # Not required since 8.3.0
            # from PyInstaller.depend import dylib
            # self._fixup_darwin_rtbinary(rtbinary, self.pylib_name)
            # logger.debug('mac_set_relative_dylib_deps "%s"', rtbinname)
            # dylib.mac_set_relative_dylib_deps(rtbinary, rtbinname)

            import PyInstaller.utils.osx as osxutils
            # Since PyInstaller 4.4
            if hasattr(osxutils, 'sign_binary'):
                logger.info('re-signing "%s"', os.path.basename(rtbinary))
                osxutils.sign_binary(rtbinary, identity=codesign)

        rtentry = (rtbinname, rtbinary, 1, 'b') if self.one_file_mode else None
        if not self.one_file_mode:
            dest = os.path.join(os.path.dirname(executable), rtname)
            os.makedirs(dest, exist_ok=True)
            shutil.copy2(rtbinary, dest)

        repack_executable(executable, buildpath, obfpath, rtentry, codesign)

    def _fixup_darwin_rtbinary(self, rtbinary, pylib_name):
        from sys import version_info as pyver
        pylib = os.path.normpath(os.path.join('@rpath', pylib_name))
        output = check_output(['otool', '-L', rtbinary])
        for line in output.splitlines():
            if line.find(b'libpython%d.%d.dylib' % pyver[:2]) > 0:
                reflib = line.split()[0].decode()
                if reflib.endswith(pylib_name):
                    return
                break
            elif line.find(pylib.encode()) > 0:
                return
            # Only for debug
            elif line.find(b'/Python ') > 0:
                return
        else:
            logger.warning('fixup dylib failed, no CPython library found')

        cmdlist = ['install_name_tool', '-change', reflib, pylib, rtbinary]
        try:
            logger.info('%s', ' '.join(cmdlist))
            check_call(cmdlist, stdout=DEVNULL, stderr=DEVNULL)
        except Exception as e:
            logger.warning('%s', e)
