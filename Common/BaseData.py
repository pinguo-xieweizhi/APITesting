"""
Create by: peiyaojun
Create time: 2021.04.28
"""
import os
from Common.BaseOS import BaseOS
import yaml


class BaseData:
    """
    对于Data目录的一些操作

    casepath_to_datapath(self, path, app)：将TestCase 目录路径转化相应的Data目录路径
    get_data_path(self, testcase_path)：通过testcase的路径获取 测试用例yaml文件绝对路径

    """

    def casepath_to_datapath(self, path, app):
        """
        将TestCase 目录路径转化相应的Data目录路径
        :param path:需要转化的路径
        :param app: 识别到TestCase 的索引（区分不同产品），便于替换掉TestCase
        :return: 转换后的路径
        """
        """
        将TestCase 文件路径转化相应的 Data路径
        """
        list_path = BaseOS().path_list(path)
        list_path[list_path.index(app) - 1] = "Data"
        data_path = os.path.sep.join(list_path)
        return data_path

    def datapath_to_casepath(self, path, app):
        """
        将TestCase 目录路径转化相应的Data目录路径
        :param path:需要转化的路径
        :param app: 识别到TestCase 的索引（区分不同产品），便于替换掉TestCase
        :return: 转换后的路径
        """
        """
        将TestCase 文件路径转化相应的 Data路径
        """
        list_path = BaseOS().path_list(path)
        list_path[list_path.index(app) - 1] = "TestCase"
        data_path = os.path.sep.join(list_path)
        return data_path

    def get_data_path(self, testcase_path):
        """
        通过testcase的路径获取到 测试用例 yaml文件绝对路径
        yaml文件所在的路径与testcase的路径结构需一致
        :param testcase_path: testcase 文件路径
        :return: 返回测试数据 yaml文件绝对路径
        """

        # 获取当前app 名称
        with open(os.path.join(BaseOS().get_project_path(),"Conf","Config.yaml")) as f:
            app = yaml.safe_load(f)["APP"]

        # 转化为Data目录
        data_dir = self.casepath_to_datapath(testcase_path, app)
        data_dir_list = BaseOS().path_list(data_dir)

        # 将.py 修改为需要使用的.yaml 格式
        filename, type = os.path.splitext(data_dir_list[-1])
        data_dir_list[-1] = filename+".yaml"

        return os.path.sep.join(data_dir_list)
