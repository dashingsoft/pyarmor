import os
import sys


def call_pyarmor():
    from .pyarmor import main_entry
    main_entry()


def call_pyarmor_cli():
    from .cli.__main__ import main
    main()


def find_cli_command(argv):
    args = argv[1:6]
    cmds = 'generate', 'gen', 'g', 'register', 'reg', 'r', 'cfg'
    return not args or len(args) < 2 or set(cmds).intersection(args)


cli = os.getenv('PYARMOR_CLI', '')
if cli == '7':
    call_pyarmor()
elif cli == '8' or find_cli_command(sys.argv):
    call_pyarmor_cli()
else:
    call_pyarmor()
