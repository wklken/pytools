#!/usr/bin/python
# -*- coding:utf-8 -*-
# back_up.py
# this script is used to back up files of dirs
# wiil create dir in path ~/bak/
# created 2011-10-29 version0.1

import sys,os,time,shutil,getopt

BACK_UP_DIR = "~/bak/"

COLOR_NONE = "\033[m"
COLOR_GREEN = "\033[01;32m"
COLOR_RED = "\033[01;31m"
COLOR_YELLOW = "\033[01;33m"

def get_timestamp():
  return time.strftime('%Y%m%d%H%M%S',time.localtime())

def back_up_file(in_path):
  if not os.path.exists(in_path):
    print("The file/dir to back up  is not exists!")
    sys.exit(1)
  back_root = os.path.expanduser(BACK_UP_DIR)  
  if not os.path.exists(back_root):
    os.mkdir(back_root)

  time_stamp = get_timestamp()
  if os.path.isdir(in_path):  
    if in_path.endswith(os.sep):
      in_path = in_path[:-1]
    dir_name = os.path.basename(in_path)
    back_path = back_root+dir_name
    if not os.path.exists(back_path):
      os.mkdir(back_path)
    back_des =  back_path+"/"+dir_name+"_"+time_stamp
    shutil.copytree(in_path,back_des)  

  elif os.path.isfile(in_path):
    des = os.path.basename(in_path)
    back_des = back_root+des+"_"+time_stamp
    shutil.copy(in_path,back_des)

  if os.path.exists(back_des):
    print(COLOR_GREEN + "Back up success!" + COLOR_NONE)
    print("Back up path:" + COLOR_GREEN + back_des + COLOR_NONE )
  else:
    print(COLOR_RED + "Back up Failed!" + COLOR_NONE)

def help_msg():
  print("功能：快速备份文件夹或目录")
  print("选项:")
  print("\t -i inputfilepath  [必输，原文件路径]")
  print("\t -h                [可选，帮助信息 ]")
  sys.exit(0)

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:h")
        for op,value in opts:
          if op in ("-h","-H","--help"):
            help_msg()
          if op == "-i":
            in_path = value
    except getopt.GetoptError:
      print(sys.argv[0]+" : params are not defined well!")
    back_up_file(in_path)

if __name__ == "__main__":
  main()



