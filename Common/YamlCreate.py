"""
Create by：peiyaojun
Create time：2021-10-26
"""
import os
from json import JSONDecodeError

from Common.BaseData import BaseData
from Common.BaseOS import BaseOS
import xlrd
import yaml
import json

from Common.ConfMsg import ConfMsg


class YamlCreate:
    """
    用于 excle 生成 yaml 用例

    使用方法：
    YamlCreate().create_yaml(test_list, app)

    """

    def create_yaml(self, test_list, app, env):
        """
        生成yaml文件的主方法

        :param env: 环境
        :param test_list: TestCase目录下需要执行的用例.py路径list
        :param app: 当前用例对应的产品名称
        :return:
        """
        # 清除Data目录多余目录及文件
        data_root = os.path.join(BaseOS().get_project_path(), "Data", app)
        BaseOS().clear_folder(data_root)

        # 根据此次确认执行的用例，创建其相应目录
        new_path_list = []
        for path in test_list:
            dirs, file = os.path.split(BaseData().casepath_to_datapath(path, app))
            new_path_list.append(dirs)
        BaseOS().create_dirs(new_path_list)

        # 获取需要生成yaml文件的，xls文件及需解析的sheet
        xls_info = self.get_xls_info(test_list)

        # 根据xls生成yaml文件
        self.generate_yaml(xls_info, app, env)

    def case_yaml_data(self, table, env):
        yaml_data = {}
        row_nums = table.nrows
        col_nums = table.ncols
        keys = table.row_values(0)

        # 设置 Var、Global_Var
        yaml_data["Var"] = {}
        yaml_data["Global_Var"] = {}
        if "Var" in keys and table.cell_value(1, keys.index("Var")) != "":
            val = table.cell_value(1, keys.index("Var"))
            val = val.split("\n")
            for i in range(len(val) // 2):
                yaml_data["Var"][val[i * 2]] = val[i * 2 + 1]
        if "Global_Var" in keys and table.cell_value(1, keys.index("Global_Var")) != "":
            val = table.cell_value(1, keys.index("Global_Var"))
            val = val.split("\n")
            for i in range(len(val) // 2):
                yaml_data["Global_Var"][val[i * 2]] = val[i * 2 + 1]

        # 设置 TestCase
        yaml_data["TestCase"] = []
        normal_env = ConfMsg().get_ENV()
        for row in range(1, row_nums):
            test = {
                "name": "",
                "priority": 4,
                "encryption": 0,
                "sig": 0,
                "request": {
                    "method": "",
                    "env": normal_env,
                    "HOST": "",
                    "PATH": "",
                    "headers": {},
                    "params": {},
                },
                "validate": [],
                "export": {}
            }

            # 第 row 行的数据
            row_val = table.row_values(row)

            for col in range(col_nums):
                key = keys[col]
                pri_env = ""
                pri_normal = ""
                if key == "name":
                    test[key] = row_val[col]
                elif key == "priority":
                    pri_val = row_val[col]
                    pri_normal = pri_val
                elif key == "env":
                    test["request"][key] = normal_env if row_val[col] == "" else row_val[col]
                elif key.lower() == (env + "-priority").lower():
                    pri_val = row_val[col]
                    pri_env = pri_val
                elif key == "encryption":
                    enc_val = row_val[col]
                    if enc_val != "":
                        test[key] = int(enc_val)
                elif key == "sig":
                    s_val = row_val[col]
                    if s_val != "":
                        test[key] = int(s_val)
                elif key in ["method", "HOST"]:
                    test["request"][key] = row_val[col]
                elif key == "PATH":
                    test["request"][key] = row_val[col].lstrip("/") if row_val[col].startswith("/") else row_val[col]
                elif key == "headers":
                    # 获取 此行中 headers的值
                    h_val = row_val[col]
                    for i in h_val.split("\n"):
                        if i != "":
                            i_list = i.split(":", maxsplit=1)
                            test["request"][key][i_list[0]] = i_list[1] if len(i_list) == 2 else ""
                elif key == "params":
                    p_val = row_val[col]
                    # IDPhoto 部分接口请求时，请求体为json时，直接填入json时判断是否为json数据（有null值时，直接写null）
                    try:
                        p_val = json.loads(p_val)
                        test["request"][key] = p_val
                    except JSONDecodeError:
                        for i in p_val.split("\n"):
                            if i != "":
                                i_list = i.split("=", maxsplit=1)
                                test["request"][key][i_list[0]] = i_list[1] if len(i_list) == 2 else ""
                elif key == "validate":
                    v_val = row_val[col].split("\n")
                    v_list = []
                    for i in range(len(v_val) // 3):
                        v_list.append({v_val[i * 3]: [v_val[i * 3 + 1], v_val[i * 3 + 2]]})
                    test[key] = v_list
                elif key == "export":
                    # 若export字段下无数据时，删除export键值对
                    if row_val[col] == "":
                        del test[key]
                    else:
                        e_val = row_val[col].split("\n")
                        for i in range(len(e_val) // 2):
                            test[key][e_val[i * 2]] = e_val[i * 2 + 1]

                # 判断环境 优先级，有时，使用环境优先级，若没有值，使用优先级，若没有优先级，使用默认值5
                if pri_env != "":
                    test["priority"] = int(pri_env)
                elif pri_normal != "":
                    test["priority"] = int(pri_normal)

            yaml_data["TestCase"].append({"Test": test})

        return yaml_data

    def generate_yaml(self, xls_info, app, env):

        root_path = os.path.join(BaseOS().get_project_path(), "Data", app)
        for xls_name in xls_info.keys():
            xls_path = os.path.join(root_path, xls_name + ".xls")

            # 若找不到xls，使用xlsx
            if not os.path.exists(xls_path):
                xls_path += "x"
            data = xlrd.open_workbook(xls_path)
            tables = data.sheet_names()

            xls_table = xls_info[xls_name]
            for i in xls_table:
                if xls_name == app:
                    yaml_path = os.path.join(root_path, i + ".yaml")
                else:
                    yaml_path = os.path.join(root_path, xls_name, i + ".yaml")

                if i in tables:
                    table = data.sheet_by_name(i)
                    yaml_data = self.case_yaml_data(table, env)

                    with open(yaml_path, "w") as f:
                        yaml.dump(yaml_data, f, encoding='utf-8', allow_unicode=True)

                    del table
                    del yaml_data

            del data

    def get_xls_info(self, test_list):
        """
        返回用例xls的名字及其需要用于生成yaml的sheet名字
        return :{xls名字：[sheet1,sheet2...]; xls名字2：[....]}
        """
        info = {}
        for i in test_list:
            test_path, file = os.path.split(i)
            list_path = BaseOS().path_list(test_path)
            xls_name = list_path[-1]
            xls_sheet_name, type = os.path.splitext(file)
            if xls_name not in info.keys():
                info[xls_name] = [xls_sheet_name]
            else:
                info[xls_name] = info[xls_name] + [xls_sheet_name]
        return info
