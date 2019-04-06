#! /bin/sh
#
# Build wheel distribute for pyarmor-core
#

PYTHON=C:/Python34/python
test -f $PYTHON || PYTHON=python

get_platforms()
{
    $PYTHON -c 'from src.config import support_platforms; print(" ".join([x for x, _ in support_platforms[0]]), end="")'
}


for plat in $(get_platforms) ; do
    echo "Build wheel for $plat ..."
    $PYTHON setup-core.py bdist_wheel --python-tag=py2.py3 --plat-name=$plat >build.log 2>&1 || exit 1
    rm -rf pyarmor_core.egg-info build build.log __pycache__ src/__pycache__
    echo "Build OK."
done
