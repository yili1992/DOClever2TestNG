__author__ = 'zhaoli'
import re

def templateParseBase(template, cls):
    result = []
    with open(template, 'r') as f:
        while True:
            line = f.readline()
            if line:
                params = regexStringLine(line)
                paramList = regexListLine(line)
                params_pretty = [x.strip('${').strip('}') for x in params]
                if params_pretty:
                    for index, var in enumerate(params_pretty):
                        param_value = getattr(cls, var)
                        line = line.replace(params[index], param_value)
                    result.append(line)
                elif paramList:
                    paramList_perrty = paramList.strip('@{').strip('}')
                    paramList_value = getattr(cls, paramList_perrty)
                    for i in paramList_value:
                        result.append(i)
                else:
                    result.append(line)
            else:
                break
    return result


def regexStringLine(line):
    pattern = re.compile('\$\{.*?\}')
    result = pattern.findall(line)
    return result


def regexListLine(line):
    pattern = re.compile('@\{.*?\}')
    result = pattern.search(line)
    if result:
        return result.group(0)
    else:
        None

if __name__ == '__main__':
    templateParseBase("ApiMethodTemplate")