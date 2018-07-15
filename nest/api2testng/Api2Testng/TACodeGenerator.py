# -*- coding:utf-8 -*-
import json
import os
from .ApiCaseFileObject import CaseFileObject
from .ApiClassFileObject import ClassFileObject
from .ApiMethodObject import ApiMethodObject
import argparse
import re

METHOD_TEMPLATE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ApiMethodTemplate')
CLASS_TEMPLATE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ApiClassTemplate')
CASE_TEMPLATE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ApiCaseTemplate')
DATAPROVIDER_TEMPLATE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ApiDataProviderCaseTemplate')


def generateTACode(interface_path, group, destination, author, CLASS_FILE_DICT, FAILED_LIST, base_url, data_provider):
    with open(interface_path, 'rb') as f:
        content = f.read()
        interface_json = json.loads(content)
        for i in interface_json["data"]:
            #print(i["name"])
            if i["name"] == u"#回收站":
                continue
            if len(i["data"]) == 0:
                continue
            recursion_found_interface(i, group, destination, author, CLASS_FILE_DICT, FAILED_LIST, base_url, data_provider)


def recursion_found_interface(data, group, destination, author, CLASS_FILE_DICT, FAILED_LIST, base_url, data_provider):
    if 'type' not in data.keys():
        requestData = data["param"][0]["bodyInfo"]
        if 'remark' not in data:
            description = data["name"]
        else:
            description = data["name"]+'-'+data["remark"]
        url = data["url"]
        pattern = r'http://[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*:[0-9]*'
        result = re.match(pattern, url)
        if result:
            url = url.replace(result.group(0), '')
        pattern = r'\{\{\w*\}\}'
        result = re.match(pattern, url)
        if result:
            url = url.replace(result.group(0), '')
        if url[0] != '/':
            url = '/' + url
        try:
            return_code_path = []
            getResponseCodePath(data["param"][0]["outParam"], return_code_path)
            if 'rawJSON' in requestData.keys():
                api_methond = ApiMethodObject(METHOD_TEMPLATE, requestData["rawJSON"], url, author)
            else:
                api_methond = ApiMethodObject(METHOD_TEMPLATE, data["param"][0]["queryParam"], url, author)
            if url not in CLASS_FILE_DICT.keys():
                CLASS_FILE_DICT[url] = ClassFileObject(CLASS_TEMPLATE, data['url'], author, base_url)
            CLASS_FILE_DICT[url].addMethod(api_methond.getMethodCode())
            caseInstance = CaseFileObject(CASE_TEMPLATE, CLASS_FILE_DICT[url].packagePath,
                                          CLASS_FILE_DICT[url].className, api_methond.methodName,
                                          CLASS_FILE_DICT[url].packageName, description,
                                          api_methond.args, group, author, return_code_path, data_provider, DATAPROVIDER_TEMPLATE)
            createCaseFile(caseInstance, destination)
        except Exception as e:
            FAILED_LIST[data['name']] = str(e)
    else:
        for v in data["data"]:
            if len(v) == 0:
                continue
            #print(v["name"])
            recursion_found_interface(v, group, destination, author, CLASS_FILE_DICT, FAILED_LIST, base_url, data_provider)


def createCaseFile(case_info, destination):
    case_dir = case_info.casePath.replace('.', os.sep)
    case_dir = os.path.join(destination, case_dir)
    if os.path.exists(case_dir) != True:
        os.makedirs(case_dir)
    fileName = case_info.caseName + '.java'
    caseFile = os.path.join(case_dir, fileName)
    #print(caseFile)
    with open(caseFile, 'w') as f:
        for line in case_info.getCaseResutl():
            f.write(line)

def getResponseCodePath(content, outPath=[]):
    for i in content:
        if i["name"] == "code":
            outPath.append("code")
            outPath.append(i["mock"])
            return True
        if "data" in i:
            if i["name"]:
                outPath.append(i["name"])
            if getResponseCodePath(i["data"], outPath):
                return True
    else:
        return False

def createJavaFile(destination, CLASS_FILE_DICT):
    for api_class in CLASS_FILE_DICT.values():
        file_dir = api_class.packagePath.replace('.', os.sep)
        file_dir = os.path.join(destination, file_dir)
        if os.path.exists(file_dir) != True:
            os.makedirs(file_dir)
        fileName = api_class.className + '.java'
        javaFile = os.path.join(file_dir, fileName)
        with open(javaFile, 'w') as f:
            for line in api_class.getCodeResutl():
                f.write(line)


def test_main():
    generateTACode()


def transfer2code(group, interface, destination, author, base_url, data_provider):
    CLASS_FILE_DICT = {}
    FAILED_LIST = {}
    generateTACode(interface, group, destination, author, CLASS_FILE_DICT, FAILED_LIST, base_url, data_provider)
    createJavaFile(destination, CLASS_FILE_DICT)
    return FAILED_LIST


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", help="测试用例Group分类，多个类目用','分割 例如: 团课,智能排课")
    parser.add_argument("-i", "--interface", help="接口json文件路径")
    parser.add_argument("-d", "--destination", help="代码产生的目标目录")
    parser.add_argument("-a", "--author", help="作者")
    args = parser.parse_args()
    if not args.group:
        raise Exception("使用 -g, 来设置测试用例Group分类，多个类目用','分割 例如: 团课,智能排课")
    if not args.interface:
        raise Exception("使用 -i, 来设置接口json文件路径")
    if not args.destination:
        raise Exception("使用 -d, 来设置代码产生的目标目录")
    if not args.author:
        raise Exception("使用 -a, 来设置作者")
    transfer2code(args.group, args.interface, args.destination, args.author, "www.api.com", False)
