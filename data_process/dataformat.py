#!/usr/bin/python
# -*- coding: utf-8 -*-
#dataformat.py
#   lingyue.wkl@taobao.com or wukunliang@163.com
#this script change data from your source to the dest data format
#2011-08-05 created version0.1
#2011-10-29 add row-row mapping ,default row value .rebuild all functions. version0.2 
#next:add data auto generate by re expression
#2011-12-17 add new functions, add timestamp creator.  version0.3
#2012-03-08 rebuild functions. version0.4
#2012-06-22 add function to support multi output separators
#2012-07-11 fix bug  line 44,add if
#2012-09-03 rebuild functions,add help msg! version0.5
#2012-11-08 last version edited by lingyue.wkl
#           this py: https://github.com/wklken/pytools/blob/master/data_process/dataformat.py

import os
import sys
import getopt
import time
import re

#read file and get each line without \n
def read_file(path):
    f = open(path, "r")
    lines = f.readlines()
    f.close()
    return [line[:-1] for line in lines ]

#处理一行，转为目标格式，返回目标行
def one_line_proc(parts, total, ft_map, outsp, empty_fill, fill_with_sno):
    outline = []
    #step1.获取每一列的值
    for i in range(1, total + 1):
        if i in ft_map:
            fill_index = ft_map[i]
            #加入使用默认值列  若是以d开头，后面是默认，否则取文件对应列 done
            if fill_index.startswith("d"):
                #列默认值暂不开启时间戳处理
                outline.append(fill_index[1:])
            else:
                outline.append(handler_specal_part(parts[int(fill_index) - 1]))
        else:
            #-s 选项生效，填充列号
            if fill_with_sno:
                outline.append(str(i))
            #否则，填充默认填充值
            else:
                outline.append(empty_fill)

    #step2.组装加入输出分隔符，支持多分隔符
    default_outsp = outsp.get(0,"\t")
    result = []
    outsize = len(outline)
    for i in range(outsize):
        result.append(outline[i])
        if i < outsize - 1:
            result.append(outsp.get(i + 1, default_outsp))
    #step3.拼成一行返回
    return ''.join(result)

#处理入口，读文件，循环处理每一行，写出
#输入数据分隔符默认\t,输出数据默认分隔符\t
def process(inpath, total, to, outpath, insp, outsp, empty_fill, fill_with_sno, error_line_out):
    ft_map = {}
    #有效输入字段数（去除默认值后的）
    in_count = 0
    used_row = []
    #step1-3相当于数据预处理，解析传入选项

    #step1 处理映射列 不能和第二步合并
    for to_row in to:
        if r"\:" not in to_row and len(to_row.split(":")) == 2:
            used_row.append(int(to_row.split(":")[1]))
        if r"\=" not in str(to_row) and len(str(to_row).split("=")) == 2:
            pass
        else:
            in_count += 1

    #step2 处理默认值列
    for to_row in to:
        #处理默认值列
        if r"\=" not in str(to_row) and len(str(to_row).split("=")) == 2:
            ft_map.update({int(to_row.split("=")[0]): "d"+to_row.split("=")[1]})
            continue
        #处理列列映射
        elif r"\:" not in to_row and len(to_row.split(":")) == 2:
            ft_map.update({int(to_row.split(":")[0]): to_row.split(":")[1]})
            continue
        #其他普通列
        else:
            to_index = 0
            for i in range(1, total + 1):
                if i not in used_row:
                    to_index = i
                    break
            ft_map.update({int(to_row): str(to_index)})
            used_row.append(to_index)

    #setp3 处理输出分隔符   outsp  0=\t,1=    0代表默认的，其他前面带列号的代表指定的
    if len(outsp) > 1 and len(outsp.split(",")) > 1:
        outsps = re.findall(r"\d=.+?", outsp)
        outsp = {}
        for outsp_kv in  outsps:
            k,v = outsp_kv.split("=")
            outsp.update({int(k): v})
    else:
        outsp = {0: outsp}

    #step4 开始处理每一行
    lines = read_file(inpath)
    f = open(outpath, "w")
    result = []
    for line in lines:
        #多个输入分隔符情况，使用正则切分成列
        if len(insp.split("|")) > 0:
            parts = re.split(insp, line)
        #否则使用正常字符串切分成列
        else:
            parts = line.split(insp)

        #正常的，切分后字段数大于等于配置的选项个数
        if len(parts) >= in_count:
            outline = one_line_proc(parts, total, ft_map, outsp, empty_fill, fill_with_sno)
            result.append(outline + "\n")
        #不正常的，列数少于配置
        else:
            #若配置了-e 输出，否则列数不符的记录过滤
            if error_line_out:
                result.append(line + "\n")

    #step5 输出结果
    f.writelines(result)
    f.close()

#特殊的处理入口，处理维度为每一行,目前只有时间处理
def handler_specal_part(part_str):
    #timestamp 时间处理
    #时间列，默认必须 TS数字=时间
    if part_str.startswith("TS") and "=" in part_str:
        ts_format = {8: "%Y%m%d",
                     10: "%Y-%m-%d",
                     14: "%Y%m%d%H%M%S",
                     19: "%Y-%m-%d %H:%M:%S"}
        to_l = 0
        #step1 确认输出的格式 TS8 TS10 TS14 TS19
        if part_str[2] != "=":
            to_l = int(part_str[2:part_str.index("=")])

        part_str = part_str.split("=")[1].strip()
        interval = 0
        #step2 存在时间+-的情况 确认加减区间
        if "+" in part_str:
            inputdate = part_str.split("+")[0].strip()
            interval = int(part_str.split("+")[1].strip())
        elif "-" in part_str:
            parts = part_str.split("-")
            if len(parts) == 2: #20101020 - XX
                inputdate = parts[0].strip()
                interval = -int(parts[1].strip())
            elif len(parts) == 3: #2010-10-20
                inputdate = part_str
            elif len(parts) == 4: #2010-10-20 - XX
                inputdate = "-".join(parts[:-1])
                interval = -int(parts[-1])
            else:
                inputdate = part_str
        else:
            inputdate = part_str.strip()
        #step3 将原始时间转为目标时间
        part_str = get_timestamp(inputdate, ts_format, interval)

        #step4 如果定义了输出格式，转换成目标格式，返回
        if to_l > 0:
            part_str = time.strftime(ts_format.get(to_l), time.localtime(int(part_str)))
    return part_str

#将时间由秒转化为目标格式
def get_timestamp(inputdate, ts_format, interval=0):
    if "now()" in inputdate:
        inputdate = time.strftime("%Y%m%d%H%M%S") 
    inputdate = inputdate.strip()
    try:
        size = len(inputdate)
        if size in ts_format:
            ts = time.strptime(inputdate, ts_format.get(size))
        else:
            print "the input date and time expression error,only allow 'YYYYmmdd[HHMMSS]' or 'YYYY-MM-DD HH:MM:SS'  "
            sys.exit(0)
    except:
        print "the input date and time expression error,only allow 'YYYYmmdd[HHMMSS]' or 'YYYY-MM-DD HH:MM:SS'  "
        sys.exit(0)
    return str(int(time.mktime(ts)) + interval)

#打印帮助信息
def help_msg():
    print("功能：原数据文件转为目标数据格式")
    print("选项:")
    print("\t -i inputfilepath  [必输，input, 原文件路径]")
    print("\t -t n              [必输，total, n为数字，目标数据总的域个数]")
    print("\t -a '1,3,4'        [必输，array, 域编号字符串，逗号分隔。指定域用原数据字段填充，未指定用'0'填充]")
    print("\t                          -a '3,5=abc,6:2'  第5列默认值abc填充,第6列使用输入的第1列填充，第3列使用输入第1列填充")
    print("\t -o outputfilepath [可选，output, 默认为 inputfilepath.dist ]")
    print("\t -F 'FS'           [可选，field Sep，原文件域分隔符，默认为\\t,支持多分隔符，eg.'\t||\|' ]")
    print("\t -P 'OFS'          [可选，out FS，输出文件的域分隔符，默认为\\t,可指定多个，多个需指定序号=分隔符,逗号分隔,默认分隔符序号0 ]")
    print("\t -f 'fill_str'     [可选，fill，未选列的填充值，默认为空 ]")
    print("\t -s                [可选，serial number,当配置时，-f无效，使用列号填充未指派的列]")
    print("\t -e                [可选，error, 源文件列切分不一致行/空行/注释等，会被直接输出，正确行按原逻辑处理]")
    sys.exit(0)

#判断某个参数必须被定义
def must_be_defined(param, map, error_info):
    if param not in map:
       print error_info
       sys.exit(1)

#程序入口，读入参数，执行
def main():
    #init default value
    insp = "\t"
    outsp = "\t"
    empty_fill = ''
    fill_with_sno = False
    error_line_out = False
    #handle options
    try:
        opts,args = getopt.getopt(sys.argv[1:],"F:P:t:a:i:o:f:hse")

        for op,value in opts:
          if op in ("-h", "-H", "--help"):
            help_msg()
          if op == "-i":
            inpath = value
          elif op == "-o":
            outpath = value
          elif op == "-t":
            total = int(value)
          elif op == "-a":
            to = value.split(",")
          elif op == "-F":
            insp = value.decode("string_escape")
          elif op == "-P":
            outsp = value.decode("string_escape")
          elif op == "-f":
            empty_fill = value
          elif op == "-s":
            fill_with_sno = True
          elif op == "-e":
            error_line_out = True
        if len(opts) < 3:
          print(sys.argv[0]+" : the amount of params must great equal than 3")
          print("Command : ./dataformat.py -h")
          sys.exit(1)

    except getopt.GetoptError:
        print(sys.argv[0]+" : params are not defined well!")
        print("Command : ./dataformat.py -h")
        sys.exit(1)

    params_map = dir()

    must_be_defined('inpath', params_map, sys.argv[0]+" : -i param is needed,input file path must define!")
    must_be_defined('total', params_map, sys.argv[0]+" : -t param is needed,the fields of result file must define!")
    must_be_defined('to', params_map, sys.argv[0]+" : -a param is needed,must assign the field to put !")

    if not os.path.exists(inpath):
        print(sys.argv[0]+" file : %s is not exists"%inpath)
        sys.exit(1)

    if 'outpath' not in dir():
        outpath = inpath+".dist"

    process(inpath, total, to, outpath, insp, outsp, empty_fill, fill_with_sno, error_line_out)

if __name__ =="__main__":
    main()
