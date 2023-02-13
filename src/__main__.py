import os
import sys

from configparser import ConfigParser


def call_pyarmor():
    from .pyarmor import main_entry
    main_entry()


def call_pyarmor_cli():
    from .cli.__main__ import main
    main()


def find_cli_command(args):
    commands = 'generate', 'register', 'shell'
    return not args or len(args) < 2 \
        or set(['cfg', 's']).intersection(args) \
        or any([cmd.startswith(arg) for arg in args for cmd in commands])


def boot_pyarmor():
    try:
        c = ConfigParser()
        c.read(os.path.expanduser(os.path.join('~', '.pyarmor', 'global')))
        call_pyarmor_cli() if c.getint('pyarmor', 'boot') else call_pyarmor()
        return True
    except Exception:
        pass


if boot_pyarmor() is None:
    call_pyarmor_cli() if find_cli_command(sys.argv[1:8]) else call_pyarmor()
