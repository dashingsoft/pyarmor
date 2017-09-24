build=__build__
mkdir -p $build
rm -rf $build/pyarmor
rm -f pyarmor-webapp.zip
mkdir -p $build/pyarmor/webapp/projects
mkdir $build/pyarmor/src

src=../src
target=$build/pyarmor/webapp

cp *.py *.html *.js *.md $target
cp -a js css images $target
cp start-server.* $target
cp $src/*.py $src/*.key $src/*.lic $src/*.md $src/*.html $target/$src
cp -a $src/platforms $target/$src
cp -a $src/examples $target/$src
rm $target/$src/setup.py

cp ../ChangeLog.rst ../README.* $target/..

(cd $build && zip -r ../pyarmor-webapp ./)

rm -rf $build
