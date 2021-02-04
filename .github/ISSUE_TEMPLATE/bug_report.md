---
name: Bug report
about: Report a bug of pyarmor
title: "[Bug]"
labels: bug
assignees: jondy

---

It's more readable in the issue Preview mode for the hints

**Hints**
Every pyarmor command prints detail logs in the console, not only check the last error message, but also check each log to understand what pyarmor is doing. And `pyarmor -d subcommand ...` even prints more debug logs, it's very useful to find the problem.

When running the obfuscated scripts, if there is traceback, check the source script according to script name and line number in the traceback, make sure it doesn't use some features changed by pyarmor 

Before report a bug, please read these common questions and solutions first
https://pyarmor.readthedocs.io/en/latest/questions.html

And remove all the above hints.

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Obfuscate the scripts by which Python version and in which platform
2. What command options used
3. How to distribute the obfuscated scripts to target machine if it's different from build machine
4. Run the obfuscated scripts in which platform by which Python version
5. When see error, provide the full traceback and console output by text not snapshot, quote them like this

```
pyarmor obfuscate foo.py
... 
```

**Additional context**
Add any other context about the problem here.
