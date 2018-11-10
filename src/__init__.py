# Package pyarmor
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
def main_entry():
    try:
        from pyarmor import main
    except ImportError:
        from .pyarmor import main
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
