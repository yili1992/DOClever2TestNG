# -*- coding:utf-8 -*-
import time
from .ApiClassFileObject import ClassFileObject
from .ApiMethodObject import ApiMethodObject
from .TemplateObject import templateParseBase

__author__ = 'zhaoli'

class CaseFileObject():
    def __init__(self, template, classpath, classname, methodname, package, description, rawArgs, group, author, return_code_path, data_provider, data_template):
        self.template = template
        # 变量 for template
        self.casePath = self.getCasePath(package)
        self.classFile = classpath+'.'+classname
        self.description = description
        self.methodName = methodname
        self.caseName = self.getCaseName()
        self.className = classname
        self.args = self.getArgs(rawArgs)
        self.group = self.get_group(group)
        self.date = self.date = time.strftime('%Y/%m/%d', time.localtime(time.time()))
        self.args_declare = self.getArgsDeclare(rawArgs)
        self.args_defined = self.getArgsDefined(rawArgs)
        self.author = author
        self.assertContent = self.getAssertContent(return_code_path)
        self.dataProviderCase = self.getDataProviderCase(data_provider, rawArgs, return_code_path, data_template)

    def getDataProviderCase(self, flag, raw_args, return_code_path, data_template):
        result = []
        if flag:
            CaseFileObject.assertExpectCodeContent = self.getAssertContent(return_code_path, "expectCode")
            for k, v in raw_args.items():
                if v["type"] == "List<String>":
                    continue
                else:
                    CaseFileObject.arg = k
                    result.extend(templateParseBase(data_template, self))
            return result
        else:
            return result

    def getAssertContent(self, path, expect_code="00000"):
        if len(path) == 0:
            if expect_code == "00000":
                return 'res1.getJSONObject(1).getJSONObject("result").getString("code"),"00000"'
            else:
                return 'res1.getJSONObject(1).getJSONObject("result").getString("code"),{}'.format(expect_code)
        else:
            result = "res1.getJSONObject(1)"
            for i in path:
                if i == "code":
                    result = result + '.getString("code")'.format(i)
                    break
                else:
                    result = result + '.getJSONObject("{}")'.format(i)
            if "00000" != path[-1] or '0' != [-1]:
                if expect_code == "00000":
                    path[-1] = "00000"
                    return result + ',"{}"'.format(path[-1])
                else:
                    return result + ',{}'.format(expect_code)


    def getArgs(self, raw):
        args = [x for x in raw.keys() if x]
        return ', '.join(args)

    def get_group(self, raw):
        raw = raw.replace("，", ",")
        str_group = '","'.join(raw.split(','))
        return '"'+str_group+'"'

    def getArgsDeclare(self, rawArgs):
        content = []
        for k, v in rawArgs.items():
            content.append("    public static {} {};\n".format(v["type"], k))
        return content

    def getArgsDefined(self, rawArgs):
        content = []
        for k, v in rawArgs.items():
            if v["type"]=="String":
                content.append('        {} = "{}";\n'.format(k, v["value"][0]))
            if v["type"]=="List<String>":
                content.append('        {} = new ArrayList();\n'.format(k))
                for value in v["value"]:
                    content.append('        {}.add("{}");\n'.format(k, value))
        return content

    def getCaseResutl(self):
        caseCode = templateParseBase(self.template, self)
        return caseCode

    def getCasePath(self, package):
        sub_name = package.split('.')
        if sub_name.count('class') > 0:#java中class不能作为文件夹,需要转换
            sub_name[sub_name.index('class')] = 'lclass'
        transPackage  = '.'.join(sub_name)
        return transPackage

    def getCaseName(self):
        cap = self.methodName[0].upper()
        return 'Test'+cap+self.methodName[1:]

if __name__ == '__main__':
    print("write your testcase")