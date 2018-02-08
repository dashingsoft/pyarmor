# Package pyarmor.webui
import sys
import os
sys.path.append(os.path.dirname(__file__))
def main():
    from server import main as main_entry
    main_entry()
