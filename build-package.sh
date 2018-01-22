# Build wheel
# C:/Python34/python setup.py --bdist_wheel \
#      --plat-name=win32 --python-tag=py2.py3

# Build source
(cd src &&
python setup.py sdist --formats=zip,bztar,gztar &&
rm -rf *.pyc __pycache__ *.pyo)
