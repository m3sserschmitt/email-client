#!/usr/bin/env python

import subprocess
import sys

modules_required = ["tkinterhtml", "bs4", "termcolor", "mail-parser", "lxml"]

interpreter_location = "\"" + sys.executable + "\"";
print(interpreter_location)

for module in modules_required:
    print(subprocess.check_output(f"{interpreter_location} -m pip install {module}", shell=True).decode(), '\n')
