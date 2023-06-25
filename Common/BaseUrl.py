"""
Create by：peiyaojun
Create time：2021-04-28
"""
import os
import yaml
from Conf.EnvHost_Conf import HOST_YAML_PATH
from Common.BaseOS import BaseOS


class BaseUrl:
    """
    提供请求url生成的类
    调用 get_path(self, app, testcase_path）获取
    """

    # def create_url(self, api, testcase_path, env='QA'):
    #     """
    #     通过test case文件路径、产品、环境、测试api 自动拼接出请求url
    #     :param api: XXX_EnvHost.yaml 中存在的接口名
    #     :param testcase_path: 传递TestCase 文件路径
    #     :param env: 默认值"QA"，可传参：QA（测试环境）、PROD（线上环境）、DEV（开发环境）
    #     :return: 返回拼接完整的request url
    #     """
    #     app = self.get_app(testcase_path)   # 此时只能传入 testcase_path
    #     return self.get_host(app, api, env)+"/"+self.get_path(app, testcase_path).replace("//","/")

    def get_app(self):
        """
        通过config.yaml 获取当前app
        :return: 当前app name
        """
        with open(os.path.join(BaseOS().get_project_path(), "Conf", "Config.yaml")) as f:
            return yaml.safe_load(f)["APP"]

    def get_host(self, host, env='QA'):
        """
        从EnvHost_Conf.py中根据的app，获取对应的XXX_EnvHost.yaml路径，通过api，env，获取到request url的host
        :param app: 工程中TestCase目录下的产品名称，如C360_iOS，可通过get_app(file_path)获取
        :param host: XXX_EnvHost.yaml 中存在的接口名
        :param env: 默认值"QA";可传参：QA（测试环境）、PROD（线上环境）、DEV（开发环境）
        :return: 返回requst url 的host
        """

        # conf_path = os.path.realpath(__file__)
        conf_path = os.path.join(BaseOS().get_project_path(), "Conf", HOST_YAML_PATH[self.get_app()])
        with open(conf_path, 'r', encoding="utf-8") as f:
            host = yaml.safe_load(f)[env][host]
            return host

    def get_path(self, app, testcase_path):
        """
        依据TestCase文件路径截取 request url的 path；TestCase目录下的路径结构需与请求url相同
        :param app: 产品名称，如C360_iOS
        :param testcase_path: TestCase中 .py文件路径，通过os.path.realpath(__file__)传递进来
        :return 返回request url中 path
        """
        dirname = testcase_path.split(".")[0].split(os.path.sep)
        path = ''

        for i in dirname[dirname.index(app) + 2:]:
            path = os.path.join(path, i)
        return path
