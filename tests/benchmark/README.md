# Benchmark Test of Pyarmor

Test script

``` bash

$PYTHON pybench.py -f ${result_base}

$PYTHON pyarmor.py encrypt -C project.zip -O ${output} -e ${mode} --in-place ${output}/*.py ${output}/package/*.py
find ${output}/ -name "*.py" -delete

cd ${output}

cat <<EOF > main.py
import pyimcore
from pytransfrom import exec_file
exec_file('pybench.pye')
EOF

$PYTHON main.py -v -f ${result_mode}
$PYTHON main.py -s ${result_base} -c ${result_mode} > ${result_file}

```
