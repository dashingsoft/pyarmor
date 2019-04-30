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
#
import os
import time
from distutils.filelist import FileList
from distutils.text_file import TextFile
from glob import glob
from io import StringIO
from json import dump as json_dump, load as json_load

from config import config_filename, capsule_filename, default_output_path, \
                   default_manifest_template, \
                   default_obf_module_mode, default_obf_code_mode


class Project(dict):

    VERSION = 1, 2, 0

    OBF_MODULE_MODE = 'none', 'des'

    OBF_CODE_MODE = 'none', 'des', 'fast', 'wrap'

    DEFAULT_VALUE = \
        ('version', '.'.join([str(x) for x in VERSION])), \
        ('name', None), \
        ('title', None), \
        ('src', None), \
        ('is_package', None), \
        ('manifest', default_manifest_template), \
        ('entry', None), \
        ('output', default_output_path), \
        ('capsule', capsule_filename), \
        ('runtime_path', None), \
        ('disable_restrict_mode', 0), \
        ('obf_module_mode', default_obf_module_mode), \
        ('obf_code_mode', default_obf_code_mode), \
        ('obf_code', 1), \
        ('obf_mod', 1), \
        ('wrap_mode', 1), \
        ('cross_protection', 1), \
        ('plugins', None), \
        ('platform', None), \
        ('build_time', 0.)

    def __init__(self, *args, **kwargs):
        for k, v in Project.DEFAULT_VALUE:
            kwargs.setdefault(k, v)
        super(Project, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
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
        pro_path = path if (path == '' or os.path.exists(path)) \
            else os.path.dirname(path)
        assert os.path.exists(os.path.normpath(pro_path)), \
            'Project path %s does not exists' % pro_path
        assert os.path.exists(self.src), \
            'The src of this project is not found: %s' % self.src
        assert os.path.isabs(self.src), \
            'The src of this project is not absolute path'
        assert self.src != os.path.abspath(self.output), \
            'The output path can not be same as src in the project'
        assert self.capsule.endswith('.zip'), \
            'Invalid capsule, not a zip file'

        capsule = self.capsule if os.path.isabs(self.capsule) \
            else os.path.join(pro_path, self.capsule)
        assert os.path.exists(os.path.normpath(capsule)), \
            'No project capsule found: %s' % capsule

    def _dump(self, filename):
        with open(filename, 'w') as f:
            json_dump(self, f, indent=2)

    def _load(self, filename):
        with open(filename, 'r') as f:
            obj = json_load(f)
        self.update(obj)
        self._check(os.path.dirname(filename))

    def _project_filename(self, path):
        if path == '' or os.path.exists(path):
            filename = os.path.join(path, config_filename)
        else:
            name = os.path.basename(path)
            filename = os.path.join(os.path.dirname(path),
                                    '%s.%s' % (config_filename, name))
        return filename

    def open(self, path):
        filename = self._project_filename(path)
        self._load(filename)

    def save(self, path):
        filename = self._project_filename(path)
        self._dump(filename)

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
