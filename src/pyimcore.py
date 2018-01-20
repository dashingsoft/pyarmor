# DEPRECATED from v3.4.0.
from imp import find_module, load_module, new_module, PKG_DIRECTORY
import os
import sys

from pytransform import PytransformError, init_runtime, import_module

_ext = '.py' + os.getenv('PYARMOR_EXTRA_CHAR', 'e')

class PyshieldImporter(object):
    '''Import encrypted module or package, package in multi-pathes is not supported.'''

    def __init__(self):
        self.mod_info = None
        self.imp_loader = None

    def find_module(self, name, path=None):
        # From Python3.3, path of package is <class '_frozen_importlib._NamespacePath'>
        path = None if path is None else list(path)
        try:
            self.mod_info = find_module(name, path)
            self.imp_loader = True
            return self
        except ImportError:
            self.imp_loader = None

        m = name.rsplit('.', 1)[-1]
        for dirname in sys.path if path is None else path:
            filename = os.path.join(dirname, m + _ext)
            if os.path.exists(filename):
                self.mod_info = None, filename, None
                return self
            filename = os.path.join(dirname, name, '__init__' + _ext)
            if os.path.exists(filename):
                self.mod_info = None, filename, PKG_DIRECTORY
                return self
        self.mod_info = None

    def load_module(self, name):
        fp, filename, description = self.mod_info
        if self.imp_loader is None:
            m = import_module(name, filename)
            m.__loader__ = self
            if description == PKG_DIRECTORY:
                m.__package__ = name
                m.__path__ = [os.path.dirname(filename)]
        else:
            m = load_module(name, fp, filename, description)
        if not description == PKG_DIRECTORY:
            i = name.rfind('.')
            if not i == -1:
                m.__package__ = name[:i]
        return m

    def load_package(self, name, filenames):
        pkg = new_module(name)
        path = []
        for filename in filenames:
            m = import_module(name, filename)
            path.append(os.path.dirname(filename))
        pkg.__path__ = path
        return pkg

sys.meta_path.append(PyshieldImporter())
init_runtime()
