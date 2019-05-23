#!/usr/bin/env python

import os
import subprocess


def main():
    files = os.listdir()
    jsfiles = filter(lambda s: s.endswith('.js'), files)
    for jsf in jsfiles:
        print("Building", jsf)
        subprocess.run(["browserify", jsf, "-o", "static/"+jsf])


if __name__ == "__main__":
    main()
