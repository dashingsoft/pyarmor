# Benchmark Test of Pyarmor

## Test Steps

* Run pybench to get base result, save to file **${base_result}**

> $PYTHON pybench.py -f ${base_result}

* Encrypted pybench in the path **${output}**

> $PYTHON pyarmor.py encrypt -C project.zip -O ${output} -e ${mode} --in-place ${output}/*.py ${output}/package/*.py

> Note that Pyarmor support 3 encrypt modes: 0, 1, 2. This command and next commands need execute 3 times.


* Remove original file

> find ${output}/ -name "*.py" -delete

* Generate startup script to run encrypted **pybench.pye**

``` bash
    cat <<EOF > main.py
    import pyimcore
    from pytransfrom import exec_file
    exec_file('pybench.pye')
    EOF
```

* Run encrypted pybench, save result to **${mode_result}**

> $PYTHON main.py -v -f ${mode_result}

* Comapre both of results and write final result to **{compare_result}**

> $PYTHON main.py -s ${base_result} -c ${mode_result} > ${comapre_result}

## Test Results

The following results are got by running script [benchmark-test.sh](../benchmark-test.sh) in different platfrom.

### linxu_x86_64

* [py26.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py26.base-mode0.bench)
* [py26.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py26.base-mode1.bench)
* [py26.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py26.base-mode2.bench)
* [py27.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py27.base-mode0.bench)
* [py27.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py27.base-mode1.bench)
* [py27.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py27.base-mode2.bench)
* [py32.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py32.base-mode0.bench)
* [py32.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py32.base-mode1.bench)
* [py32.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py32.base-mode2.bench)
* [py33.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py33.base-mode0.bench)
* [py33.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py33.base-mode1.bench)
* [py33.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py33.base-mode2.bench)
* [py34.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py34.base-mode0.bench)
* [py34.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py34.base-mode1.bench)
* [py34.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py34.base-mode2.bench)

### win_amd64

* [py26.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py26.base-mode0.bench)
* [py26.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py26.base-mode1.bench)
* [py26.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py26.base-mode2.bench)
* [py27.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py27.base-mode0.bench)
* [py27.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py27.base-mode1.bench)
* [py27.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py27.base-mode2.bench)
* [py32.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py32.base-mode0.bench)
* [py32.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py32.base-mode1.bench)
* [py32.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py32.base-mode2.bench)
* [py33.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py33.base-mode0.bench)
* [py33.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py33.base-mode1.bench)
* [py33.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py33.base-mode2.bench)
* [py34.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py34.base-mode0.bench)
* [py34.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py34.base-mode1.bench)
* [py34.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win_amd64/py34.base-mode2.bench)

### win32

* [py26.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py26.base-mode0.bench)
* [py26.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py26.base-mode1.bench)
* [py26.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py26.base-mode2.bench)
* [py27.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py27.base-mode0.bench)
* [py27.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py27.base-mode1.bench)
* [py27.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py27.base-mode2.bench)
* [py32.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py32.base-mode0.bench)
* [py32.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py32.base-mode1.bench)
* [py32.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py32.base-mode2.bench)
* [py33.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py33.base-mode0.bench)
* [py33.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py33.base-mode1.bench)
* [py33.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py33.base-mode2.bench)
* [py34.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py34.base-mode0.bench)
* [py34.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py34.base-mode1.bench)
* [py34.base-mode2.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/win32/py34.base-mode2.bench)

### linux_i386

Pybench is not stable in my ubuntu 32 virtual box, even if no encrypted. so there is no full results in this platfrom.

* [py27.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_i386/py27.base-mode0.bench)
* [py32.base-mode1.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_i386/py32.base-mode1.bench)


## Analysis and Conclusion

The following statements effect the performance significantly. 

* TryFinally
* SecondSubmoduleImport after Python33, especially in Linux_xi6_64

That's goal to minimize these effects in next version.
