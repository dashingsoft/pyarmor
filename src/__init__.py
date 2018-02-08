# Package pyarmor
# This is main entry
def main():
    from pyarmor2 import main as main_entry
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    main_entry(sys.argv[1:])

