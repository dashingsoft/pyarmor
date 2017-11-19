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
    
    n   LOAD_GLOBAL              ? (armor)
    n+3 CALL_FUNCTION            0
    n+6 POP_TOP
    n+7 JUMP_ABSOLUTE            0

```
  In the next section, we'll explain these instructions in details

- Save obfuscated code objects as .pyc or .pyo, so it can be run or
  imported by common Python interpreter.

## Run or Import Obfuscated Python Scripts

Those obfuscated python scripts can be run and imported as normal way
by common python interpreter, only when those code object is called,
refer to above code

- For each obfuscated code object, first op is jump to offset n.

- At offset n, the instruction is to call a PyCFunction. It will
  restore those obfuscation bytecode between offset 3 and n, and place
  the original bytecode from offset 0
  
- After function call, the last instruction is to jump to
  offset 0. The really bytecode now is executed.

## Performance Analaysis

With default configuration, Pyarmor will do the following extra work
to run or import obfuscated bytecode:

- Verify license at statup
- Restore obfuscated bytecode when code object is called first time

In my laptop, it spend about ?ms to check license, if this license is
bind to fixed machine, it need more time to read hardware information.

Regarding to the second factor, it equals 

    F + V * n

- F is the time consumed to run an empty code object which bytecode is obfuscated
- V is the time counsumed to obfuscate every 1K bytes bytecode
- n is the length of bytecode in K bytes

In my laptop, F is about ?ms, V ?ms. To get the exactly data in the
target machine, run the following command

```
  python pyarmor.py check --profile
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
