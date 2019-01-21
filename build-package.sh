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

clear_platform_files()
{
    echo Remove platforms files
    rm -rf src/platforms/windows32 src/platforms/windows64
    rm -rf src/platforms/linux32 src/platforms/linux64
    rm -rf src/platforms/darwin64
}

make_platform_files()
{
    (cd src/platforms;
        cp -a win32 windows32;
        cp -a win_amd64 windows64;
        cp -a linux_i386 linux32;
        cp -a linux_x86_64 linux64;
        cp -a macosx_x86_64 darwin64;
        cp -a armv7 linux32/arm;
        cp -a armv8.64-bit linux64/arm;
    )
}

# Build source, DEPRECATED WAY
# (cd src &&
# python setup.py sdist --formats=zip,bztar,gztar &&
# rm -rf *.pyc __pycache__ *.pyo)

if ! [[ "$1" == "whl" ]] ; then
    make_platform_files
fi

# Build source
$PYTHON setup.py sdist --formats=zip,bztar,gztar
clear_build

# Build universal wheel
$PYTHON setup.py bdist_wheel --universal
clear_build
clear_platform_files

[[ "$1" == "whl" ]] || exit 0

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
