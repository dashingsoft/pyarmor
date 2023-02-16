import os
import sys


def call_pyarmor():
    from .pyarmor import main_entry
    main_entry()


def call_pyarmor_cli():
    from .cli.__main__ import main
    main()


def find_cli_command(argv):
    args = argv[1:8]
    cmds = 'generate', 'gen', 'g', 'register', 'reg', 'r', 'cfg'
    return not args or len(args) < 2 or set(cmds).intersection(args)


call_pyarmor() if os.getenv('PYARMOR_CLI', '') == '7' else \
    call_pyarmor_cli() if find_cli_command(sys.argv) else \
    call_pyarmor()
