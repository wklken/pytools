#!/usr/bin/env python
# -*- coding=utf-8 -*-

from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob
import sys
from StringIO import StringIO

def parsefile(file):
    
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    xml_str = open(file).read().replace('encoding="gbk"', 'encoding="utf-8"')
    f = StringIO(xml_str)
    parser.parse(f)

for arg in sys.argv[1:]:
    for filename in glob(arg):
        try:
            parsefile(filename)
            print "%s is well-formed" % filename
        except Exception, e:
            print "%s is NOT well-formed! %s" % (filename, e)
