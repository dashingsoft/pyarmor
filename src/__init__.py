# Package pyarmor
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
def main_entry():
    from pyarmor.pyarmor import main
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main(sys.argv[1:])
