# APITesting
基于Pytest+Allure+Request接口自动化测试框架

# 目录结构
##### 依赖库
- PyYAML
- pycrypto
- pytest
- requests
- urllib3
- xlrd
##### TestCase目录 用于存放测试用例文件
##### Common目录 用于存放公共的类  
- Assert 用于断言  
- BaseData 用于获取测试文件（yaml）
- BaseRequest 接口请求的基础类  
- BaseUrl 用于生成请求url
- EmailSender 用于邮件发送,目前没有用到  
- Log 日志模块

##### Conf目录 用于存放配置文件  
- Config2 主要用于数据解析
  
##### Data目录 用于存放测试文件(yaml)  
##### Report目录 用于存放日志和测试报告
##### main.py 直接执行此文件即可执行测试用例  

# 测试报告截图
![Report](http://10.1.3.239/gitlab/qa/APITesting/blob/master/Report/%E6%B5%8B%E8%AF%95%E6%8A%A5%E5%91%8A.png "Report")

