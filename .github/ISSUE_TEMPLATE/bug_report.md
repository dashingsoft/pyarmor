---
name: Bug report
about: Report a bug of pyarmor
title: "[BUG]"
labels: bug
assignees: jondy

---

First please click Preview button above

**Next please click the following link to read the page "Questions" and the related links mentioned in the section "Common Solutions"**

[Questions](https://pyarmor.readthedocs.io/en/latest/questions.html)

**Do not submit the question solved in the documentation, this kind of issue will be marked as "documented" and be closed directly.**

If it's a new question, please provide the following information:

1. A clear and concise description of the question (required)
2. The full pyarmor command and full output log (required if something is wrong)
3. If distributing the obfuscated script to other machine, which files are copied (optional)
4. The command to run the obfuscated scripts and full traceback when something is wrong

**If missing necessary information and I don't know how to help you, the issue will be marked as "invalid" and be closed direclty**

**Hint**
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

**Finally remove all the above content and submit your question**
