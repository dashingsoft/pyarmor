# Upload dist\pyarmor-%1.tar.bz2 to pypi
# Not it need run on window command window
# C:\Python34\Scripts\twine upload dist\pyarmor-%1.tar.bz2

# Build wheel
# C:/Python34/python setup.py --bdist_wheel \
#      --plat-name=win32 --python-tag=py2.py3

# Build source
python setup.py sdist --formats=zip,bztar,gztar
rm -rf *.pyc __pycache__ *.pyo
