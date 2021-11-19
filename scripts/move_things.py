# -*- coding: utf-8 -*-
"""
"""

from mover_thingy import DirectoryWalker
import sys


if __name__ == "__main__":
    dw = DirectoryWalker(*sys.argv[1:])
    dw.go()
