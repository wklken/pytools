#!/usr/bin/python
# -*- coding:utf-8 -*-
#ftp.py
#    lingyue.wkl@taobao.com or wukunliang@163.com
#this script is used to do some operations more convenient via ftp
  #1.[p]upload many files in the same time,show md5s
  #2.[g]download many files in the same time,show md5s
  #3.[l]list all the files on ftp site
  #4.[f]search a file on ftp site,return True or Flase
  #5.[h]show help info

#add upload and download operations  20111210 version0.1
#add md5sum after ops 20120308 version0.2

import sys,os,ftplib,socket

CONST_HOST = "ip"
CONST_USERNAME = "username"
CONST_PWD = "pwd"
CONST_BUFFER_SIZE = 8192

COLOR_NONE = "\033[m"
COLOR_GREEN = "\033[01;32m"
COLOR_RED = "\033[01;31m"
COLOR_YELLOW = "\033[01;33m"

def connect():
  try:
    ftp = ftplib.FTP(CONST_HOST)
    ftp.login(CONST_USERNAME,CONST_PWD)
    return ftp
  except socket.error,socket.gaierror:
    print("FTP is unavailable,please check the host,username and password!")
    sys.exit(0)

def disconnect(ftp):
  ftp.quit()

def upload(ftp, filepath):
  f = open(filepath, "rb")
  file_name = os.path.split(filepath)[-1]
  try:
    ftp.storbinary('STOR %s'%file_name, f, CONST_BUFFER_SIZE)
  except ftplib.error_perm:
    return False
  return True

def download(ftp, filename):
  f = open(filename,"wb").write
  try:
    ftp.retrbinary("RETR %s"%filename, f, CONST_BUFFER_SIZE)
  except ftplib.error_perm:
    return False
  return True

def list(ftp):
  ftp.dir()

def find(ftp,filename):
  ftp_f_list = ftp.nlst()
  if filename in ftp_f_list:
    return True
  else:
    return False

def help():
  print("help info:")
  print("[./ftp.py l]\t show the file list of the ftp site ")
  print("[./ftp.py f filenamA filenameB]\t check if the file is in the ftp site")
  print("[./ftp.py p filenameA filenameB]\t upload file into ftp site")
  print("[./ftp.py g filenameA filenameB]\t get file from ftp site")
  print("[./ftp.py h]\t show help info")
  print("other params are invalid")

def main():
  args = sys.argv[1:]
  if len(args) == 0:
    print("Params needed!")
    sys.exit(0)

  ftp = connect()

  success_list = []
  failed_list = []

  if args[0] == "p":
    f_list = args[1:]

    for up_file in f_list:
      if not os.path.exists(up_file):
        print(("UPLOAD: %s "+COLOR_RED+"FAILED"+COLOR_NONE+"  :file not exist")%up_file)
        continue
      elif not os.path.isfile(up_file):
        print(("UPLOAD: %s "+COLOR_RED+"FAILED"+COLOR_NONE+"  :%s is not a file")%(up_file,up_file))
        continue

      if upload(ftp, up_file):
        success_list.append(up_file)
      else:
        failed_list.append(up_file)
    if len(success_list) > 0 :
      print((COLOR_GREEN + "UPLOAD SUCCESS: %s" + COLOR_NONE)%(" ".join(success_list)))
      print("md5sum:")
      for f in success_list:
        print( os.popen("md5sum " + f).read()[:-1])
    if len(failed_list) > 0:
      print((COLOR_RED + "UPLOAD FAILED: %s" + COLOR_NONE)%(" ".join(failed_list)))

  elif args[0] == "g":
    f_list = args[1:]

    for down_file in f_list:
      if not find(ftp,down_file):
        print(("DOWNLOAD: %s "+COLOR_RED+"FAILED"+COLOR_NONE+"  :%s is not in the ftp site")%(down_file,down_file))
        continue

      if download(ftp, down_file):
        success_list.append(down_file)
      else:
        failed_list.append(down_file)
    if len(success_list) > 0 :
      print((COLOR_GREEN + "DOWNLOAD SUCCESS: %s" + COLOR_NONE)%(" ".join(success_list)))
      print("md5sum:")
      for f in success_list:
        print( os.popen("md5sum " + f).read()[:-1])
    if len(failed_list) > 0:
      print((COLOR_RED + "DOWNLOAD FAILED: %s" + COLOR_NONE)%(" ".join(failed_list)))

  elif args[0] == "l":
    list(ftp)
  elif args[0] == "f":
    f_list = args[1:]
    for f_file in f_list:
      if find(ftp,f_file):
        print(("SEARCH: %s "+COLOR_GREEN+"EXIST"+COLOR_NONE)%f_file)
      else:
        print(("SEARCH: %s "+COLOR_RED+"NOT EXIST"+COLOR_NONE)%f_file)
        if len(f_file) > 3:
          print("Similar File List:")
          s = ftp.nlst()
          print  ", ".join([k for k in s if f_file in k])

  elif args[0] == "h":
    help()
  else:
    print("args are invalid!")
    help()

  disconnect(ftp)

if __name__ == "__main__":
  main()
