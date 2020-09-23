#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 - 2018 Dashingsoft corp.            #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 3.4.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: project.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2018/01/15
#
#  @Description:
#
#   Define project object.
#
#  @Change Log:
#    1.0.0: Initial.
#    1.0.1: Add title
#    1.0.2: Add disable_restrict_mode
#    1.1.0: Add cross_protection, obf_code, obf_mod, wrap_mode, plugins
#    1.2.0: Add platform
#    1.2.1: Add advanced_mode
#    1.2.2: Remove disable_restrice_mode, add restrict_mode
#    1.2.3: Add package_runtime
#    1.2.4: Add enable_suffix, remove obf_module_mode and obf_code_mode
#
#    2.0: Add license_file, bootstrap_code
#         Remove attribute capsule
#
import os
import time
from distutils.filelist import FileList
from distutils.text_file import TextFile
from glob import glob
from io import StringIO
from json import dump as json_dump, load as json_load

from config import config_filename, default_output_path, \
                   default_manifest_template


class Project(dict):

    VERSION = 2, 0

    OBF_MODULE_MODE = 'none', 'des', 'aes'

    OBF_CODE_MODE = 'none', 'fast', 'aes', 'wrap'

    DEFAULT_VALUE = \
        ('version', '.'.join([str(x) for x in VERSION])), \
        ('name', None), \
        ('title', None), \
        ('src', None), \
        ('is_package', None), \
        ('manifest', default_manifest_template), \
        ('entry', None), \
        ('output', default_output_path), \
        ('runtime_path', None), \
        ('restrict_mode', 1), \
        ('obf_code', 1), \
        ('obf_mod', 2), \
        ('wrap_mode', 1), \
        ('advanced_mode', 0), \
        ('bootstrap_code', 1), \
        ('cross_protection', 1), \
        ('plugins', None), \
        ('platform', None), \
        ('package_runtime', 1), \
        ('enable_suffix', 0), \
        ('license_file', None), \
        ('build_time', 0.)

    def __init__(self, *args, **kwargs):
        self._path = ''
        for k, v in Project.DEFAULT_VALUE:
            kwargs.setdefault(k, v)
        super(Project, self).__init__(*args, **kwargs)

    def _format_path(self, path):
        return os.path.normpath(path if os.path.isabs(path)
                                else os.path.join(self._path, path))

    def __getattr__(self, name):
        if name in ('src', 'output'):
            return self._format_path(self[name])
        elif name == 'license_file':
            v = self[name] if name in self else None
            return v if v in ('no', 'outer') \
                else self._format_path(v) if v else None
        if name in self:
            return self[name]
        raise AttributeError(name)

    def _update(self, kwargs):
        result = []
        for name in dict(Project.DEFAULT_VALUE).keys():
            value = kwargs.get(name)
            if value is not None:
                self[name] = value
                result.append(name)
        self['build_time'] = 0.
        return result

    def _check(self, path):
        assert os.path.exists(os.path.normpath(path)), \
            'Project path %s does not exists' % path

        assert os.path.exists(self.src), \
            'The src of this project is not found: %s' % self.src
        assert os.path.isabs(self.src), \
            'The src of this project is not absolute path'
        assert self.src != self.output, \
            'The output path can not be same as src in the project'

        assert self.license_file is None \
            or self.license_file == 'outer' \
            or self.license_file.endswith('license.lic'), \
            'Invalid license file'

    def _dump(self, filename):
        with open(filename, 'w') as f:
            json_dump(self, f, indent=2)

    def _load(self, filename):
        with open(filename, 'r') as f:
            obj = json_load(f)
        self.update(obj)
        self._check(os.path.dirname(filename))

    def _project_filename(self, path):
        return path if path and os.path.isfile(path) else \
            os.path.join(path, config_filename)

    def open(self, path):
        filename = self._project_filename(path)
        self._path = os.path.abspath(os.path.dirname(filename))
        self._load(filename)

    def save(self, path):
        filename = self._project_filename(path)
        self._dump(filename)

    def check(self):
        self._check(self._path)

    @classmethod
    def map_obfuscate_mode(cls, mode, comode):
        m = Project.OBF_MODULE_MODE.index(mode)
        c = Project.OBF_CODE_MODE.index(comode)
        if comode == 'wrap':
            return 13 + m
        else:
            return 7 + (1 - m) * 3 + c

    def get_obfuscate_mode(self, mode=None, comode=None):
        if mode is None:
            mode = self.obf_module_mode
        if comode is None:
            comode = self.obf_code_mode
        return Project.map_obfuscate_mode(mode, comode)

    def get_build_files(self, force=False, excludes=[]):
        mlist = self.manifest.split(',') + excludes
        files = self.build_manifest(mlist, self.src)

        if force:
            return files

        results = []
        buildtime = self.get('build_time', 1.)
        for x in files:
            if os.path.getmtime(os.path.join(self.src, x)) > buildtime:
                results.append(x)
        return results

    @classmethod
    def build_manifest(cls, manifest, path=None):
        infile = StringIO()
        infile.write('\n'.join(manifest))
        infile.seek(0)
        template = TextFile(file=infile,
                            strip_comments=1,
                            skip_blanks=1,
                            join_lines=1,
                            lstrip_ws=1,
                            rstrip_ws=1,
                            collapse_join=1)
        lines = template.readlines()

        filelist = FileList()
        try:
            if path is not None and not path == os.getcwd():
                oldpath = os.getcwd()
                os.chdir(path)
            else:
                oldpath = None

            for line in lines:
                filelist.process_template_line(line)
        finally:
            if oldpath is not None:
                os.chdir(oldpath)
        return set(filelist.files)

    @classmethod
    def build_globfiles(cls, patterns, path=''):
        files = []
        n = len(path) + 1
        for x in patterns:
            for name in glob(os.path.join(path, x)):
                files.append(name[n:])
        return set(files)

    def info(self):
        lines = []
        for k, v in Project.DEFAULT_VALUE:
            if k == 'build_time':
                v = time.asctime(time.gmtime(self[k]))
            else:
                v = str(self[k])
                n = 50
                if len(v) > n:
                    v = v[:n] + '\n%24s' % ' ' + v[n:]
            lines.append('%22s: %s' % (k, v))
        return '\n'.join(lines)


if __name__ == '__main__':
    project = Project()
