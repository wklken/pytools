#!/usr/bin/python
# -*- coding=utf-8 -*-
# author : wklken@yeah.net
# date: 2012-05-25
# version: 0.1
import os,sys,getopt

#py 2.7
#from xml.etree.ElementTree import ElementTree,Element

#py 2.4
import elementtree
from elementtree.ElementTree import ElementTree
from elementtree.ElementTree import Element

def read_xml(in_path):
    '''读取并解析xml文件
       in_path: xml路径
       return: ElementTree'''
    #tree = ElementTree()
    #tree.parse(in_path)
    f = open(in_path)
    tree = elementtree.ElementTree.fromstring(f.read().replace('"	"','"&#x9;"'))
    f.close()
    return tree

def write_xml(tree, out_path):
    '''将xml文件写出
       tree: xml树
       out_path: 写出路径'''
    f = open(out_path,"w")
    f.write(elementtree.ElementTree.tostring(tree))
    f.close()
    #tree.write(out_path, encoding="utf-8")#,xml_declaration=True)

def if_match(node, kv_map):
    '''判断某个节点是否包含所有传入参数属性
       node: 节点
       kv_map: 属性及属性值组成的map'''
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

#---------------search -----

def find_nodes(tree, path):
    '''查找某个路径匹配的所有节点
       tree: xml树
       path: 节点路径'''
    return tree.findall(path)


def get_node_by_keyvalue(nodelist, kv_map):
    '''根据属性及属性值定位符合的节点，返回节点
       nodelist: 节点列表
       kv_map: 匹配属性及属性值map'''
    result_nodes = []
    for node in nodelist:
        if if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes

#---------------change -----

def change_node_properties(nodelist, kv_map, is_delete=False):
    '''修改/增加 /删除 节点的属性及属性值
       nodelist: 节点列表
       kv_map:属性及属性值map'''
    for node in nodelist:
        for key in kv_map:
            if is_delete: 
                if key in node.attrib:
                    del node.attrib[key]
            else:
                node.set(key, kv_map.get(key))
            
def change_node_text(nodelist, text, is_add=False, is_delete=False):
    '''改变/增加/删除一个节点的文本
       nodelist:节点列表
       text : 更新后的文本'''
    for node in nodelist:
        if is_add:
            node.text += text
        elif is_delete:
            node.text = ""
        else:
            node.text = text
            
def create_node(tag, property_map, content):
    '''新造一个节点
       tag:节点标签
       property_map:属性及属性值map
       content: 节点闭合标签里的文本内容
       return 新节点'''
    element = Element(tag, property_map)
    element.text = content
    return element
        
def add_child_node(nodelist, element):
    '''给一个节点添加子节点
       nodelist: 节点列表
       element: 子节点'''
    for node in nodelist:
        node.append(element)
        
def del_node_by_tagkeyvalue(nodelist, tag, kv_map):
    '''同过属性及属性值定位一个节点，并删除之
       nodelist: 父节点列表
       tag:子节点标签
       kv_map: 属性及属性值列表'''
    for parent_node in nodelist:
        children = parent_node.getchildren()
        for child in children:
            if child.tag == tag and if_match(child, kv_map):
                parent_node.remove(child)

def trans_to_map(exp):
    result_map = {}
    parts = exp.split(",")
    for part in parts:
        kv = part.split("=")
        result_map.update({kv[0]: kv[1]})
    return result_map

def handler_cmd(tree, cmd):
    '''Node_operation:  N|a|path|a=1,b=2|[pyTag=,pyText=t1,p1=v1,p2=v2]
                        N|d|path|a=1,b=2|[pyTag=]
       propertity_operation: P|a/c/d|path|a=1,b=2,c=3|a=2,b=3,d=3
       text_operation: T|a/c/d|path|a=1|text=afdfsd'''
    parts = cmd.split(r"|")
    path = parts[2]
    identity_map = trans_to_map(parts[3])
    nodes = find_nodes(tree, path)
    result_nodes = get_node_by_keyvalue(nodes, identity_map)
    
    if parts[0] == "N":  #node operation 节点操作
        if parts[1] == "a":
            new_node_map = trans_to_map(parts[4])
            if "pyTag" in new_node_map and "pyText" in new_node_map:
                prop_map = {}
                for key in new_node_map:
                    if key != "pyTag" and key != "pyText":
                        prop_map.update(key, new_node_map.get(key))
                a = create_node(new_node_map.get("pyTag"), prop_map, new_node_map.get("pyText"))
                add_child_node(result_nodes, a)
                
        elif parts[1] == "d":
            del_node_by_tagkeyvalue(nodes, trans_to_map(parts[4]).get("pyTag"), identity_map)
            
    elif parts[0] == "P":  #property operation 属性操作
        if parts[1] == "a" or parts[1] == "c":
            new_property_map = trans_to_map(parts[4])
            change_node_properties(result_nodes, new_property_map)

        elif parts[1] == "d":
            del_property_map = trans_to_map(parts[4])
            change_node_properties(result_nodes, del_property_map, True)
        
    elif parts[0] == "T":  #text operation #文本操作
        if parts[1] == "a":
            a_text = trans_to_map(parts[4])
            change_node_text(result_nodes, a_text, is_add=True)
        elif parts[1] == "c":
            c_text = trans_to_map(parts[4])
            change_node_text(result_nodes, a_text)
        elif parts[1] == "d":
            change_node_text(result_nodes, a_text, is_delete=True)

def test():
    #1. 读取xml文件
    tree = read_xml("./test.xml")
    
    #2. 属性修改
      #A. 找到父节点
    nodes = find_nodes(tree, "processers/processer")
      #B. 通过属性准确定位子节点
    result_nodes = get_node_by_keyvalue(nodes, {"name":"BProcesser"})
      #C. 修改节点属性
    change_node_properties(result_nodes, {"age": "1"})
      #D. 删除节点属性
    change_node_properties(result_nodes, {"value":""}, True)
    
    #3. 节点修改
      #A.新建节点
    a = create_node("person", {"age":"15","money":"200000"}, "this is the firest content")
      #B.插入到父节点之下
    add_child_node(result_nodes, a)
    
    #4. 删除节点
       #定位父节点
    del_parent_nodes = find_nodes(tree, "processers/services/service")
       #准确定位子节点并删除之
    del_node_by_tagkeyvalue(del_parent_nodes, "chain", {"sequency" : "chain1"})
    
    #5. 修改节点文本
       #定位节点
    text_nodes = get_node_by_keyvalue(find_nodes(tree, "processers/services/service/chain"), {"sequency":"chain3"})
    change_node_text(text_nodes, "new text")
    
    #6. 输出到结果文件
    write_xml(tree, "./out.xml")                        

def help_msg():
    print """
      cmd_format:

         Node_operation:       N|a|path|a=1,b=2|[pyTag=,pyText=t1,a=v1,b=v2]
         propertity_operation: P|a/c/d|path|a=1,b=2,c=3|a=2,b=3,d=3
         text_operation:       T|a/c/d|path|a=1|text=afdfsd"""
    sys.exit(0)

if __name__ == "__main__":
    #test()
    #sys.exit(0)
    '''
      cmd_format:
         Node_operation:       N|a|path|a=1,b=2|[pyTag=,pyText=t1,a=v1,b=v2]
                               N|d|path|a=1,b=2|[pyTag=]
         propertity_operation: P|a/c/d|path|a=1,b=2,c=3|a=2,b=3,d=3
         text_operation:       T|a/c/d|path|a=1|text=afdfsd
      the problem is how to figure out multi-cmd
      condition is:
         i want to change property also ,i want to change some other nodes,
         add new node,properties or text
         how to figure out that?
         which type of format is better?
    '''
    
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:o:c:h")

        for op,value in opts:
          if op in ("-h", "-H", "--help"):
            help_msg()
          if op == "-i":
            inpath = value
          elif op == "-o":
            outpath = value
          elif op == "-c":
            cmd_str = value
        if len(opts) < 3:
          print(sys.argv[0]+" : the amount of params must great equal than 3")
          print("Command : ./xml_op.py -h")
          sys.exit(1)

    except getopt.GetoptError:
      print(sys.argv[0]+" : params are not defined well!")
      print("Command : ./xml_op.py -h")
      sys.exit(1)
      
    if 'inpath' not in dir():
      print(sys.argv[0]+" : -i param is needed,input file path must define!")
      sys.exit(1)
    if 'outpath' not in dir():
      print(sys.argv[0]+" : -o param is needed,input file path must define!")
      sys.exit(1)
    if 'cmd_str' not in dir():
      print(sys.argv[0]+" : -c param is needed,input file path must define!")
      sys.exit(1)
    
    cmds = cmd_str.split("#")
    tree = read_xml(inpath)
    for cmd in cmds:
        handler_cmd(tree, cmd)
    
    write_xml(tree, outpath)   
 
