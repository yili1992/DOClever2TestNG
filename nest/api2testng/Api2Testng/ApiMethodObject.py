# -*- coding:utf-8 -*-
import copy
import re
import time

__author__ = 'zhaoli'
from .TemplateObject import templateParseBase

def stringPretty(field):#部分字段含中文，需要去除
    pattern = re.compile('\w+')
    result = pattern.findall(field)
    return result[0]

class ApiMethodObject():
    STRING = 0
    BOOLEAN = 2
    NUMBER = 1
    ARRAY = 3
    OBJECT = 4
    MIXED = 5

    def __init__(self, template, requestData, url, author):
        self.template = template
        self.author = author
        self.date = time.strftime('%Y/%m/%d', time.localtime(time.time()))
        self.params = requestData
        self.method_url = url
        self.rest_api_flag = False
        self.args = {} #在addMethodBody中会获取args{"arg":{"type":"String","value":["111","2222"]}}
        self.methodBody = []
        self.methodName = self.getMethodName()
        self.addMethodBody()
        self.allArgs = self.getRequestArgs(self.args)

    def getMethodCode(self):
        methodCode = templateParseBase(self.template, self)
        return methodCode

    def getRequestArgs(self, args):
        result = []
        for k, v in args.items():
            result.append("{} {}".format(v["type"], k))
        return ', '.join(result)

    def getMethodName(self):
        for i in self.params:
            if i["name"] == "method":
                return i["mock"]
        else:
            self.rest_api_flag = True
            return self.method_url.split('/')[-1]

    def getStringParamBody(self, k, v, comment, must, params, arg_flag=False):
        mustStr = "必须字段" if must==1 else "非必须变量"
        if arg_flag:
            if k !=v:
                comment = comment+";"+v
                v = k
            self.methodBody.append('        {0}.put("{1}",{2});//{3};{4}\n'.format(params, k, v, mustStr, comment))
            arg_value = ";".join(comment.split(';')[1:])
            arg_dict = {"type": "String", "value": [arg_value.replace('"', '\\"')]}
            self.args[k] = arg_dict
        else:
            self.methodBody.append('        {0}.put("{1}","{2}");//{3};{4}\n'.format(params, k, v, mustStr, comment))

    def getStringParamBody2List(self, k, v, comment, must, params, arg_flag=False, arg_value=None):
        mustStr = "必须字段" if must==1 else "非必须变量"
        value = comment.split(";")[1]
        if arg_flag:
            self.methodBody.append('        {0}.add({1});//{3};{4}\n'.format(params, value, v, mustStr, comment))
            if arg_value:
                arg_dict = {"type": "String", "value": [arg_value]}
                self.args[k] = arg_dict
            else:
                arg_value = ";".join(comment.split(';')[1:])
                arg_dict = {"type": "String", "value": [arg_value.replace('"', '\\"')]}
                self.args[k] = arg_dict
        else:
            self.methodBody.append('        {0}.add("{1}");//{3};{4}\n'.format(params, value, v, mustStr, comment))

    def addListParamBody(self, parent_node, data, params):
        value_list = []
        if len(data) == 0:
            arg_dict = {"type": "List<String>", "value": value_list}
            self.args[parent_node+"List"] = arg_dict
            self.methodBody.append('        {1}.put("{0}", {2});\n'.format(parent_node, params, parent_node+"List"))
            return
        if data[0]["type"] == ApiMethodObject.STRING or data[0]["type"] == ApiMethodObject.NUMBER or data[0]["type"] == ApiMethodObject.BOOLEAN or data[0]["type"] == ApiMethodObject.MIXED:
            arg_dict = {"type": "List<String>", "value": value_list}
            self.args[parent_node+"List"] = arg_dict
        if data[0]["type"] == ApiMethodObject.ARRAY:
            self.methodBody.append("        List<JSONObject> {} = new ArrayList();\n".format(parent_node))
        if data[0]["type"] == ApiMethodObject.OBJECT:
            self.methodBody.append("        List<JSONObject> {} = new ArrayList();\n".format(parent_node))
        index = 0
        for i in data:
            if i["type"] == ApiMethodObject.STRING or i["type"] == ApiMethodObject.NUMBER or i["type"] == ApiMethodObject.BOOLEAN or i["type"] == ApiMethodObject.MIXED:
                value_list.append(i["mock"])
            if i["type"] == ApiMethodObject.ARRAY:
                self.methodBody.append("        List<JSONObject> {} = new ArrayList();\n".format(i["name"]))
                self.addListParamBody(i["name"], i["data"], parent_node)
                self.methodBody.append('        {1}.add({0});\n'.format(i["name"], parent_node))
            if i["type"] == ApiMethodObject.OBJECT:
                object_name = "{}Info{}".format(parent_node, index)
                self.methodBody.append("        JSONObject {} = new JSONObject();\n".format(object_name))
                self.getDictParamBody(object_name, i["data"])
                self.methodBody.append('        {1}.add({0});\n'.format(object_name, parent_node))
            index+=1

        if data[0]["type"] == ApiMethodObject.STRING or data[0]["type"] == ApiMethodObject.NUMBER or data[0]["type"] == ApiMethodObject.BOOLEAN or data[0]["type"] == ApiMethodObject.MIXED:
            self.methodBody.append('        {1}.put("{0}", {2});\n'.format(parent_node, params, parent_node+"List"))
        if data[0]["type"] == ApiMethodObject.ARRAY:
            self.methodBody.append('        {1}.put("{0}", {0});\n'.format(parent_node, params))
        if data[0]["type"] == ApiMethodObject.OBJECT:
            self.methodBody.append('        {1}.put("{0}", {0});\n'.format(parent_node, params))

    def getDictParamBody(self, params, v):
        for i in v:
            if i["type"] == ApiMethodObject.STRING or i["type"] == ApiMethodObject.NUMBER or i["type"] == ApiMethodObject.BOOLEAN or i["type"] == ApiMethodObject.MIXED:
                self.getStringParamBody(i["name"], i["name"], i["remark"]+";"+i["mock"], i["must"], params, True)
            if i["type"] == ApiMethodObject.ARRAY:
                self.addListParamBody(i["name"], i["data"],params)
            if i["type"] == ApiMethodObject.OBJECT:
                self.methodBody.append("        JSONObject {} = new JSONObject();\n".format(i["name"]))
                self.getDictParamBody(i["name"], i["data"])
                self.methodBody.append('        {1}.put("{0}", {0});\n'.format(i["name"], params))


    def getListParamBody(self, k, v, params):
        self.methodBody.append("        List<JSONObject> {0}=new ArrayList<>();\n".format(k))
        self.methodBody.append("        JSONObject {} = new JSONObject();\n".format("paramsInfo"))
        for i in v:
            if i["type"] == ApiMethodObject.STRING or i["type"] == ApiMethodObject.NUMBER or i["type"] == ApiMethodObject.BOOLEAN or i["type"] == ApiMethodObject.MIXED:
                self.getStringParamBody(i["name"], i["name"], i["remark"]+";"+i["mock"], i["must"], "paramsInfo", True)
            else:
                self.methodBody.append("        JSONObject {} = new JSONObject();\n".format(i["name"]))
                self.getDictParamBody(i["name"], i["data"])
                self.methodBody.append('        {1}.put("{0}", {0});\n'.format(i["name"], "paramsInfo"))

        self.methodBody.append('        {0}.add({1});\n'.format(k, "paramsInfo"))
        self.methodBody.append('        {1}.put("{0}", {0});\n'.format(k, params))

    def addMethodBody(self):
        for k in self.params:
            if 'remark' not in k.keys():
                k['remark'] = "无"
            if 'must' not in k.keys():
                k['must'] = 0
            if 'type' not in k.keys():
                self.getStringParamBody(k["name"], k["name"], k["remark"], k["must"], "jsonParams", True)
            else:
                if k["type"] == ApiMethodObject.STRING or k["type"] == ApiMethodObject.NUMBER or k["type"] == ApiMethodObject.BOOLEAN or k["type"] == ApiMethodObject.MIXED:
                    self.getStringParamBody(k["name"], k["mock"], k["remark"], k["must"], "jsonParams", self.rest_api_flag)
                if k["type"] == ApiMethodObject.ARRAY:
                    if len(k["data"]) == 0:#list中没有数据
                        self.methodBody.append("        List<JSONObject> {0}=new ArrayList<>();\n".format(k["name"]+"List"))
                        self.getStringParamBody2List(k["name"], k["name"], k["remark"]+";"+k["name"], k["must"], k["name"]+"List", True)
                        self.methodBody.append('        {1}.put("{0}", {2});\n'.format(k["name"], "jsonParams", k["name"]+"List"))
                        continue
                    if k["data"][0]["type"] == ApiMethodObject.STRING or k["data"][0]["type"] == ApiMethodObject.NUMBER or k["data"][0]["type"] == ApiMethodObject.BOOLEAN or k["data"][0]["type"] == ApiMethodObject.MIXED:
                        #if self.rest_api_flag:
                        value_list = []
                        arg_dict = {"type": "List<String>", "value": value_list}
                        for value in k["data"]:
                            value_list.append(value["mock"])
                        self.args[k["name"]+"List"] = arg_dict
                        self.methodBody.append('        {1}.put("{0}", {2});\n'.format(k["name"], "jsonParams", k["name"]+"List"))
                        # else:
                        #     self.methodBody.append("        List<String> {0}=new ArrayList<>();\n".format(k["name"]+"List"))
                        #     self.getStringParamBody2List(k["data"][0]["name"], k["data"][0]["name"], k["data"][0]["remark"]+";"+k["data"][0]["mock"], k["data"][0]["must"], k["name"]+"_list")
                        #     self.methodBody.append('        {1}.put("{0}", {2});\n'.format(k["name"], "jsonParams", k["name"]+"List"))
                    else:
                        self.getListParamBody(k["name"], k["data"][0]["data"], "jsonParams")


if __name__ == '__main__':
    print("write your testcase")