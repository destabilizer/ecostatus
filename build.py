#!/usr/bin/env python

import os
import subprocess


def main():
    files = os.listdir()
    jsfiles = filter(lambda s: s.endswith('.js'), files)
    for jsf in jsfiles:
        print("Building", jsf)
        subprocess.run(["browserify", jsf, "-o", "static/"+jsf])
    #cp node_modules/noty/lib/noty.css static/noty.css
    #cp node_modules/noty/lib/themes/mint.css static/mint.css


if __name__ == "__main__":
    main()
