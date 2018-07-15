# -*- coding:utf-8 -*-
import time
import re
from .ApiMethodObject import ApiMethodObject
from .TemplateObject import templateParseBase


__author__ = 'zhaoli'


class ClassFileObject():
    def __init__(self, template, packageLink, author, base_url):
        self.template = template
        # 变量 for template
        self.packageLink = packageLink
        self.packageName = packageLink.split('/')[-1]
        self.packagePath = self.getPackagePath()
        self.staticMethod = ["import com.lee.test.tool.HttpHelper;"]
        self.className = self.getClassName()
        self.ApiMethods = []
        self.date = time.strftime('%Y/%m/%d', time.localtime(time.time()))
        self.author = author
        self.base_url = self.getBaseUrl(base_url)


    def getBaseUrl(self, base_url):
        if base_url == '':
            return "ConfigModel.jsonrpc_url"
        else:
            pattern = r'^[0-9.:]*'
            result = re.match(pattern, base_url)
            if result.group(0):
                return '"http://'+base_url+'"'
            if "ConfigModel" in base_url:
                return base_url
            if '_url' in base_url:
                return "ConfigModel."+base_url
            return '"'+base_url+'"'

    def getCodeResutl(self):
        classCode = templateParseBase(self.template, self)
        return classCode

    def addMethod(self,methodCode):
        self.ApiMethods.extend(methodCode)

    def getPackagePath(self):
        if '.' not in self.packageName:
            self.packageName = '.'.join(self.packageLink.split('/')[1:])
        sub_name = self.packageName.split('.')
        if sub_name.count('class') > 0:#java中class不能作为文件夹,需要转换
            sub_name[sub_name.index('class')] = 'lclass'
        transPackage  = '.'.join(sub_name)
        return transPackage

    def getClassName(self):
        suffix = self.packageName.split('.')[-1]
        if suffix[-3:] == 'Api':
            return suffix
        else:
            return suffix + 'Api'


if __name__ == '__main__':
    print("write your testcase")