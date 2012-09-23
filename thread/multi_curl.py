#!/usr/bin/python

import commands
import threading


#f_r = 'curl -s "localhost:2089'
f_r = 'curl -s "localhost:2089'
#f = open("test_request")
f = open("test_request_new")
# f_r + f中一行  + "   =   执行的curl命令 ,根据需求改

dir_path = "./new/"
#dir_path="./old/"
#线程数
thread_count = 50

#一次性读入内存，超过百万慎用
lines = f.readlines()


def curl_function(i, the_lines):
    fi = open(dir_path + str(i) + ".result", "w")
    print "size:", len(the_lines)
    print "begin"
    count = 0
    for line in the_lines:
        cmd = f_r + line.strip() + '"'

        #返回至
        back = commands.getoutput(cmd)
        count += 1
        if count % 1000 == 0:
            print "%s finish: %s" % (i, 1000)

        if len(back) > 0:
            fi.write(back)
            #do something with back
            pass
    print "end"
    fi.close()
    return


size = len(lines) / thread_count


thead_list = []
for i in range(0, thread_count):
    th = threading.Thread(target=curl_function, args=(i, lines[i * size:(i + 1) * size]))
    print "start_no: ", i
    print "handle range:", i * size, (i + 1) * size
    th.start()
    thead_list.append(th)

for th in thead_list:
    print "join_no: ", i
    th.join()
