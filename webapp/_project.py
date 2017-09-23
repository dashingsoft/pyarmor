from __future__ import print_function

import logging
import json
import os
import shutil
import sys
from zipfile import ZipFile

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
        'path': '',
        'scripts': [],
        'files': ['include *.py'],
        'licenses': [],
        'output': '',
        'clean': 0,
        'capsule': '',
        'target': '',
        'default_license': '',
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
    data['title'] = 'Project %d' % counter
    data['path'] = os.path.abspath(os.getcwd())
    data['capsule'] = capsule
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
    >>> p['scripts'] = ''
    >>> p['files'] = 'include *.py'
    >>> p['path'] = ''
    >>> p['output'] = os.path.join('projects', 'build')
    >>> buildProject(p)
    'Encrypt project OK.'

    >>> a = newLicense(p)
    >>> p['default_license'] = a['filename']
    >>> buildProject(p)
    'Encrypt project OK.'
    '''
    name = args['name']
    path = args['path'].strip()
    output = args['output'].strip()
    scripts = args['scripts'].split()
    files = args['files'].splitlines()
    capsule = args['capsule']
    target = args['target'].strip()
    default_license = args.get('default_license', None)

    if path == '':
        path = os.getcwd()
    if output == '':
        output = path
    argv = ['-O', output, '-s', path, '-C', capsule]
    if target:
        argv.extend(['-p', target])
    for wrapper in scripts:
        argv.extend(['-m', wrapper])

    manifest = os.path.join(project_data_path, name, 'MANIFEST');
    argv.extend(['--manifest', manifest])

    template = os.path.join(project_data_path, name, 'MANIFEST.in')
    with open(template, 'w') as fp:
        fp.write('\n'.join(files))
    argv.append('@' + template)

    do_encrypt(argv)

    if not default_license == '':
        licfile = os.path.join(output, 'license.lic')
        logging.info('Copy %s to %s', default_license, licfile)
        shutil.copyfile(default_license, licfile)

    if args['clean'] == 1:
        with open(manifest) as f:
            filelist = f.read().splitlines()
        backup = os.path.join(project_data_path, name, 'backup.zip')
        myzip = ZipFile(backup, 'w')
        logging.info('Backup source files to %s', backup)
        try:
            for filename in filelist:
                myzip.write(filename)
        finally:
            myzip.close()
        for filename in filelist:
            logging.info('Remove source file %s', filename)
            os.remove(filename)

    return 'Encrypt project OK.'

def removeProject(args):
    '''
    >>> p1 = newProject()['project']
    >>> m = removeProject(p1)
    >>> m == 'Remove project %s OK' % p1['name']
    True
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
    return 'Remove project %s OK' % name

def queryProject(args=None):
    '''
    >>> r = queryProject()
    >>> len(r) > 1
    True
    '''
    if args is not None and args.get('name') is not None:
        name = args.get('name')
        config = os.path.join(project_data_path, name, project_config_name)
        with open(config, 'r') as fp:
            data = json.load(fp)
        return dict(project=data, message='Got project %s' % name)

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
    >>> r = queryVersion()
    >>> r['version'][0] == '3'
    True
    >>> r['rcode'] == ''
    True
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
        argv.extend(['-B', value])
        title += 'Bind to %s.' % value
    except KeyError:
        pass

    try:
        value = args.pop('expired')
        argv.extend(['-e', value])
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
    >>> m == 'Remove license "Code: my-customer-a" OK.'
    True
    '''
    name = args['name']
    config = os.path.join(project_data_path, name, project_config_name)
    with open(config, 'r') as fp:
        data = json.load(fp)

    licenses = data['licenses']
    index = args.get('index')
    if index is None:
        filename = args['filename']
        for index in range(len(licenses)):
            if licenses[index]['filename'] == filename:
                break
        else:
            raise RuntimeError('No license %s found', filename)
    lic = licenses.pop(index)

    with open(config, 'w') as fp:
        json.dump(data, fp)

    title = lic['title'];
    filename = lic['filename'];
    os.remove(filename)

    return 'Remove license "%s" OK.' % title

if __name__ == '__main__':
    import doctest
    doctest.testmod()
