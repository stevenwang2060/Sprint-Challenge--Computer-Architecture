#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

sys.path.append('/ls8/cpu.py')

cpu = CPU()
if len(sys.argv) != 2:
    print("No file parameter found...")
    print("usage: python3 examples/print8.ls8")
    sys.exit(1)
load_file = sys.argv[1]
cpu.load(load_file)
cpu.run()