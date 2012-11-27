#!/bin/env python
#-*- coding:utf-8 -*-
#@Author: wklken
#@Mail: wklken@yeah.net ,lingyue.wkl@taobao.com
#@Date: 20120706
#@Version: 0.1  sh -n, check for static syntax
#          0.2  sh -vx, color the output log which i care about
#          0.2.1 rebuild all functions , lines  200+ -> 120
#          0.2.2 refine the re pattern.
#          0.2.3 add sh params support. fix bug and add re patterns
#          0.2.5 add warn/error pattern and collect the result
#          0.2.6 use decorator to refine print, refine collect method
#          0.2.7 last version edited by lingyue.wkl
#                this py: https://github.com/wklken/pytools/tree/master/shell

#@Desc: Quick test shell script.The target is hacking into it and get all the status i need.
#TODO: need to keep source code in 200 lines! refine!

import sys,os
import commands
import re

#color defined
COLOR_NONE = "C_NONE"
COLOR_GREEN = "C_G"
COLOR_RED = "C_R"
COLOR_YELLOW = "C_Y"
COLOR_PURPLE = "C_P"
COLOR_BLUE = "C_B"

COLOR_MAP = {COLOR_NONE : "\033[m",
             COLOR_GREEN : "\033[01;32m",
             COLOR_RED : "\033[01;31m",
             COLOR_YELLOW : "\033[01;33m",
             COLOR_PURPLE : "\033[01;35m",
             COLOR_BLUE : "\033[01;34m",
             None:"\033[m" }

#the command used defined
SH_N = "sh -n "
SH_X = "sh -vx "
LOG_BEGIN = "export PS4='+${BASH_SOURCE}|${LINENO}|${FUNCNAME[0]} -> ';"
LOG_BEGIN = ""

#the type of output log line
LINE_TYPE_CMD = "CMD"
LINE_TYPE_EXC = "EXC"
LINE_TYPE_CMT = "CMT"

CMD_Y = COLOR_MAP.get(COLOR_YELLOW) + "CMD: " + COLOR_MAP.get(COLOR_NONE)

#----------pattern used to match begin -----------------------------
#0. special
PATTERN_ADDSIGN = re.compile("(^\++)")

#1. execute command log match pattern
exc_mark_pattern = [(r"([\[\]])", COLOR_YELLOW), #for condition testing   must be the first one
                    (r"(([12]\d{3})(1[12]|0[1-9])(0[1-9]|1\d|2\d|3[01]))",COLOR_PURPLE), #date yyyyMMDD
                    (r"(tbsc-dev)", COLOR_RED),  # path: tbsc-dev
                    (r"([a-zA-Z_][a-zA-Z0-9_]*=[\s|\"\"]*)$",COLOR_RED),   # params=None
                    (r"(exit\s+-?\d*|return\s+-?\d*)",COLOR_BLUE), #exit status
                    (r"(\s(\-[acbdefgnorsuwxzL]|\-(lt|le|gt|ge|eq|ne))\s)", COLOR_YELLOW),
                    (r"((\s(=|==|<=|>=|\+=|<|>|'!='|\&\&)\s)|'!')", COLOR_YELLOW),
                    (r"(\s(\-input|\-output|\-i|\-o)\s)", COLOR_YELLOW),
                    ]
EXC_MARK_PATTERN = [(re.compile(s), color) for s, color in exc_mark_pattern]

#2. error/warn result log match pattern
# 100% error
error_mark_pattern = [(r"(No such file or directory|command not found|unknown option|invalid option)",COLOR_RED), #result -> file not found
                    (r"(unary operator expected)", COLOR_RED), # test failed
                    (r"(Permission denied)", COLOR_RED),
                    (r"(syntax error|unexpected|read error)", COLOR_RED),
                    (r"(sed: -e expression)",COLOR_RED),  # sed 的一些错误
                    (r"(java.io.FileNotFoundException|org.apache.hadoop.mapred.InvalidInputException|java.lang.IllegalMonitorStateException)", COLOR_RED),#javaerror
                    ]
ERROR_MARK_PATTERN = [(re.compile(s), color) for s, color in error_mark_pattern]

# may be not error ,just warn,notice
warn_mark_pattern = []

WARN_MARK_PATTERN = [(re.compile(s), color) for s, color in warn_mark_pattern]

#3. command log match pattern
cmd_mark_pattern = error_mark_pattern + warn_mark_pattern + \
                    [
                    (r"(line \d+)", COLOR_RED),  #error report the line No
                    (r"(\$(\{\w+\}))", COLOR_PURPLE),
                    (r"(\.\.)", COLOR_PURPLE), #相对路径
                    (r"((?<!-)\b(\w+)\b=)", COLOR_YELLOW),
                    (r"(\$(\w+))", COLOR_PURPLE), #变量名
                    (r"(\w+\.sh\s*)", COLOR_GREEN), #*.sh
                    (r"(`)", COLOR_GREEN),  # ``
                    (r"(\s?\w+\s*\(\))", COLOR_GREEN), #function()
                    (r"(\{\s*$|^\}\s*$)", COLOR_GREEN), # function {}
                    (r"(^export\s|^source\s)", COLOR_YELLOW),
                    (r"(\|)", COLOR_GREEN),
                    (r"(<<|>>|<|>)", COLOR_YELLOW),
                    ]
CMD_MARK_PATTERN = [(re.compile(s), color) for s, color in cmd_mark_pattern]
#----------pattern used to match end -----------------------------

#static params defined
error_lines = []

#functions begin
def str_coloring(str_info, color=COLOR_NONE):
    """color str"""
    return COLOR_MAP.get(color, COLOR_MAP.get(None)) + str_info + COLOR_MAP.get(COLOR_NONE)


def print_symbol(str_info):
    """print the symbol"""
    print "=" * 20 + " " + str_info + " " + "=" * 20


def wrap_print_func(arg):
    """wrap func, print begin and end sign"""
    def  newfunc(func):
        def newfunc_withparams(*args, **kwargs):
            print_symbol(arg + " BEGIN")
            func(*args, **kwargs)
            print_symbol(arg + " END")
        return newfunc_withparams
    return newfunc


@wrap_print_func("STATIC SYNTAX")
def static_syntax_check(file_path):
    """use sh -n to Check the static syntax"""
    cmd = SH_N + file_path
    result = commands.getoutput(cmd)
    if result:
        print "script syntax check:" + str_coloring(" FAILED", COLOR_RED)
        print str_coloring(result, COLOR_RED)
    else:
        print "script syntax check:" + str_coloring(" PASS", COLOR_GREEN)


def pre_handler(result):
    """pre handle the result lines """
    pass


@wrap_print_func("PROCESS LOG CHECK")
def dynamic_log_process(file_path, params):
    """run shell, and get the process log , and pass it to process function"""
    cmd = LOG_BEGIN + SH_X + file_path + " " + params
    result = commands.getoutput(cmd)
    pre_handler(result)
    process_line(result)


def cmd_type(line):
    """return the type of line,and can do something with it
       + execute cmd line     # comment line    others: normal commend line
    """
    if line.startswith("+"):
        return LINE_TYPE_EXC, line
    elif line.lstrip().startswith("#"):
        return LINE_TYPE_CMT, line
    else:
        #return LINE_TYPE_CMD, CMD_Y + line
        return LINE_TYPE_CMD, line


def mark_sign_by_pattern(line, line_type=LINE_TYPE_EXC):
    """mark the str by pattern"""
    #can't use in py2.4,ni mei a
    #use_pattern = EXC_MARK_PATTERN if line_type == LINE_TYPE_EXC else CMD_MARK_PATTERN
    if line_type == LINE_TYPE_EXC:
        use_pattern = EXC_MARK_PATTERN
    else:
        use_pattern = CMD_MARK_PATTERN
    native_line = line
    for pt, color in use_pattern:
        m = pt.findall(line)
        if m:
            line = pt.sub(COLOR_MAP.get(color) + r"\1" + COLOR_MAP.get(COLOR_NONE), line)
    for pt, color in ERROR_MARK_PATTERN:
        e = pt.findall(native_line)
        if e:
            error_lines.append(line)
    return line


def process_line(result):
    """format each line.With the pattern"""
    lines = result.split("\n")
    for line in lines:
        line_type, line = cmd_type(line)

        if line_type == LINE_TYPE_EXC:
            result = mark_sign_by_pattern(line, line_type)
            print PATTERN_ADDSIGN.sub(COLOR_MAP.get(COLOR_GREEN) + r"\1" + COLOR_MAP.get(COLOR_NONE), result)
        elif line_type == LINE_TYPE_CMD:
            print mark_sign_by_pattern(line, line_type)
        elif line_type == LINE_TYPE_CMT:
            print line

@wrap_print_func("RESULT COLLECT")
def warn_error_collect(collect_list, collect_type="ERROR"):
    """collect the warning and error info in the end"""
    print str_coloring("RESULT TYPE: " + collect_type, COLOR_GREEN)
    if len(collect_list):
        print str_coloring(collect_type + " FOUND: ", COLOR_RED) + str_coloring(str(len(collect_list)), COLOR_YELLOW)
        for line in collect_list:
            print line
    else:
        print str_coloring("NO " + collect_type + " FOUND", COLOR_GREEN)

if __name__ == "__main__":
    args = sys.argv[1:]
    sh_name = args[0]
    params = " ".join(args[1:])
    
    #step1 : sh -n ,  check the syntax 
    static_syntax_check(sh_name)
    
    #step2 : sh -x ,  check the dynamic log
    dynamic_log_process(sh_name, params)
    
    #step3 : collect the warnings and errors
    warn_error_collect(error_lines, "ERROR")
