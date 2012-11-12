#!/usr/bin/python
# -*- coding: utf-8 -*-
#gen_lasttable_xml.py
#used just for creating the xml file for lasttable common/mall
#2011-08-08 version0.1 created by lingyue.wkl
#2011-12-15 add user
import os,getopt,sys

#读文件，返回所有行
def read_file(path):
  f = open(path,"r")
  lines = f.readlines()
  f.close()
  return lines

#process one line
#包含特殊逻辑，需要再后期提出来，方便扩展
def one_line_proc(parts,tags,outsp):
    toindex = 0
    total = len(tags)
    outline=""
    for i in range(1,total+1):
      #选项带=
      if "=" in tags[toindex] :
          outline +=  tags[toindex] + outsp + "\n"
          toindex+=1
          continue
      #数据中存在 del
      if ("del:"+tags[toindex]) in parts[toindex]:
          pass
      #数据中格式为   tag=value的形式，直接输出
      elif tags[toindex] in parts[toindex] and "=" in parts[toindex]:
          outline += parts[toindex]+outsp+"\n"
      #数据中带关键字use
      elif "use:" in  parts[toindex] and "=" in parts[toindex]:
          outline += parts[toindex][4:] + outsp+"\n"
      #纯数据 
      else:
          outline += tags[toindex]+"="+parts[toindex]+outsp+"\n"
      toindex+=1
    #返回所有行
    return outline

#处理入口
def process(inpath,root,tags,noise,outpath,insp="\t",outsp=""):
  count_default = tags.count("=")
  tags = tags.split(",")
  tags_len = len(tags) - count_default
  #step1 :read all lines
  lines = read_file(inpath)

  f = open(outpath,"w")
  result=[]
  #step2 :process each line
  for line in lines:
     parts = line.strip("\n").split(insp)
     if len(parts) > tags_len: #中间某个字段值存在^I会出错，目前只适应最后一个的
       parts[tags_len-1] = "\t".join(parts[tags_len-1:])
       del parts[tags_len:]

     if len(parts) == tags_len:
       result.append("<"+root+">"+outsp+"\n")
       #line process func
       outline = one_line_proc(parts,tags,outsp)
       result.append(outline)
       if noise:
         result.append("aaaa=bbb\n")
       result.append("</"+root+">"+outsp+"\n")
  #step 3:output
  f.writelines(result)
  f.close()


#判断某个参数必须被定义
def must_be_defined(param, map, error_info):
    if param not in map:
       print error_info
       sys.exit(1)

#打印帮助信息
def help_msg():
  print("功能：专用于lasttable的xml文件生成,将源文件转为目标xml文件")
  print("选项:")
  print("\t -i inputfilepath     [必输，原文件路径]")
  print("\t -r rootTag           [必输，xml根标签]")
  print("\t -a 'taga,tagb,tagc'  [必输，域编号字符串，逗号分隔。指定域用原数据字段填充，未指定用'0'填充]")
  print("\t -n                   [可选，若配置，在每个tag中加入一行aaaa=bbb，作为干扰项]")
  print("\t -o outputfilepath    [可选，默认为 inputfilepath.dist ]")
  print("\t -F 'FS'              [可选，原文件域分隔符，默认为\\t ]")
  print("\t -P 'OFS'             [可选，输出文件的域分隔符，默认为^A,对于目前lasttable表格式，不需要进行配置]")
  sys.exit(0)

#程序入口，读入参数，执行
def main():
    #init param value
    insp="\t"
    outsp="^A"
    #step 1: read all options
    try:
        opts,args = getopt.getopt(sys.argv[1:],"F:P:a:i:o:r:hn")
 
        noise = False
        for op,value in opts:
          if op in ("-h","-H","--help"):
            help_msg()
          if op == "-n":
            noise = True
          if op == "-i":
            inpath = value
          elif op == "-o":
            outpath = value
          elif op == "-r":
            root = value
          elif op == "-a":
            tags = value
          elif op == "-F":
            insp = value.decode("string_escape")
          elif op == "-P":
            outsp = value.decode("string_escape")
        #考虑下这边放在神马地方合适
        if len(opts) < 3:
          print(sys.argv[0]+" : the amount of params must great equal than 3")
          sys.exit(1)
    except getopt.GetoptError:
      print getopt.GetoptError
      print(sys.argv[0]+" : params are not defined well!")
    
    #step2 :check and change option values
    params_map = dir()
    must_be_defined('inpath', params_map, sys.argv[0]+" : -i param is needed,input file path must define!")
    must_be_defined('root', params_map, sys.argv[0]+" : -r param is needed,the root element of xml file  must define!")
    must_be_defined('tags', params_map, sys.argv[0]+" : -a param is needed,must assign the field tags put !")

    if not os.path.exists(inpath):
      print(sys.argv[0]+" file : %s is not exists"%inpath)
      sys.exit(1)

    if 'outpath' not in dir():
      outpath = inpath+".dist"

    #step3 :call process
    process(inpath, root, tags, noise, outpath, insp, outsp)

if __name__ =="__main__":
    main()
