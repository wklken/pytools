#!/usr/bin/env python
# -*- coding:utf-8 -*-
#datafilter.py
# lingyue.wkl@taobao.com or wukunliang@163.com
#created 20111008 lingyue.wkl version0.1
#
import sys,os,getopt

def get_lines(path):
  f = open(path,"r")
  lines = f.readlines()
  f.close()
  return lines
  #return [line[:-1] for line in lines ]

def filter(lines,insp,isBlankCut):
  new_lines = []
  for line in lines:
    if isBlankCut and len(line.strip()) == 0:
      continue
    if not line.strip().startswith(insp):
      new_lines.append(line)
  return new_lines    

def output(outpath,new_lines):
  f = open(outpath,"w")
  f.writelines(new_lines)
  f.close()
  
#打印帮助信息
def help_msg():
  print("功能：数据过滤，清理注释行[空行]")
  print("选项:")
  print("\t -i inputfilepath  [必输，原文件路径]")
  print("\t -o outputfilepath [可选，默认为 inputfilepath.dist ]")
  print("\t -F 'FS'           [可选，要去除注释行开始标志，默认为# ]")
  print("\t -b                [可选，是否删除空行,默认不剔除空行 ]")
  sys.exit(0)

#程序入口，读入参数，执行
def main():
    insp = "#"
    isBlankCut = False
    try:
        opts,args = getopt.getopt(sys.argv[1:],"F:i:o:bh")

        for op,value in opts:
          if op in ("-h","-H","--help"):
            help_msg()
          if op == "-i":
            inpath = value
          elif op == "-o":
            outpath = value
          elif op == "-F":
            insp = value.decode("string_escape")
          elif op == "-b":
            isBlankCut = True

        if len(opts) < 1:
          print(sys.argv[0]+" : the amount of params must great equal than 1")
          sys.exit(1)

    except getopt.GetoptError:
      print(sys.argv[0]+" : params are not defined well!")
    
    
    if 'inpath' not in dir():
      print(sys.argv[0]+" : -i param is needed,input file path must define!")
      sys.exit(1)
    
    if not os.path.exists(inpath):
      print(sys.argv[0]+" file : %s is not exists"%inpath)
      sys.exit(1)

    if 'outpath' not in dir():
      outpath = inpath+".dist"

    lines = get_lines(inpath)
    new_lines = filter(lines,insp,isBlankCut)
    output(outpath,new_lines)

if __name__ =="__main__":
    main()
