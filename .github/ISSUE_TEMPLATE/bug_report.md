---
name: Bug report
about: Report a bug of pyarmor
title: "[BUG] `Error message`"
labels: bug
assignees: ''

---

Please read this first before report any issue
https://pyarmor.readthedocs.io/en/latest/questions.html

If this issue has been documented and there is solution in FAQ, it will be marked as `documented` and be closed it immediately.

Do not ask questions here but in discussions, it will be closed immediately.

A good report should have

- A clear title
- Reproduced steps
- Expected results and actual results

Please also provide necessary log (but not full log), for example, the whole command options `pyarmor gen` and first 4 logs in the console, paste the text directly, DO NOT paste IMAGE

```
$ pyarmor gen -O dist --assert-call foo.py
INFO     Python 3.10.0
INFO     Pyarmor 8.4.0 (trial), 000000, non-profits
INFO     Platform darwin.x86_64

```

In order to save time for both of us, if the bug report is not clear or missing necessary information, it will be marked as `invalid` and be closed immediately.
