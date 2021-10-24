---
name: Question
about: Something you're not sure but nothing found in documentation, or it's not clear
title: ''
labels: question
assignees: jondy

---

It's more readable in the issue Preview mode for all the hints

**IMPORTANT**

Please first read the document list in the below before asking a question.

If reporting the error, please provide the following information:

1. A clear and concise description of the question
2. The full pyarmor command and full output log
3. If distributing the obfuscated script to other machine, which files are copied
4. The command to run the obfuscated scripts and full traceback when something is wrong

The output log could be redirected to a file by this way. For example,

    pyarmor obfuscate foo.py >log.txt 2>&1

If missing the necessary information, or ambiguous description, or the question has been described in the document, the issue will be marked as "invalid" and be closed direclty.

**Hint 1**
[Basic usage](https://pyarmor.readthedocs.io/en/latest/usage.html)
[Advanced usage](https://pyarmor.readthedocs.io/en/latest/advanced.html)
[Command usage](https://pyarmor.readthedocs.io/en/latest/man.html)
[Support platforms](https://pyarmor.readthedocs.io/en/latest/platforms.html)
[Performance](https://pyarmor.readthedocs.io/en/latest/performance.html)
[Security](https://pyarmor.readthedocs.io/en/latest/security.html)
[License](https://pyarmor.readthedocs.io/en/latest/license.html)

**Hint 2**
If something you're not sure, but it could be verified by doing a test in five minutes, just do it to save time for both of us. For example, understand the difference of super mode and non-super mode scripts by a simple test
```
mkdir test-non-super-mode
cd test-non-super-mode
echo "print('Hello')" > foo.py
pyarmor obfuscate foo.py

# check the output file list and the content of obfuscated scripts in non-super mode
ls dist/
cat dist/foo.py

mkdir test-super-mode
cd test-super-mode
echo "print('Hello')" > foo.py
pyarmor obfuscate --advanced 2 foo.py

# check the output file list and the content of obfuscated scripts in super mode
ls dist/
cat dist/foo.py
```

**Hint 3**
Please remove all the above hints before your question
