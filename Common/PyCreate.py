import xlrd
import os
from Common.BaseData import BaseData
from Common.BaseOS import BaseOS
import shutil


class PyCreate:
    """
    通过mod.xls文件用于生成可执行的，testcase 目录下的.py文件（此方式生成的文件与Conf目录下的，template.py文件完全一致）
    """

    def create_py(self, mod_xls_list, app):
        # 获取需要在TestCase目录下生成的文件夹、py文件list
        dir_list, py_path_list = self.get_dir_py_list(mod_xls_list, app)

        # 生成py文件根目录
        BaseOS().create_dirs(dir_list)

        # 给创建的根目录中添加__init__.py文件
        self.generate__init__py(dir_list)

        # 生成 py文件（当已存在时不生成，若不存在时生成）
        return self.generate_py(py_path_list)

    def get_xls_sheets(self, xls_path):
        data = xlrd.open_workbook(xls_path)
        tables = data.sheet_names()
        data = None
        return tables

    def get_dir_py_list(self, mod_xls_list, app):
        dir_list = []
        py_path_list = []
        bd = BaseData()
        for i in mod_xls_list:
            path, mod_xls_name = os.path.split(i)
            mod_xls_name = mod_xls_name.split('.')[0]
            dir_list.append(os.path.join(os.path.join(bd.datapath_to_casepath(path, app), mod_xls_name)))
            sheet_paths = self.get_xls_sheets(i)
            for j in sheet_paths:
                py_path_list.append(os.path.join(bd.datapath_to_casepath(path, app), mod_xls_name, j + '.py'))
        return dir_list, py_path_list

    def generate_py(self, py_path_list):
        sucess_list = []
        template_py = os.path.join(BaseOS().get_project_path(), "Conf", "template.py")
        for i in py_path_list:
            if os.path.exists(i) is not True:
                sucess_list.append(i)
                shutil.copy(template_py, i)
        return sucess_list

    def generate__init__py(self, dir_list):
        template_init_py = os.path.join(BaseOS().get_project_path(), "Conf", "template_init_.py")

        dir_list = BaseOS().get_all_dirs(os.path.join(BaseOS().get_project_path(), "TestCase"))
        dir_list.append(os.path.join(BaseOS().get_project_path(), "TestCase"))

        for i in dir_list:
            p = os.path.join(i, "__init__.py")
            if os.path.exists(p) is not True:
                shutil.copy(template_init_py, p)

# list1 = ['/Users/peiyaojun/PycharmProjects/APITesting/Data/C360_iOS/dispatcher.xls',
#          '/Users/peiyaojun/PycharmProjects/APITesting/Data/C360_iOS/i.xls']
# PyCreate().create_py(list1, 'C360_iOS')
