#!/usr/bin/python
#Notice: get the source from python cookbook,change a little
#version 0.1
#desc: check if a xml is well-formed

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob
import sys
import platform

sys_name = platform.platform().lower()
if sys_name.endswith("nix") or sys_name.startswith("cygwin"):
    COLOR_NONE = "\033[m"
    COLOR_GREEN = "\033[01;32m"
    COLOR_RED = "\033[01;31m"
else:
    COLOR_NONE = COLOR_GREEN = COLOR_GREEN = ''


def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)

if len(sys.argv) < 2:
    print "Error: Params not well defined"
for arg in sys.argv[1:]:
    for filename in glob(arg):
        try:
            parsefile(filename)
            print COLOR_GREEN + ("%s is well-formed" % filename) + COLOR_NONE
        except Exception, e:
            print COLOR_RED + ("%s is NOT well-formed! %s" % (filename, e)) + COLOR_NONE
