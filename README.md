# DOClever2TestNG
- 根据DOClever 接口文档Json文件 生成TestNG 接口测试代码
- template模板文件中的${变量} 为String 类型来源于相应处理文件的类成员变量, @{变量}为List类型 其数据内容会进行for 循环处理

# 安装说明
使用python3
`
pip install -r requirements.txt
`

启动应用
`
python application
`
进入http://127.0.0.1:5000/api2testng/#/

# 文件说明
 - ApiCaseFileObject :处理生成API Case文件
 - ApiCaseTemplate ：API Case模板文件
 - ApiClassFileObject ：处理生成API Class文件
 - ApiClassTemplate ：API Class模板文件
 - ApiMethodObject ： 处理生成API 接口Method文件
 - ApiMethodTemplate API 接口Method模板文件
 - TACodeGenerator ：代码生成主进程
 - TemplateMethod ：template 解析文件
