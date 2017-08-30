# It seems imp must be imported even if there is no used in module
import imp
import os
import sys

from pytransform import PytransformError, init_runtime, import_module

ext_char = os.getenv('PYARMOR_EXTRA_CHAR', 'e')
ext_list = [x + ext_char for x in ('.py', '.pyc', '.pyo')]

class PyshieldImporter(object):

    def __init__(self):
        self.filename = ''

    def find_module(self, fullname, path=None):
        _name = fullname.rsplit('.', 1)[-1]
        for dirname in sys.path if path is None else path:
            for ext in ext_list:
                self.filename = os.path.join(dirname, _name + ext)
                if os.path.exists(self.filename):
                    return self
        self.filename = ''

    def load_module(self, fullname):
        ispkg = 0
        try:
            mod = import_module(fullname, self.filename)
            mod.__file__ = '<pytransform>'
            mod.__loader__ = self
        except Exception:
            raise ImportError('Import module from %s failed' % fullname)
        return mod

sys.meta_path.append(PyshieldImporter())
init_runtime()
