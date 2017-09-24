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

* Comapre both of results and write to **{compare_result}**

> $PYTHON main.py -s ${result_base} -c ${mode_result} > ${comapre_result}

## Test Results

The following results are got by running script [benchmark-test.sh](../benchmark-test.sh) in different platfrom.

### linxu_x86_64

### win_amd64

* [py26.base-mode0.bench](https://github.com/dashingsoft/pyarmor/blob/benchmark/tests/benchmark/linux_x86_64/py26.base-mode0.bench)

### win32

### linux_i386

Pybench is not stable in my ubuntu 32 virtual box, even if no encrypted. so there is no full results in this platfrom.


## Analysis and Conclusion

TryFinally
SecondSubmoduleImport after Python33
