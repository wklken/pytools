#!/usr/bin/python
# -*- coding: utf-8 -*-

#trans_lasttable_xml.py
# version 0.10  created by lingyue.wkl 20110825 18:06
#this script trans the lasttable_xml file to the easier readable format 
#modify to output with tags   20111201
# last modified by lingyue.wkl     wklken@yeah.net/lingyue.wkl@taobao.com

#TODO:排序  不要按字典序，增加可按数字序
import os,getopt,sys,urllib

#read file and return lines
def read_file(path):
  f = open(path,"r")
  lines = f.readlines()
  f.close()
  return lines

#读入文件，将宝贝信息输出，及<doc></doc> 转为一条宝贝记录,map形式存放
def process_lines(lines):
  result = []
  xml_cell = {}
  sign = False
  for line in lines:
    line = line[:-2]  #-2  \n
    if line.startswith("<doc>"):
      sign = True
      xml_cell = {}
      continue
    elif line.startswith("</doc>"):
      sign = False
      result.append(xml_cell)
      continue

    if sign:
      parts = line.split("=")
      if len(parts) == 2:
        xml_cell.update({parts[0]:parts[1]})
      else:
        continue
  return result

#将字段直接拼接为url
def toUrlStr(result,outpath):
  url_lines = []
  for xml_cell in result:
    line = []
    keys = xml_cell.keys()
    for key in keys:
      url = urllib.urlencode({key:xml_cell.get(key)})  
      line.append(url)
    url_lines.append("&".join(line)+"\n")  
  f = open(outpath,"w")
  f.writelines(url_lines)
  f.close()
    

#根据逻辑，针对宝贝字段，拼接输出格式
def output_lines(array, result, with_tag):
  out_lines = []
  for xml_cell in result:
    line = []
    for col in array:
      if "=" in col:
        if with_tag:
          line.append(col)
        else:
          line.append(col.split("=")[1])
        continue
      if xml_cell.get(col) != None:
        if with_tag:
          line.append(col+"="+xml_cell.get(col))
        else:
          line.append(xml_cell.get(col))
      else:
          line.append('')
      #else:
      #  if with_tag:
      #    line.append(col+"=")
      #  else:
      #    line.append('')
    if len(line) > 0:
      out_lines.append(line)
  return out_lines

#对结果数据进行排序，可以指定列号
def sort_output(col_id,out_lines):
  return sorted(out_lines,cmp=lambda a,b:cmp(a[col_id],b[col_id]))

#对结果进行反序
def reverse_output(out_lines):
  out_lines.reverse()
  return out_lines

#输出
def send_to_output_file(out_lines,out_path,osp):
  lines = []
  for line in out_lines:
    lines.append(osp.join(line)+"\n")
  f = open(out_path,"w")
  f.writelines(lines)
  f.close()

#帮助信息
def help_msg():
    print("功能：只显示lasttable的某些字段，可指定排序字段")
    print("选项:")
    print("\t -i inputfilepath  [必输，原文件路径]")
    print("\t -a 'tag1,tag3,tag4'        [必输，xml中字段key，指定输出的序列，按序列顺序输出对应的值]")
    print("\t -s 'sort_tag'              [可选，排序的字段标签，不输默认用-a第一个字段排序,sort_tag必为-a中一个，否则使用默认]")
    print("\t -o outputfilepath [可选，默认为 inputfilepath.dist ]")
    print("\t -r            [可选，将结果反序输出 ]")
    print("\t -P 'OFS'          [可选，输出文件的域分隔符，默认为\\t ]")
    print("\t -u           [可选，将doc格式转化为url，=后面内容有经过urlencode\\t ]")
    print("\t -t           [可选，输出标签\\t ]")
    sys.exit(0)

#程序入口，读入参数，执行
def main():
    reverse = False
    with_tag = False
    outsp = "\t"
    toUrl = False
    try:
        opts,args = getopt.getopt(sys.argv[1:],"P:a:i:o:s:rhtu")
 
        for op,value in opts:
          if op in ("-h","-H","--help"):
            help_msg()
          if op == "-i":
            inpath = value
          elif op == "-o":
            outpath = value
          elif op == "-r":
            reverse = True 
          elif op == "-a":
            tags = value.split(",")
          elif op == "-s":
            sort_tag = value
          elif op == "-P":
            outsp = value.decode("string_escape")
          elif op == "-u":
            toUrl = True 
          elif op == "-t":
            with_tag = True
        #考虑下这边放在神马地方合适
        if len(opts) < 2:
          print(sys.argv[0]+" : the amount of params must great equal than 3")
          sys.exit(1)
    except getopt.GetoptError:
      print(sys.argv[0]+" : params are not defined well!")
    
    if 'inpath' not in dir():
      print(sys.argv[0]+" : -i param is needed,input file path must define!")
      sys.exit(1)
    
    if not toUrl and 'tags' not in dir():
      print(sys.argv[0]+" : -a param is needed,must assign the field tags put !")
      sys.exit(1)

    if not os.path.exists(inpath):
      print(sys.argv[0]+" file : %s is not exists"%inpath)
      sys.exit(1)

    if 'outpath' not in dir():
      outpath = inpath+".dist"

    #step 1:读到所有行
    lines = read_file(inpath)
    #step 2:拆分，得到每个宝贝的信息
    result = process_lines(lines)

    #step 3-1:带-u，表示转为query请求格式，调用toUrlStr,退出
    if toUrl:
       toUrlStr(result,outpath)
       sys.exit(0)
    
    #step 3-2: 不带-u，转为默认的格式输出
    out_lines = output_lines(tags,result,with_tag)

    #step 4 :排序,默认用第一个字段
    if "sort_tag" not in dir():
      sort_tag = tags[0]
    sort_col_id = tags.index(sort_tag)
    out_lines = sort_output(sort_col_id,out_lines)

    #step 5 :判定是否反序
    if reverse:
      out_lines = reverse_output(out_lines)

    #step 6 :输出
    send_to_output_file(out_lines,outpath,outsp)


if __name__ =="__main__":
   main()
