#!/usr/bin/python
import sys
from elementtree.ElementTree import ElementTree

COLOR_NONE = "\033[m"
COLOR_GREEN = "\033[01;32m"
COLOR_RED = "\033[01;31m"
COLOR_YELLOW = "\033[01;33m"

if len(sys.argv) < 2:
    print "Error: Params not well defined"

xml_paths = sys.argv[1:] 

for xml_path in xml_paths:
    tree = ElementTree()
    
    try:
        tree.parse(xml_path)
    except:
        print COLOR_RED + "ERROR:[ " + COLOR_YELLOW + xml_path + COLOR_RED + " ] is not a well formed xml file!!!!" + COLOR_NONE
        continue
    print COLOR_GREEN + "Info:[ " + COLOR_YELLOW + xml_path + COLOR_GREEN + " ] The XML file is normal!" + COLOR_NONE
