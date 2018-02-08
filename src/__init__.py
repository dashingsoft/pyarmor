# Package pyarmor
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
def main():
    from pyarmor2 import main as main_entry
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main_entry(sys.argv[1:])
