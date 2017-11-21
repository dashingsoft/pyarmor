# How to Obfuscate Python Script by Pyarmor

From Pyarmor 3.2.0, a new mode is introduced. By this way, no import
hooker, no setprofile, no settrace. The performance of running or
importing obfuscation python script has been remarkably improved. 

## Obfuscate Python Scripts

- At first, compile python source file to code objects
  
- Iterate code object, wrap bytecode of each code object as the
  following format
  
```
    0   JUMP_ABSOLUTE            n = 3 + len(bytecode)
    
    3
    ...
    ... Here it's obfuscated bytecode
    ...
    
    n   LOAD_GLOBAL              ? (__pyarmor__)
    n+3 CALL_FUNCTION            0
    n+6 POP_TOP
    n+7 JUMP_ABSOLUTE            0

```
- Save obfuscated code objects as .pyc or .pyo, so it can be run or
  imported by common Python interpreter.

## Run or Import Obfuscated Python Scripts

Those obfuscated file (.pyc or .pyo) can be run and imported as normal
way by common python interpreter. But when those code object is called
first time, from the wrapped bytecode descripted in above section, we
know

- First op is JUMP_ABSOLUTE, it will jump to offset n

- At offset n, the instruction is to call a PyCFunction. This function
  will restore those obfuscated bytecode between offset 3 and n, and
  place the original bytecode at offset 0
  
- After function call, the last instruction is to jump to
  offset 0. The really bytecode now is executed.

## Performance Analaysis

With default configuration, Pyarmor will do the following extra work
to run or import obfuscated bytecode:

- Load library _pytransform at startup
- Initialize library _pytransform at startup
- Veirfy license at startup
- Restore obfuscated bytecode when code object is called first time

There is a script "benchmark.py" in the package of Pyarmor used to
check performance. First run it to prepare test data

```
python benchmark.py
  
```

It will create directory "test-bench", change to this directory, and
run benchmark.py again. In my laptop, the output is

```
cd test-bench
python benchmark.py

load_pytransform: 1.65887005192 ms
init_pytransform: 1.31916207227 ms
verify_license: 0.771047716958 ms

Test script: bfoo.py
Obfuscated script: obfoo.pyc

run_empty_no_obfuscated_code_object: 0.00446984183744 ms
run_empty_obfuscated_code_object: 0.0430222276854 ms

run_one_thousand_no_obfuscated_bytecode: 0.0041904767226 ms
run_one_thousand_obfuscated_bytecode: 0.120126999381 ms

run_ten_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
run_ten_thousand_obfuscated_bytecode: 0.72551120324 ms

```

Here it's a normal license checked by verify_license. If the license
is bind to fixed machine, for example, mac address, it need more time
to read hardware information.

The bytecode size of function one_thousand is about 1K, and
ten_thousand is about 10K. Most of them will not be executed, because
they're in False condition for ever. So run_empty, run_one_thousand,
run_ten_thousand are almost same in non-obfuscated mode, about 0.004
ms.

In obfuscated mode, it's about 0.1 ms for 1K bytecoe, and 0.7~0.8 ms
for 10K bytecode in my laptop. It's mainly consumed by restoring
obfuscated bytecodes.

If you really care about performance, there is another option which
could reduce the elapsed time here.


```
# First change to src path of pyarmor
cd ..

# Edit pytransform.py
vi pytransform.py

# Uncomment line 187

    # m.set_option('disable_obfmode_encrypt'.encode(), c_char_p(1))

# Change to

    m.set_option('disable_obfmode_encrypt'.encode(), c_char_p(1))
    
```

By default, bytecode will be encrypted by DES algorithm. If it's
disabled, another simple algorithm is applied. Now run "benchmark.py"
to prepare new test data

```
python benchmark.py
  
```

It will update test files in output path "test-bench", change to this
directory, run "benchmark.py" again. In my laptop, the output is


```
cd test-bench
python benchmark.py

load_pytransform: 1.78905419544 ms
init_pytransform: 1.32139699319 ms
verify_license: 0.759314382135 ms

Test script: bfoo.py
Obfuscated script: obfoo.pyc

run_empty_no_obfuscated_code_object: 0.00502857206712 ms
run_empty_obfuscated_code_object: 0.00474920695228 ms

run_one_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
run_one_thousand_obfuscated_bytecode: 0.00642539764132 ms

run_ten_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
run_ten_thousand_obfuscated_bytecode: 0.0287746068285 ms

```

# DEPRECATED Mode

The following modes are used by Pyarmor before v3.2.0. It requires
import hooker, for example, sys.meta_path, and sys.setprofile or
sys.settrace. Especially the latter, it could dramatically effect
performance.

## Mode 0

### Py_Source

**Encrypt**

- Compile source to Code Object
- Encrypt bytecode of each Code Object
- Encrypt Code Object
- Write to file with ".pye"

**Decrypt**

Add import hooker to sys.meta_path, when an encrypted module found:

- Decrypt source file
- Add hook by sys.setprofile
- Before each code object is called, profile hook will decrypt byte-code
- After code object is to be return, profile hokk will encrypt byte-code again

### Py_Compiled

**Encrypt**

- Read compiled file to Code Object
- Encrypt bytecode of each Code Object
- Encrypt Code Object
- Write to file with ".pye"

**Decrypt**

Add import hooker to sys.meta_path, when an encrypted module found:

- Decrypt source file
- Add hook by sys.setprofile
- Before each code object is called, profile hook will decrypt byte-code
- After code object is to be return, profile hokk will encrypt byte-code again

## Mode 1

### Py_Source

**Encrypt**

- Compile source to Code Object
- Encrypt bytecode of each Code Object
- **DO NOT** Encrypt Code Object
- Write to file with ".pyc"

**Decrypt**

- Import compiled file as normal
- Add hook by sys.setprofile
- Before each code object is called, profile hook will decrypt byte-code
- After code object is to be return, profile hokk will encrypt byte-code again

**No extra import hooker needed**

### Py_Compiled

**Encrypt**

- Read compiled file to Code Object
- Encrypt bytecode of each Code Object
- **DO NOT** encrypt Code Object
- Write to file with ".pyc" or ".pyo"

**Decrypt**

- Import compiled file as normal
- Add hook by sys.setprofile
- Before each code object is called, profile hook will decrypt byte-code
- After code object is to be return, profile hokk will encrypt byte-code again

**No extra import hooker needed**

## Mode 2

### Py_Source

**Encrypt**

- Compile source to Code Object
- **DO NOT** Encrypt bytecode of each Code Object
- Encrypt Code Object
- Write to file with ".pye"

**Decrypt**

Add import hooker to sys.meta_path, when an encrypted module found:

- Decrypt source file
- Import decrypted script as normal

**No sys.setprofile needed**

### Py_Compiled

**Encrypt**

- Read compiled file to Code Object
- **DO NOT** encrypt bytecode of each Code Object
- Encrypt Code Object
- Write to file with ".pyc" or ".pyo"

**Decrypt**

Add import hooker to sys.meta_path, when an encrypted module found:

- Decrypt compiled file
- Import compiled file as normal

**No sys.setprofile needed**

## Compare 3 modes

```
MODE             0                    1                    2

import hooker   NEED                 No                   Need
profile hooker  NEED                 Need                 No
performance     low                  high                 medium
security        high                 medium               low
```

## Limitations

### sys.meta_path

Used to hook importer, so that encrypted source file can be imported

### sys.setprofile/sys.settrace

Use any of one to decrypt byte-code in runtime

### threading.setprofile/threading.settrace

Use any of one to decrypt byte-code in runtime in other thread (not main thread)

### Py_TRACE_REFS or Py_DEBUG

If Py_TRACE_REFS or Py_DEBUG is defined, the size of_PyObject_HEAD_EXTRA will not be 0. In this case, f_code is not right and pytransform will not work.

### About package

**It works if package is only in one path**

```
    a/pkg/__init__.pye
         foo.pye
         hello.py

```

**If one package locates at different path, any of __init__.py CAN NOT
be encrypted**

It works if none of \__init__.py is encrypted
```
    a/pkg/__init__.py
         foo.pye
         hello.pye

    b/pkg/__init__.py
         foo2.pye
         hello2.py

```

It doesn't work if both of \__init__.py are encrypted
```
    a/pkg/__init__.pye
         foo.pye
         hello.py

    b/pkg/__init__.pye
         foo2.py
         hello2.py

```

It doesn't work if any of \__init__.py is encrypted
```
    a/pkg/__init__.pye
         foo.pye
         hello.py

    b/pkg/__init__.py
         foo2.py
         hello2.py

```
