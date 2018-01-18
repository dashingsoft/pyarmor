#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2018 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      pyarmor                                              #
#                                                           #
#      Version: 4.0.1 -                                     #
#                                                           #
#############################################################
#
#
#  @File: utils.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2018/01/17
#
#  @Description:
#
#   A tool used to import or un encrypted python scripts.
#
from distutils.filelist import FileList
from distutils.text_file import TextFile
import fnmatch
import glob
import logging
import os
import shutil
import sys
import tempfile
import time
from zipfile import ZipFile

def _import_pytransform():
    try:
        m = __import__('pytransform')
        return m
    except Exception:
        pass
    logging.info('Searching pytransform library ...')
    path = sys.rootdir
    platname = platform.replace('i586', 'i386').replace('i686', 'i386')
    src = os.path.join(path, 'platforms', platname, dll_name + dll_ext)
    if os.path.exists(src):
        logging.info('Find pytransform library "%s"', src)
        logging.info('Copy %s to %s', src, path)
        shutil.copy(src, path)
        m = __import__('pytransform')
        logging.info('Load pytransform OK.')
        return m
    logging.error('No library %s found', src)

def make_config(filename='project.json'):
    pass

def make_capsule(filename='project.zip'):    
    rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    logging.info('Rootdir is %s', rootdir)
    filelist = 'public.key', 'pytransform.py'
    for x in filelist:
        src = os.path.join(rootdir, x)
        if not os.path.exists(src):
            raise RuntimeError('No %s found in the rootdir' % src)

    licfile = os.path.join(rootdir, 'license.lic')
    if not os.path.exists(licfile):
        raise RuntimeError('Missing license file %s' % licfile)

    logging.info('Generating project key ...')
    pri, pubx, capkey, lic = pytransform.generate_project_capsule(licfile)
    logging.info('Generating project OK.')
    logging.info('Writing capsule to %s ...', filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(rootdir, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', capkey)
        myzip.write(os.path.join(rootdir, 'pytransform.py'), 'pytransform.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('license.lic', lic)
    finally:
        myzip.close()
    logging.info('Write project capsule OK.')

