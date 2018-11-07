PYTHON=C:/Python27/python.exe
PYARMOR=./pyarmor.bat

# Create a project
$PYTHON pyarmor.py init --src=examples/py2exe --entry="hello.py" projects/py2exe

# Enter project path
cd projects/py2exe

# Change project settings
#
# Set `runtime-path` to empty string, let obfuscated scripts search dynamic library
# in the same path of `hello.exe`
#
# Exclude useless script `setup.py`
#
$PYARMOR config --runtime-path='' --disable-restrict-mode=1 --manifest "include queens.py"

# Obfuscate all the scripts in project, no runtime files generated
$PYARMOR build --no-runtime

# Move entry script and pytransform.py to python source path
cp ../../examples/py2exe/hello.py hello.py.bak
cp ../../pytransform.py ../../examples/py2exe
mv dist/hello.py ../../examples/py2exe

# Run py2exe, generate `hello.exe`, `library.zip` in the path `dist`
( cd ../../examples/py2exe; $PYTHON setup.py py2exe )

# Compile all obfuscated scripts because `library.zip` includes `.pyc` files other than `.py`
$PYTHON -m compileall dist

# Update `library.zip`, replace original scripts with obfuscated scripts
( cd dist; zip -r ../../../examples/py2exe/dist/library.zip *.pyc )

# Restore hello.py
mv hello.py.bak ../../examples/py2exe/hello.py

# Generate runtime files only, save in other path `runtimes`
$PYARMOR build --only-runtime --output runtimes
rm runtimes/pytransform.py
cp runtimes/* ../../examples/py2exe/dist

# Now run `hello.exe`
cd ../../examples/py2exe/dist
./hello.exe
