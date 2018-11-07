#! /bin/sh
#
# Build source and wheel distribute
#

PLATFORMS="win32 win_amd64 linux_x86_64 linux_i386 macosx_x86_64"

PYTHON=C:/Python34/python
test -f $PYTHON || PYTHON=python

clear_build()
{
    echo Remove build files: pyarmor.egg-info build src/__pycache__
    rm -rf pyarmor.egg-info build src/__pycache__
}

# Build source, DEPRECATED WAY
# (cd src &&
# python setup.py sdist --formats=zip,bztar,gztar &&
# rm -rf *.pyc __pycache__ *.pyo)

# Build source
$PYTHON setup.py sdist --formats=zip,bztar,gztar
clear_build

# Build universal wheel
$PYTHON setup.py bdist_wheel --universal
clear_build

# Build binary wheel
for plat in $PLATFORMS ; do
    cp src/platforms/$plat/_pytransform.* src/
    $PYTHON setup.py bdist_wheel --python-tag=py2.py3 --plat-name=$plat
    clear_build
    rm -rf src/_pytransform.*
done
