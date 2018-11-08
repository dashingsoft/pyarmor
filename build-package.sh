#! /bin/sh
#
# Build source and wheel distribute
#

PLATFORMS="win32 win_amd64 manylinux1_x86_64 macosx_10_11_x86_64 macosx_10_11_intel"

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
    name=$plat
    [[ "$plat" == "manylinux1_x86_64" ]] && name="linux_x86_64"
    [[ "$plat" == "macosx_10_11_intel" ]] && name="macosx_x86_64"
    [[ "$plat" == "macosx_10_11_x86_64" ]] && name="macosx_x86_64"
    cp src/platforms/$name/_pytransform.* src/

    $PYTHON setup.py bdist_wheel --python-tag=py2.py3 --plat-name=$plat
    clear_build
    rm -rf src/_pytransform.*
done
