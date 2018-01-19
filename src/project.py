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
#      Version: 3.3.0 -                                     #
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
import os
from distutils.filelist import FileList
from distutils.text_file import TextFile
from io import StringIO
from json import dump as json_dump, load as json_load

class Project(dict):

    VERSION = 1, 0, 0

    OBF_MODULE_MODE = 'none', 'des'

    OBF_CODE_MODE = 'none', 'des', 'fast'

    DEFAULT_VALUE = {
        'version': '.'.join([str(x) for x in VERSION]),
        'name': None,
        'title': None,
        'description': None,
        'src': None,
        'manifest': 'global-include *.py',
        'entry': None,
        'output': 'build',
        'capsule': 'project.zip',
        'obf_module_mode': 'des',
        'obf_code_mode': 'des',
        'licenses': [],
        'targets': [],
    }

    def __init__(self, *args, **kwargs):
        for k, v in Project.DEFAULT_VALUE.items():
            kwargs.setdefault(k, v)
        super(Project, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)

    def dump(self, filename):
        with open(filename, 'w') as f:
            json_dump(self, f, indent=2)

    def load(self, filename):
        with open(filename, 'r') as f:
            obj = json_load(f)
        self._check(obj)
        self.update(obj)

    def get_target(self, name):
        if name == '' or name is None:
            return None, None
        t = self.targets[name]
        c = t.get('license')
        return t.get('platform'), None if c is None else self.get_license(c)

    def get_license(self, code):
        return self.licenses[code]['source']

    @classmethod
    def map_obfuscate_mode(cls, mode, comode):
        a = Project.OBF_CODE_MODE.index(mode)
        b = Project.OBF_MODULE_MODE.index(comode)
        return 7 + ( 1 - a ) * 3 + b

    def get_obfuscate_mode(self, mode=None, comode=None):
        if mode is None:
            mode = self.obf_module_mode
        if comode is None:
            comode = self.obf_code_mode
        return Project.map_obfuscate_mode(mode, comode)

    def get_build_files(self, force=False):
        s = self.manifest
        if self.entry:
            s = s + ',include ' + self.entry.replace(',', ' ')
        filelist = self.build_manifest(s, self.src)

        if force:
            return filelist

        results = []
        buildtime = self.get('build_time', 1.)
        for x in filelist:
            if os.path.getmtime(os.path.join(self.src, x)) > buildtime:
                results.append(x)
        return results
        
    def build_manifest(self, manifest, path=None):
        infile = StringIO()
        infile.write('\n'.join(manifest.split(',')))
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
        return filelist.files

    def add_license(self, code, title, source):
        self.licenses[code] = dict(title=title, source=source)

    def remove_license(self, code, path=''):
        if code in self.licenses:
            lic = self.licenses.pop(code)

            licfile = lic['source']
            if not os.path.isabs(licfile):
                licfile = os.path.join(path, licfile)
            os.remove(licfile)

            try:
                os.rmdir(os.path.dirname(licfile))
            except OSError:
                pass

    def add_target(self, name, platform=None, licode=None):
        self.targets[name] = dict(platform=platform, license=licode)

    def remove_target(self, name):
        self.targets.pop(name)

    def _update(self, kwargs):
        result = []
        for name in Project.DEFAULT_VALUE.keys():
            value = kwargs.get(name)
            if value is not None:
                self[name] = value
                result.append(name)
        return result

    def _check(self, project=None):
        if project is None:
            project = self

if __name__ == '__main__':
    project = Project()
