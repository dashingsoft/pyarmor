# How to Obfuscate Python Script by Pyarmor

From Pyarmor 3.3.0, a new mode is introduced. By this way, no import
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

## Usage

In Pyarmor 3.3, there are 2 modes to obfucate python scripts:

* mode 7: only code object of python module is obfuscated, it's almost
  quickly as no obfuscated module.
  
```
    python pyarmor.py --with-capsule=project.zip --output=dist --mode=7 foo.py
    
```

* mode 8: both code object and bytecode are obfuscated, it's slower
  but more secure. It's the default mode.

```
    python pyarmor.py --with-capsule=project.zip --output=dist --mode=8 foo.py

```

### Change Obfuscated Algorithm

For mode 8, there is another option which could reduce the elapsed
time

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
disabled, another simple algorithm is applied, it's fater than DES
remarkably.

## Performance Analaysis

With default configuration, Pyarmor will do the following extra work
to run or import obfuscated bytecode:

- Load library _pytransform at startup
- Initialize library _pytransform at startup
- Veirfy license at startup
- Restore obfuscated code object of python module
- Restore obfuscated bytecode when code object is called first time

There is a script "benchmark.py" in the package of Pyarmor used to
check performance. First run it to prepare test data

```
    python benchmark.py bootstrap MODE

```

**MODE** could be 7, 8, and the default value is 8

For example,

```
    python benchmark.py bootstrap
```

It will create directory "test-bench", change to this directory, and
run benchmark.py again. In my laptop, the output is

```
    cd test-bench
    
    # Run this command more times to check the results
    python benchmark.py
    
    load_pytransform: 1.93544151561 ms
    init_pytransform: 1.29848905378 ms
    verify_license: 0.727187393929 ms
    
    Test script: bfoo.py
    Obfuscated script: obfoo.py
    Start test with mode 8
    --------------------------------------
    
    import_no_obfuscated_module: 0.315403214654 ms
    import_obfuscated_module: 1.37224144409 ms
    
    run_empty_no_obfuscated_code_object: 0.00474920695228 ms
    run_empty_obfuscated_code_object: 0.0441396881447 ms
    
    run_one_thousand_no_obfuscated_bytecode: 0.00502857206712 ms
    run_one_thousand_obfuscated_bytecode: 0.117333348233 ms
    
    run_ten_thousand_no_obfuscated_bytecode: 0.00642539764132 ms
    run_ten_thousand_obfuscated_bytecode: 0.726908028814 ms
    
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

Now let's test mode 7

```
    cd ..
    python benchmark.py bootstrap 7
    
    cd test-bench
    python benchmark.py
    
    load_pytransform: 1.74212085614 ms
    init_pytransform: 1.29625413286 ms
    verify_license: 0.757079461216 ms
    
    Test script: bfoo.py
    Obfuscated script: obfoo.py
    Start test with mode 7
    --------------------------------------
    
    import_no_obfuscated_module: 0.325739723903 ms
    import_obfuscated_module: 1.32474937457 ms
    
    run_empty_no_obfuscated_code_object: 0.00446984183744 ms
    run_empty_obfuscated_code_object: 0.00363174649292 ms
    
    run_one_thousand_no_obfuscated_bytecode: 0.00502857206712 ms
    run_one_thousand_obfuscated_bytecode: 0.00363174649292 ms
    
    run_ten_thousand_no_obfuscated_bytecode: 0.006984127871 ms
    run_ten_thousand_obfuscated_bytecode: 0.00391111160776 ms
    
```
Notice it almost spends same time with no obfuscate scripts. Because
bytecode of each code object isn't obfuscated.

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
