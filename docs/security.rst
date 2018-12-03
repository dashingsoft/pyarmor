.. _the security and anti-debug:

The Security and Anti-Debug
===========================

|PyArmor| cound obfuscate code object in runtime, each function is
restored only as it's called and will be obfuscated as soon as code
object completed execution. So even trace code in any ``c`` debugger,
only a piece of code object could be got one time.

From |PyArmor| v4.5, anti-debug code is added into dynamic library
``_pytransform``, but it's not strong.

If you want to hide your source code more thoroughly, try to use any
dynamic library protection tool such as ASProtect_, VMProtect_ to
protect dynamic library ``_pytransform`` which is distributed with
obfuscatd scripts.

.. include:: _common_definitions.txt
