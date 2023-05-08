import logging
import marshal
import os
import shutil
import struct
import tempfile

from importlib._bootstrap_external import _code_to_timestamp_pyc
from subprocess import check_call

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

    # Cookie - holds some information for the bootloader.
    #
    #   typedef struct _cookie {
    #       char magic[8]; /* 'MEI\014\013\012\013\016' */
    #       uint32_t len;  /* len of entire package */
    #       uint32_t TOC;  /* pos (rel to start) of TableOfContents */
    #       int  TOClen;   /* length of TableOfContents */
    #       int  pyvers;   /* new in v4 */
    #       char pylibname[64];    /* Filename of Python dynamic library. */
    #   } COOKIE;
    #

    # TOC entry:
    #
    #   typedef struct _toc {
    #       int  structlen;  /* len of this one - including full len of name */
    #       uint32_t pos;    /* pos rel to start of concatenation */
    #       uint32_t len;    /* len of the data (compressed) */
    #       uint32_t ulen;   /* len of data (uncompressed) */
    #       char cflag;      /* is it compressed (really a byte) */
    #       char typcd;      /* type code -'b' binary, 'z' zlib, 'm' module,
    #                         * 's' script (v3),'x' data, 'o' runtime option  */
    #       char name[1];    /* the name to save it as */
    #                        /* starting in v5, we stretch this out to a mult of 16 */
    #   } TOC;
    #

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
            return self.open_embedded_archive(self, name)

        ndx = self.toc.find(name)
        (dpos, dlen, ulen, flag, typcd, nm) = self.toc.get(ndx)
        return ZlibArchiveReader(self.path, self.pkg_start + dpos)

    def get_logical_toc(self, path):
        logical_toc = []
        for name, entry in self.get_toc().items():
            *_, flag, typecode = entry
            if typecode in (PKG_ITEM_PYMODULE, PKG_ITEM_PYSOURCE):
                source = os.path.join(path, name + '.pyc')
            elif typecode == PKG_ITEM_PYPACKAGE:
                source = os.path.join(path, name, '__init__.pyc')
            elif typecode == PKG_ITEM_PYZ:
                source = os.path.join(path, name)
            else:
                source = None
            item = name, source, flag, typecode
            logical_toc.append(item)

        return logical_toc


class CArchiveWriter2(CArchiveWriter):

    def __init__(self, archive_path, logical_toc, pylib_name, src_arch):
        self._carch = src_arch
        super().__init__(archive_path, logical_toc, pylib_name)

    def _write_rawdata(self, name, typecode, compress):
        rawdata = self._carch.extract(name)
        if hasattr(self, '_write_blob'):
            # Since 5.0
            return self._write_blob(rawdata, name, typecode, compress)
        with tempfile.NamedTemporaryFile() as f:
            f.write(rawdata)
            f.flush()
            return self.add((name, f.name, typecode, compress))

    def add(self, entry):
        name, source, compress, typecode = entry[:4]
        if source is None:
            return self._write_rawdata(name, typecode, compress)
        return super().add(entry)

    def _write_entry(self, fp, entry):
        '''For PyInstaller 5.10+'''
        name, source, compress, typecode = entry[:4]
        if source is None:
            rawdata = self._carch.extract(name)
            return self._write_blob(fp, rawdata, name, typecode, compress)
        return super()._write_entry(fp, entry)


def fix_extract(data):
    return data[1] if isinstance(data, tuple) else data


def extract_pyzarchive(name, pyzarch, output):
    dirname = os.path.join(output, name + EXTRACT_SUFFIX)
    os.makedirs(dirname, exist_ok=True)

    for name, (typecode, offset, length) in pyzarch.toc.items:
        # Prevent writing outside dirName
        filename = name.replace('..', '__').replace('.', os.path.sep)
        if typecode == PYZ_ITEM_PKG:
            filepath = os.path.join(dirname, filename, '__init__.pyc')
        elif typecode == PYZ_ITEM_MODULE:
            filepath = os.path.join(dirname, filename + '.pyc')
        elif typecode == PYZ_ITEM_DATA:
            filepath = os.path.join(dirname, filename)
        else:
            continue
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(_code_to_timestamp_pyc(fix_extract(pyzarch.extract(name))))

    return dirname


def repack_pyzarchive(pyzpath, pyztoc, obfpath, rtpath, cipher=None):
    # logic_toc tuples: (name, src_path, typecode)
    #   `name` is the name without suffix)
    #   `src_path` is name of the file from which the resource is read
    #   `typecode` is the Analysis-level TOC typecode (`PYMODULE` or `DATA`)
    logical_toc = []
    code_dict = {}

    def compile_item(name, fullpath):
        with open(fullpath, 'r') as f:
            return compile(f.read(), '<frozen %s>' % name, 'exec')

    rtname = os.path.basename(rtpath)
    filepath = os.path.join(rtpath, '__init__.py')
    logical_toc.append((rtname, filepath, 'PYMODULE'))
    code_dict[rtname] = compile_item(rtname, filepath)

    for name, (typecode, offset, length) in pyztoc.items:
        filename = name.replace('..', '__').replace('.', os.path.sep)
        if typecode == PYZ_ITEM_PKG:
            filepath = os.path.join(obfpath, filename, '__init__.py')
            code_dict[name] = compile_item(name, filepath)
        elif typecode == PYZ_ITEM_MODULE:
            filepath = os.path.join(obfpath, filename + '.py')
            code_dict[name] = compile_item(name, filepath)
        elif typecode == PYZ_ITEM_DATA:
            filepath = os.path.join(obfpath, filename)
        elif typecode == PYZ_ITEM_NSPKG:
            filepath = '-'
        else:
            raise ValueError('unknown PYZ item type "%s"' % typecode)
        logical_toc.append((name, filepath, 'DATA'
                            if typecode == PYZ_ITEM_DATA else 'PYMODULE'))

    ZlibArchiveWriter(pyzpath, logical_toc, code_dict, cipher=cipher)


def repack_carchive(executable, buildpath, logical_toc, pkgname):
    destfile = os.path.join(buildpath, pkgname)
    pkgarch = CArchiveReader2(executable)
    *_, pylib_name = pkgarch.get_cookie_info()
    CArchiveWriter2(destfile, logical_toc, pylib_name.decode('utf-8'))


def repack_executable(executable, pkgname, codesign=None):
    logger.info('repacking EXE "%s"', executable)

    if is_darwin:
        import PyInstaller.utils.osx as osxutils
        if hasattr(osxutils, 'remove_signature_from_binary'):
            logger.info("removing signature(s) from EXE")
            osxutils.remove_signature_from_binary(executable)

    if is_linux:
        logger.info('replace section "pydata" with "%s"', pkgname)
        check_call(['objcopy', '--update-section', 'pydata=%s' % pkgname,
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
            with open(pkgname, 'rb') as infh:
                shutil.copyfileobj(infh, outf, length=64*1024)

            outf.truncate()

        if is_darwin:
            # Fix Mach-O header for codesigning on OS X.
            logger.info('fixing EXE for code signing')
            import PyInstaller.utils.osx as osxutils
            osxutils.fix_exe_for_code_signing(executable)

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

    def __init__(self, executable, buildpath):
        self.executable = executable
        self.buildpath = buildpath
        self.extract_carchive(executable, buildpath)

    def extract_carchive(self, executable, buildpath, clean=True):
        logger.info('extracting bundle "%s"', executable)
        shutil.rmtree(self.buildpath)
        os.makedirs(self.buildpath)

        contents = []
        pyz_tocs = {}
        pkgarch = CArchiveReader2(executable)

        def write_raw_pyc(filename):
            data = fix_extract(pkgarch.extract(name))
            try:
                data = _code_to_timestamp_pyc(marshal.loads(data))
            except Exception:
                pass
            with open(filename, 'wb') as f:
                f.write(data)
            contents.append(filename)

        for name, toc_entry in pkgarch.get_toc().items():
            logger.debug('extract %s', name)
            *_, typecode = toc_entry

            if typecode == PKG_ITEM_PYZ:
                pyzarch = pkgarch.open_pyzarchive(name)
                pyz_tocs[name] = pyzarch.toc
                contents.append(extract_pyzarchive(name, pyzarch, buildpath))

            elif typecode == PKG_ITEM_PYPACKAGE:
                filename = os.path.join(buildpath, name, '__init__.pyc')
                write_raw_pyc(filename)

            elif typecode in (PKG_ITEM_PYMODULE, PKG_ITEM_PYSOURCE):
                filename = os.path.join(buildpath, name + '.pyc')
                write_raw_pyc(filename)

        self.contents = contents
        self.logical_toc = pkgarch.get_logical_toc(buildpath)
        self.pyz_tocs = pyz_tocs

    def repack(self, obfpath, rtname, entry=None):
        executable = self.executable
        logger.info('repack bundle "%s"', executable)

        obfpath = os.path.normpath(obfpath)
        logger.info('obfuscated scripts at "%s"', obfpath)

        name, ext = os.path.splitext(os.path.basename(executable))
        entry = name if entry is None else entry
        logger.info('entry script name is "%s.py"', entry)

        rtpath = os.path.join(obfpath, rtname)
        for item in self.contents:
            if item.endswith(EXTRACT_SUFFIX):
                pyzpath = item[:-len(EXTRACT_SUFFIX)]
                pyztoc = self.pyz_tocs[os.path.basename(pyzpath)]
                logger.info('repack "%s"', os.path.basename(pyzpath))
                repack_pyzarchive(pyzpath, pyztoc, obfpath, rtpath)

        for x in os.listdir(rtpath):
            ext = os.path.splitext(x)[-1]
            if x.startswith('pyarmor_runtime') and ext in ('.so', '.pyd'):
                rtbinary = os.path.join(rtpath, x)
                rtbinname = '.'.join([rtname, x])
                break

        if len(self.logical_toc) > 10:
            self.logical_toc.append((rtbinname, rtbinary, 1, PKG_ITEM_BINARY))
        else:
            dest = os.path.join(os.path.dirname(executable), rtname)
            os.makedirs(dest, exist_ok=True)
            shutil.copyfile(rtbinary, dest)

        pkgname = 'PKG-patched'
        repack_carchive(executable, self.buildpath, self.logical_toc, pkgname)

        repack_executable(executable, pkgname)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(message)s',
    )
    dest = '.pyarmor/pack'
    os.makedirs(dest, exist_ok=True)
