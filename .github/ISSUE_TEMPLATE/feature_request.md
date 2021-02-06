---
name: Feature request
about: 'Request for new platform or suggest an idea for this project '
title: "[Enhancement]"
labels: enhancement
assignees: jondy

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

If request for new platform, first check all the supported platforms by `pyarmor download`. If it's really not in the list, run the following script in this platform and provide the output by text not snapshot image

```python
from platform import *
print('system name: %s' % system())
print('machine: %s' % machine())
print('processor: %s' % processor())
print('aliased terse platform: %s' % platform(aliased=1, terse=1))

if system().lower().startswith('linux'):
    print('libc: %s' % libc_ver())
    print('distribution: %s' % linux_distribution())
```
