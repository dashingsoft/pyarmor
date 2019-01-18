from __future__ import print_function

import logging
import json
import os
import shutil
import subprocess
import sys

from zipfile import ZipFile

# PyArmor in the parent path
PYARMOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.environ['PYARMOR_PATH'] = PYARMOR_PATH
sys.path.insert(0, PYARMOR_PATH)

from config import version, config_filename, capsule_filename
from project import Project

project_base_path = os.path.join(PYARMOR_PATH, 'projects')
project_index_name = 'index.json'
project_capsule_name = capsule_filename
project_config_name = config_filename

def call_armor(args):
    p = subprocess.Popen([sys.executable, 'pyarmor.py'] + list(args),
                         cwd=PYARMOR_PATH)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError('Call pyarmor failed, see the details in console window')

def _check_trial_license():
    filename = os.path.join(PYARMOR_PATH, 'license.lic')
    return os.path.getsize(filename) == 256

def _check_project_index():
    filename = os.path.join(project_base_path, project_index_name)
    if not os.path.exists(filename):
        if not os.path.exists(project_base_path):
            os.makedirs(project_base_path)
        with open(filename, 'w') as fp:
            json.dump(dict(counter=0, projects={}), fp)
    return filename

def _create_default_project(**kwargs):
    return Project(**kwargs)

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
    path = os.path.join(project_base_path, name)
    if os.path.exists(path):
        logging.warning('Project path %s has been exists', path)
    else:
        logging.info('Make project path %s', path)
        os.mkdir(path)

    args = ['init', '--src', path, path]
    call_pyarmor(args)

    pindexes['projects'][name] = os.path.abspath(path)
    pindexes['counter'] = counter
    with open(filename, 'w') as fp:
        json.dump(pindexes, fp)

    project = Project()
    project.open(path)

    project['name'] = name
    project['title'] = name
    project['output'] = 'dist'

    return dict(project=project, message='Project has been created')

def updateProject(args):
    '''
    >>> p = newProject()['project']
    >>> updateProject(title='My Project')
    'Update project OK'
    '''
    name = args['name']
    path = os.path.join(project_base_path, name)
    project = Project()
    project.open(path)

    if not args['output']:
        args['output'] = 'dist'

    project._update(args)
    project.save(path)

    return 'Update project OK'

def buildProject(args):
    '''
    >>> p = newProject()['project']
    >>> p['src'] = ''
    >>> p['output'] = os.path.join('projects', 'build')
    >>> buildProject(p)
    'Build project OK.'
    '''
    name = args['name']
    path = os.path.join(project_base_path, name)
    call_pyarmor(['build', path])
    return 'Build project OK.'

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

    shutil.rmtree(os.path.join(project_base_path, name))
    return 'Remove project %s OK' % name

def queryProject(args=None):
    '''
    >>> r = queryProject()
    >>> len(r) > 1
    True
    '''
    if args is not None and args.get('name') is not None:
        name = args.get('name')
        path = os.path.join(project_base_path, name)
        project = Project()
        project.open(path)
        return dict(project=project, message='Got project %s' % name)

    filename = _check_project_index()
    with open(filename, 'r') as fp:
        pindexes = json.load(fp)

    result = []
    for name, filename in pindexes['projects'].items():
        path = os.path.join(project_base_path, name)
        project = Project()
        project.open(path)
        item = dict(name=name, title=project['title'])
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
    rcode = '' if _check_trial_license() else 'PyArmor'
    return dict(version=version, rcode=rcode)

def newLicense(args):
    '''
    >>> p = newProject()['project']
    >>> p['rcode'] = 'Curstomer-Tom'
    >>> a1 = newLicense(p)
    >>> p['expired'] = '2017-11-20'
    >>> a2 = newLicense(p)

    '''
    name = args['name']
    path = os.path.join(project_base_path, name)
    title = args['rcode'].strip()

    params = ['licenses', '--project', path]
    for opt in ('expired', 'bind_disk', 'bind_ipv4', 'bind_mac'):
        if args[opt]:
            params.extend(['--%s' % opt.replace('_', '-'), args[opt]])
    params.append(title)
    call_pyarmor(params)

    output = os.path.join(path, 'licenses', title, 'license.lic')
    return dict(title=title, filename=output)

def obfuscateScripts(args):
    params = ['obfuscate']
    for opt in ['output']:
        if args[opt]:
            params.extend(['--%s' % opt, args[opt]])
    params.append(args['entry'])

    call_armor(params)

    output = args['output'] if args['output'] \
        else os.path.join(PYARMOR_PATH, 'dist')
    return dict(output=output)

def generateLicenses(args):
    params = ['licenses', '--output', PYARMOR_PATH]

    for opt in ('expired', 'bind_disk', 'bind_ipv4', 'bind_mac'):
        if args[opt]:
            params.extend(['--%s' % opt.replace('_', '-'), args[opt]])

    rcode = args['rcode'].strip()
    params.append(rcode)

    call_armor(params)

    return dict(output=os.path.join(
        PYARMOR_PATH, 'licenses', rcode, 'license.lic'))

def packObfuscatedScripts(args):
    params = ['pack', '--type', args['type'], args['entry']]
    if args['output']:
        params[3:3] = ['--output', args['output']]
    if args['setup']:
        params[3:3] = ['--setup', args['setup']]

    call_armor(params)

    return dict(output=output)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
