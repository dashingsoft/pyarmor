from __future__ import print_function

import logging
import json
import os
import shutil
import sys

project_data_path = 'projects'
project_capsule_name = 'capsule'
project_config_name = 'config.json'
project_index_name = 'index.json'

path = os.path.dirname(os.path.abspath(sys.argv[0]))
rootdir = os.path.normpath(os.path.join(path, '..', 'src'))
sys.rootdir = rootdir
sys.path.append(rootdir)

from config import version
from pyarmor import (_get_registration_code, _import_pytransform,
                     do_capsule, do_encrypt, do_license)
import pyarmor
pyarmor.pytransform = _import_pytransform()

def _check_project_index():
    filename = os.path.join(project_data_path, project_index_name)
    if not os.path.exists(filename):
        with open(filename, 'w') as fp:
            json.dump(dict(counter=0, projects={}), fp)
    return filename

def _create_default_project(name):
    '''
    >>> a = _create_default_project('a')
    >>> b = _create_default_project('b')
    >>> a['name']
    'a'
    >>> a['scripts'].append('a1')
    >>> a['scripts']
    ['a1']
    >>> b['name']
    'b'
    >>> b['scripts']
    []
    '''
    return {
        'name': name,
        'title': '',
        'description': '',
        'srcpath': '',
        'scripts': [],
        'files': [],
        'licenses': [],
        'output': '',
        'capsule': None,
        'target': None,
        'default_license': None,
    }

def newProject(args=None):
    '''
    >>> p = newProject()
    >>> p['message']
    'Project has been created'
    '''
    filename = _check_project_index()
    with open(filename, 'r') as fp:
        pindexes = json.load(fp)

    counter = pindexes['counter'] + 1
    name = 'project-%d' % counter
    path = os.path.join(project_data_path, name)
    if os.path.exists(path):
        logging.warning('Project path %s has been exists', path)
    else:
        logging.info('Make project path %s', path)
        os.mkdir(path)
    capsule = os.path.join(path, project_capsule_name + '.zip')
    if not os.path.exists(capsule):
        argv = ['-O', path, project_capsule_name]
        do_capsule(argv)

    data = _create_default_project(name)
    data['capsule'] = capsule
    data['output'] = os.path.join(path, 'dist')
    config = os.path.join(path, project_config_name)
    with open(config, 'w') as fp:
        json.dump(data, fp)

    pindexes['projects'][name] = config
    pindexes['counter'] = counter
    with open(filename, 'w') as fp:
        json.dump(pindexes, fp)

    return dict(project=data, message='Project has been created')

def updateProject(args):
    '''
    >>> p = newProject()['project']
    >>> p['title'] = 'MyProject'
    >>> updateProject(p)
    'Update project OK'
    '''
    name = args['name']
    config = os.path.join(project_data_path, name, project_config_name)
    with open(config, 'w') as fp:
        json.dump(args, fp)
    return 'Update project OK'

def buildProject(args):
    '''
    >>> p = newProject()['project']
    >>> p['title'] = 'My Project'
    >>> p['scripts'] = []
    >>> p['files'] = ['*.py']
    >>> p['srcpath'] = ''
    >>> buildProject(p)
    'Encrypt scripts OK.'

    >>> a = newLicense(p)
    >>> p['default_license'] = a['filename']
    >>> buildProject(p)
    'Encrypt scripts OK.'
    '''
    name = args['name']
    src = args['srcpath']
    output = args['output']
    scripts = args['scripts']
    files = args['files']
    capsule = args['capsule']
    target = args.get('target', None)
    default_license = args.get('default_license', None)

    if src.strip() == '':
        src = os.getcwd()
    argv = ['-O', output, '-s', src, '-C', capsule]
    for s in scripts:
        argv.append('-m')
        argv.append(os.path.splitext(os.path.basename(s))[0])
    argv.extend(scripts)
    argv.extend(files)

    do_encrypt(argv)

    if default_license is not None:
        shutil.copyfile(default_license, os.path.join(output, 'license.lic'))

    return 'Encrypt scripts OK.'

def removeProject(args):
    '''
    >>> p1 = newProject()['project']
    >>> removeProject(p1)
    'Remove project OK'
    '''
    filename = _check_project_index()
    with open(filename, 'r') as fp:
        pindexes = json.load(fp)

    name = args['name']
    try:
        pindexes['projects'].pop(name)
    except KeyError:
        pass
    with open(filename, 'w') as fp:
        json.dump(pindexes, fp)

    shutil.rmtree(os.path.join(project_data_path, name))
    return 'Remove project OK'

def queryProject(args=None):
    '''
    >>> r = queryProject()
    >>> len(r) > 1
    True
    '''
    filename = _check_project_index()
    with open(filename, 'r') as fp:
        pindexes = json.load(fp)

    result = []
    for name, filename in pindexes['projects'].items():
        try:
            with open(filename, 'r') as fp:
                data = json.load(fp)
                item = dict(name=name, title=data['title'])
        except Exception:
            item = dict(name=name, title='* Something is wrong with this project')
        result.append(item)
    return result

def queryVersion(args=None):
    '''
    >>> queryVersion()
    {'version': '3.1.3', 'rcode': ''}
    '''
    rcode = _get_registration_code()
    return dict(version=version, rcode=rcode)

def newLicense(args):
    '''
    >>> p = newProject()['project']
    >>> p['hdinfo'] = 'hdsioa-2abc'
    >>> a1 = newLicense(p)
    >>> p['expired'] = '2017-11-20'
    >>> a2 = newLicense(p)

    '''
    name = args['name']
    capsule = os.path.join(project_data_path, name, project_capsule_name + '.zip')
    for i in range(1024):
        output = os.path.join(project_data_path, name, 'license-%d.lic' % i)
        if not os.path.exists(output):
            break

    argv = ['-C', capsule, '-O', output]
    title = ''

    try:
        value = args.pop('hdinfo')
        argv.append('-B')
        argv.append(value)
        title += 'Bind to %s.' % value
    except KeyError:
        pass

    try:
        value = args.pop('expired')
        argv.append('-e')
        argv.append(value)
        title += 'Expired on %s.' % value
    except KeyError:
        pass

    try:
        value = args.pop('rcode')
        argv.append(value)
        title = 'Code: %s' % value
    except KeyError:
        pass

    if title == '':
        title = 'Default license'

    do_license(argv)

    config = os.path.join(project_data_path, name, project_config_name)
    with open(config, 'r') as fp:
        data = json.load(fp)

    with open(config, 'w') as fp:
        data['licenses'].append(dict(title=title, filename=output))
        json.dump(data, fp)

    return dict(title=title, filename=output)

def removeLicense(args):
    '''
    >>> p = newProject()['project']
    >>> p['rcode'] = 'my-customer-a'
    >>> a = newLicense(p)
    >>> a['name'] = p['name']
    >>> m = removeLicense(a)
    >>> m['message']
    'Remove license "Code: my-customer-a" OK.'
    '''
    name = args['name']
    title = args['title']
    filename = args['filename']

    os.remove(filename)

    config = os.path.join(project_data_path, name, project_config_name)
    with open(config, 'r') as fp:
        data = json.load(fp)

    licenses = data['licenses']
    for i in range(len(licenses)):
        if licenses[i]['filename'] == filename:
            licenses.pop(i)

    with open(config, 'w') as fp:
        json.dump(data, fp)

    return dict(index=i, message='Remove license "%s" OK.' % title)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
