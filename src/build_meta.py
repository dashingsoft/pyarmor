"""A PEP 517 interface to building pyarmored wheel based on setuptools

Here is an example package

    mypkg/
        pyproject.toml
        setup.py
        src/
            __init__.py
            ...

The content of minimum build file "pyproject.toml"

    [build-system]
    requires = ["setuptools", "wheel", "pyarmor>=7.2.0"]
    build-backend = "pyarmor.build_meta"

Now build a pyarmored wheel by pip

    cd mypkg/
    pip wheel .


Again, this is not a formal definition! Just a "taste" of the module.
"""

import os
import shutil
import sys

from wheel.wheelfile import WheelFile
from wheel.cli.pack import pack as wheel_pack
from pyarmor.pyarmor import main as pyarmor_main

from setuptools.build_meta import build_wheel as setuptools_build_wheel

try:
    from distutils.util import get_platform
except ModuleNotFoundError:
    from polyfills import get_platform


def _wheel_unpack(path, dest='.'):
    with WheelFile(path) as wf:
        namever = wf.parsed_filename.group('namever')
        destination = os.path.join(dest, namever)
        sys.stdout.flush()
        wf.extractall(destination)
    return namever


def _wheel_append_runtime_files(build_path, namever, pkgname):
    namelist = []
    for name in os.listdir(os.path.join(build_path, pkgname)):
        if name.startswith('pytransform'):
            path = os.path.join(build_path, pkgname, name)
            n = len(path) + 1
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    prefix = root[n:].replace('\\', '/')
                    for x in files:
                        namelist.append(prefix + '/' + x)
            else:
                namelist.append(name)

    wheel_record = os.path.join(build_path, namever + '.dist-info', 'RECORD')
    with open(wheel_record, 'a') as f:
        for name in namelist:
            f.write(pkgname + '/' + name + ',,\n')


def _fix_config(config_settings, obf_options):
    from pip._internal.configuration import Configuration, ConfigurationError
    config = Configuration(False)
    config.load()
    for k, v in reversed(config.items()):
        if k in ('pyarmor.advanced', ':env:.pyarmor-advanced'):
            if v not in ('2', '3', '4', '5'):
                raise ConfigurationError('Invalid pyarmor.advanced')
            obf_options.extend(['--advanced', v])
            break

    config_settings = config_settings or {}
    global_options = config_settings.get('--global-option', [])

    plat_name = get_platform().replace('-', '_').replace('.', '_')
    global_options.append('--plat-name=%s' % plat_name)

    global_options.append('--python-tag=cp%s%s' % sys.version_info[:2])
    # global_options.append('--py-limited-api=cp%s%s' % sys.version_info[:2])

    config_settings['--global-option'] = global_options
    return config_settings


def build_wheel(wheel_directory, config_settings=None,
                metadata_directory=None):
    obf_options = ['obfuscate', '--enable-suffix', '--in-place',
                   '-r', '--bootstrap', '3']
    config_settings = _fix_config(config_settings, obf_options)

    # Build wheel by setuptools
    result_basename = setuptools_build_wheel(
        wheel_directory,
        config_settings=config_settings,
        metadata_directory=metadata_directory
    )

    # Unpack wheel and replace the original .py with obfuscated ones
    result_wheel = os.path.join(wheel_directory, result_basename)
    namever = _wheel_unpack(result_wheel, wheel_directory)

    pkgname = namever.split('-')[0]
    build_path = os.path.join(wheel_directory, namever)

    obf_options.append(os.path.join(build_path, pkgname, '__init__.py'))
    pyarmor_main(obf_options)

    # Append runtime files of obfuscated scripts to wheel
    _wheel_append_runtime_files(build_path, namever, pkgname)

    # Pack the patched wheel again
    wheel_pack(build_path, wheel_directory, None)

    shutil.rmtree(build_path)
    return result_basename
