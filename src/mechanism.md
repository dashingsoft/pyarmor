# How to Obfuscate Python Script by Pyarmor

From Pyarmor 3.3, a new mode is introduced. By this way, no import
hooker, no setprofile, no settrace. The performance of running or
importing obfuscation python script has been remarkably improved.

## Mechanism

There are 2 ways to protect Python Scripts by Pyarmor:

* Obfuscate byte code of each code object
* Obfuscate whole code object of python module

### Obfuscate Python Scripts

- Compile python source file to code object

```
    char * filename = "xxx.py";
    char * source = read_file( filename );
    PyObject *co = Py_CompileString( source, filename, Py_file_input );
```

- Iterate code object, wrap bytecode of each code object as the
  following format

```
    0   JUMP_ABSOLUTE            n = 3 + len(bytecode)

    3
    ...
    ... Here it's obfuscated bytecode
    ...

    n   LOAD_GLOBAL              ? (__armor__)
    n+3 CALL_FUNCTION            0
    n+6 POP_TOP
    n+7 JUMP_ABSOLUTE            0

```

- Serialize code object and obfuscate it

```
    char *original_code = marshal.dumps( co );
    char *obfuscated_code = obfuscate_algorithm( original_code  );
```

- Create wrapper script "xxx.py", **${obfuscated_code}** stands for string constant generated in previous step.

```
    __pyarmor__(__name__, b'${obfuscated_code}')
```

### Run or Import Obfuscated Python Scripts

When import or run this wrapper script, the first statement is to call a CFunction:

```
    int __pyarmor__(char *name, unsigned char *obfuscated_code) {
      char *original_code = resotre_obfuscated_code( obfuscated_code );
      PyObject *co = marshal.loads( original_code );
      PyObject *mod = PyImport_ExecCodeModule( name, co );
    }
```

This function accepts 2 parameters: module name and obfuscated code, then

* Restore obfuscated code
* Create a code object by original code
* Import original module **(this will result in a duplicated frame in
  Traceback)**

#### Run or Import Obfuscated Bytecode

After module imported, when any code object in this module is called
first time, from the wrapped bytecode descripted in above section, we
know

- First op is JUMP_ABSOLUTE, it will jump to offset n

- At offset n, the instruction is to call a PyCFunction. This function
  will restore those obfuscated bytecode between offset 3 and n, and
  place the original bytecode at offset 0

- After function call, the last instruction is to jump to
  offset 0. The really bytecode now is executed.

## Implementation

From Pyarmor 3.4, use the following commands:

```
    # First create a project to manage obfuscated scripts
    python pyarmor.py init --src=/PATH/TO/SCRIPTS projects/myproject
    cd projects/myproject

    # Second, use command "config" to specify obfuscation mode:
    #
    #    --obf-module-mode 'des' is default. Obfuscate module by DES
    #                      'none' means no obfuscate module object.
    #
    #    --obf-code-mode   'des' is default.
    #                      'fast' is a simple algorithm faster than DES.
    #                      'none' means no obfuscate bytecode.
    #
    # For example (in windows, run ./pyarmor.bat other than ./pyarmor),
    ./pyarmor config --obf-module-mode des
                     --obf-code-mode none

    # Finally, obfuscate scripts as project configuration by command 'build'
    ./pyarmor build

```

## Performance Analaysis

With default configuration, Pyarmor will do the following extra work
to run or import obfuscated bytecode:

- Load library _pytransform at startup
- Initialize library _pytransform at startup
- Veirfy license at startup
- Restore obfuscated code object of python module
- Restore obfuscated bytecode when code object is called first time

There is command "benchmark" used to run benchmark test

```
    usage: pyarmor.py benchmark [-h] [--obf-module-mode {none,des}]
                                [--obf-code-mode {none,des,fast}]

    optional arguments:
      -h, --help            show this help message and exit
      -m, --obf-module-mode {none,des}
      -c, --obf-code-mode {none,des,fast}
```

For example, run test in default mode

```
    python pyarmor.py benchmark

    INFO     Start benchmark test ...
    INFO     Obfuscate module mode: des
    INFO     Obfuscate bytecode mode: des
    INFO     Benchmark bootstrap ...
    INFO     Benchmark bootstrap OK.
    INFO     Run benchmark test ...
    load_pytransform: 6.35248334635 ms
    init_pytransform: 3.85942906151 ms
    verify_license: 0.730260410192 ms

    Test script: bfoo.py
    Obfuscated script: obfoo.py
    Start test with mode 8
    --------------------------------------

    import_no_obfuscated_module: 10.3613727443 ms
    import_obfuscated_module: 8.09683912341 ms

    run_empty_no_obfuscated_code_object: 0.00502857206712 ms
    run_empty_obfuscated_code_object: 0.0433015928002 ms

    run_one_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
    run_one_thousand_obfuscated_bytecode: 0.11426033197 ms

    run_ten_thousand_no_obfuscated_bytecode: 0.00474920695228 ms
    run_ten_thousand_obfuscated_bytecode: 0.72383501255 ms
    INFO     Finish benchmark test.

```

Here it's a normal license checked by verify_license. If the license
is bind to fixed machine, for example, mac address, it need more time
to read hardware information.

import_obfuscated_module will first restore obfuscated code object,
then import this pre-compiled code object.

The bytecode size of function one_thousand is about 1K, and
ten_thousand is about 10K. Most of them will not be executed, because
they're in False condition for ever. So run_empty, run_one_thousand,
run_ten_thousand are almost same in non-obfuscated mode, about 0.004
ms.

In obfuscated mode, it's about 0.1 ms for 1K bytecoe, and 0.7~0.8 ms
for 10K bytecode in my laptop. It's mainly consumed by restoring
obfuscated bytecodes.

See another mode, only module obfuscated

```
    python pyarmor.py benchmark --obf-code-mode=none
    INFO     Start benchmark test ...
    INFO     Obfuscate module mode: des
    INFO     Obfuscate bytecode mode: none
    INFO     Benchmark bootstrap ...
    INFO     Benchmark bootstrap OK.
    INFO     Run benchmark test ...
    load_pytransform: 7.96721371012 ms
    init_pytransform: 3.8571941406 ms
    verify_license: 0.728025489273 ms

    Test script: bfoo.py
    Obfuscated script: obfoo.py
    Start test with mode 7
    --------------------------------------

    import_no_obfuscated_module: 10.7399124749 ms
    import_obfuscated_module: 8.19601373918 ms

    run_empty_no_obfuscated_code_object: 0.00530793718196 ms
    run_empty_obfuscated_code_object: 0.00391111160776 ms

    run_one_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
    run_one_thousand_obfuscated_bytecode: 0.00391111160776 ms

    run_ten_thousand_no_obfuscated_bytecode: 0.00446984183744 ms
    run_ten_thousand_obfuscated_bytecode: 0.00391111160776 ms
    INFO     Finish benchmark test.

```
It's even faster than no obfuscated scripts!

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
