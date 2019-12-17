#! /bin/sh
#
# Build source and wheel distribute
#

PLATFORMS="win32 win_amd64 manylinux1_x86_64 macosx_10_11_x86_64 macosx_10_11_intel"

PYTHON=C:/Python34/python
test -x $PYTHON || PYTHON=/usr/local/bin/python3
test -x $PYTHON || PYTHON=python
echo "PYTHON is $PYTHON"

clear_build()
{
    echo Remove build files: pyarmor.egg-info build src/__pycache__
    rm -rf pyarmor.egg-info build src/__pycache__ src/*.pyc
}

clear_platform_files()
{
    echo Remove platforms files
    rm -rf src/platforms/windows
    rm -rf src/platforms/linux
    rm -rf src/platforms/darwin
}

make_platform_files()
{
    src=../pyarmor-core/platforms
    dst=src/platforms
    mkdir -p ${dst} ${dst}/windows ${dst}/linux ${dst}/darwin
    cp ${src}/index.json ${dst}/
    cp -a ${src}/win32 ${dst}/windows/x86;
    cp -a ${src}/win_amd64 ${dst}/windows/x86_64;
    cp -a ${src}/linux_i386 ${dst}/linux/x86;
    cp -a ${src}/linux_x86_64 ${dst}/linux/x86_64;
    cp -a ${src}/macosx_x86_64 ${dst}/darwin/x86_64;
}

# Make platform files
make_platform_files

# Build source
$PYTHON setup.py sdist --formats=zip,bztar,gztar
clear_build

# Build universal wheel
$PYTHON setup.py bdist_wheel --universal
clear_build

clear_platform_files

# Build binary wheel
# for plat in $PLATFORMS ; do
#     name=$plat
#     [[ "$plat" == "manylinux1_x86_64" ]] && name="linux_x86_64"
#     [[ "$plat" == "macosx_10_11_intel" ]] && name="macosx_x86_64"
#     [[ "$plat" == "macosx_10_11_x86_64" ]] && name="macosx_x86_64"
#     cp src/platforms/$name/_pytransform.* src/
#
#     $PYTHON setup.py bdist_wheel --python-tag=py2.py3 --plat-name=$plat
#     clear_build
#     rm -rf src/_pytransform.*
# done
