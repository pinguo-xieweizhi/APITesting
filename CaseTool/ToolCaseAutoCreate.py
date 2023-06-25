import copy
import json
import os
import random
import re

import xlrd
import xlwt
from Common.BaseOS import BaseOS


class CaseAutoCreate:
    # 生成的用例表头
    table_head = ["name", "priority", "PROD-priority", "PROD-O/S-priority", "PROD-PRE-priority", "encryption", "sig",
                  "env", "method", "HOST", "PATH", "headers", "params",
                  "validate", "export", "Var", "Global_Var"]

    # 接口描述文件中的公共数据
    common_data = {"content": "", "type": "", "encryption": "", "sig": 0, "host": "", "path": "", "env": "",
                   "method": "",
                   "headers": "", "params": "", "export": "", "varlist": "", "Var": "",
                   "PROD-priority": "", "PROD-O/S-priority": "", "PROD-PRE-priority": "", "priority": "",
                   "Global_Var": ""}
    common_data_list = []

    # 接口文件中的 字段信息表头中的字段
    org_field_key_head = ["字段说明", "后台配置项", "字段", "是否必下发", "值类型", "list值类型", "是否为url",
                          "是否可为空值", "是否可为null", "值规则", "值", "值说明", "备注", "所属文件", "字段2",
                          "不验证list顺序", "比对文件", "比对文件名", "比对list长度", "值映射", "值映射类型"]

    # 取出真实的 字段信息表头中的字段 list
    field_key_head = []

    type_dict = {"int": int, "str": str, "float": float, "dict": dict, "list": list, "bool": bool}

    case_id = 1

    # 自动生成用例 总方法
    def create(self):
        """
        自动生成用例 总方法

        :return:
        """
        main_path = os.path.join(BaseOS().get_project_path(), "Tool")
        case_main_path = os.path.join(BaseOS().get_project_path(), "Tool", "Case")
        if not os.path.exists(case_main_path):
            os.makedirs(case_main_path)

        xls_path_list = []
        xls_path_list += BaseOS().get_all_files_dir(path=main_path, exc_file_name=".DS_Store", need_type=[".xlsx"])
        xls_path_list += BaseOS().get_all_files_dir(path=main_path, exc_file_name=".DS_Store", need_type=[".xls"])

        # 删除已生成的case
        for xls_path in xls_path_list:
            # 保存用例.xls 文件路径名称获取
            file_name = re.sub(r'\*|\\|\(|\)|（|）|\[|\]|\?|<|>|&|\||}|;|/|`| ', "", os.path.basename(xls_path))
            file_name = file_name if file_name.endswith("s") else file_name[:-1]
            if os.path.exists(os.path.join(case_main_path, file_name)):
                os.remove(os.path.join(case_main_path, file_name))
                # time.sleep(1)
        # 保留存在的excle，并且移除为excle自动创建的编辑中副本的文件
        xls_path_list = list(filter(lambda x: os.path.exists(x), xls_path_list))

        xls_path_list = list(filter(lambda x: not os.path.split(x)[1].startswith("~$"), xls_path_list))

        for xls_path in xls_path_list:
            print("\n\n<<<<<<<<<<<<<<<< Excle:", xls_path, ">>>>>>>>>>>>>>>>>")
            # 获取接口描述文档
            data = xlrd.open_workbook(xls_path)
            tables = data.sheet_names()

            # 创建新的 用例.xls 文件
            new_xls = xlwt.Workbook(encoding='utf-8')

            # 遍历 接口描述文档中的每一张表
            for table in tables:
                print("\n== sheet:", table, "===")
                new_sheet = new_xls.add_sheet(table)
                sheet_data = data.sheet_by_name(table)

                # 创建 用例数据
                case_data = self.excle_sheet_to_case(sheet_data)

                # 将用例数据写入excle
                for row in range(0, len(case_data)):
                    for col in range(0, len(case_data[row])):
                        new_sheet.write(row, col, case_data[row][col])

            file_name = re.sub(r'\*|\\|\(|\)|（|）|\[|\]|\?|<|>|&|\||}|;|/|`| ', "", os.path.basename(xls_path))
            file_name = file_name if file_name.endswith("s") else file_name[:-1]
            file_name = file_name.replace("-","_")
            new_xls.save(os.path.join(case_main_path, file_name))
            self.case_id = 1

    # 通过 excle sheet 生成 case 用例数据,并获取共公表头数据
    def excle_sheet_to_case(self, sheet_data):
        """
        生成 case 用例数据

        :param sheet_data: 接口文件 一个sheet的数据
        :return:[[单元格数据1，单元格数据2,...],[]]
        """
        self.common_data_list = []

        case_data = [self.table_head]
        row_nums = sheet_data.nrows

        field_data_start_row = 0

        # 表是否为可执行的用例 标志
        sheet_is_case = False

        # 获取第一行数据，判断此表是否需要生成用例，并设标记
        row_0_list = sheet_data.row_values(0)
        if not [x for x in row_0_list if x not in self.table_head]:
            sheet_is_case = True

        # 判断是否为可直接执行用例（不用生成用例）
        if sheet_is_case:
            # 直接拷备用例sheet
            case_data = []
            for row2 in range(0, row_nums):
                row_list = []
                for cell in sheet_data.row_values(row2):
                    row_list.append(cell)
                case_data.append(row_list)
        else:
            for row in range(0, row_nums):
                # 获取每行的第一个单元格进行数据判断
                flag = sheet_data.cell_value(row, 0)

                # 设置接口公共数据
                if flag in self.common_data.keys():
                    row_value = sheet_data.row_values(row)
                    row_value.reverse()
                    t1 = 0
                    for t in range(0, len(row_value)):
                        if row_value[t] != "":
                            t1 = t
                            break
                    row_value.reverse()
                    row_value = row_value[0:len(row_value) - t1]
                    for i in range(len(self.common_data_list), len(row_value) - 1):
                        self.common_data_list.append(copy.deepcopy(self.common_data))
                    for i in range(0, len(row_value) - 1):
                        self.common_data_list[i][flag] = row_value[i + 1]

                # 获取到 字段信息 表头，并获取 字段信息 的起始行
                if flag in self.org_field_key_head:
                    self.field_key_head = sheet_data.row_values(row)
                    field_data_start_row = row + 1
                    break

            # 获取字段信息所有行数据
            rows_value = []
            for row in range(field_data_start_row, row_nums):
                rows_value.append(sheet_data.row_values(row))

            # 分析 生成case的类型并生成用例
            temp = self.case_type_dispenses(rows_value)

            for case in temp:
                row = []
                for i in self.table_head:
                    row.append(case[i])
                case_data.append(row)
        return case_data

    # 分析 type类型生成需要的用例
    def case_type_dispenses(self, rows_value):
        """
        分析 接口信息 通过不同的 接口用例类型 生成需要的用例

        :param rows_value:  返回
        :return:[{
                "name": "",
                "priority": "",
                "encryption": "",
                "sig": "",
                "method": ",
                "HOST": "",
                "PATH": "",
                "headers": "",
                "params": "",
                "validate": "",
                "export": "",
                "Var": ""
            },{}...]
        """
        type = self.common_data_list[0]["type"]
        if type == "field":
            return self.field_case(rows_value)
        elif type == "zip_json":
            return self.zip_json_case(rows_value)
        elif type == "compare":
            return self.compare_case(rows_value)
        elif type == "global":
            return self.global_case(rows_value)
        return []

    # 获取用例的共公信息
    def common_data_analysis(self):
        """
        分析获取用例的共公信息
        :return: {
                "name": "",
                "priority": "",
                "PROD-priority": "",
                "PROD-O/S-priority": "",
                "PROD-PRE-priority": "",
                "encryption": "",
                "sig": "",
                "env": "",
                "method": "",
                "HOST": "",
                "PATH": "",
                "headers": "",
                "params": "",
                "validate": "",
                "export": "",
                "Var": "",
                "Global_Var": ""
            },{}
        """
        data_org = {
            "name": "",
            "priority": "",
            "PROD-priority": "",
            "PROD-O/S-priority": "",
            "PROD-PRE-priority": "",
            "encryption": 0,
            "sig": 1,
            "env": "",
            "method": "",
            "HOST": "",
            "PATH": "",
            "headers": "",
            "params": "",
            "validate": "",
            "export": "",
            "Var": "",
            "Global_Var": ""
        }
        data_list = []

        # 生成Var、global_var参数
        var = ""
        global_var = ""

        # 准备多组需要获取公共信息的空数据组
        for i in range(0, len(self.common_data_list)):
            data_list.append(copy.deepcopy(data_org))
        for i in range(0, len(self.common_data_list)):
            data_list[i]["sig"] = int(float(self.common_data_list[i]["sig"]))

            data_list[i]["priority"] = int(float(self.common_data_list[i]["priority"])) if self.common_data_list[i][
                                                                                               "priority"] != "" else "5"
            data_list[i]["PROD-priority"] = int(float(self.common_data_list[i]["PROD-priority"])) if \
                self.common_data_list[i]["PROD-priority"] != "" else ""
            data_list[i]["PROD-O/S-priority"] = int(float(self.common_data_list[i]["PROD-O/S-priority"])) if \
                self.common_data_list[i]["PROD-O/S-priority"] != "" else ""
            data_list[i]["PROD-PRE-priority"] = int(float(self.common_data_list[i]["PROD-PRE-priority"])) if \
                self.common_data_list[i]["PROD-PRE-priority"] != "" else ""

            data_list[i]["encryption"] = self.common_data_list[i]["encryption"]
            data_list[i]["env"] = self.common_data_list[i]["env"]
            data_list[i]["method"] = self.common_data_list[i]["method"]
            data_list[i]["HOST"] = self.common_data_list[i]["host"]
            data_list[i]["PATH"] = self.common_data_list[i]["path"]
            this_col_var = self.common_data_list[i]["Var"]

            var += (this_col_var + "\n") if this_col_var != "" else ""

            this_col_Global_var = self.common_data_list[i]["Global_Var"]
            global_var += (this_col_Global_var + "\n") if this_col_Global_var != "" else ""

        for p in range(0, len(self.common_data_list)):
            params = ""
            # 当params 中为{} json数据时，IDCamera360部分接口会使用到，不进行参数化数据解析
            if self.common_data_list[p]["params"].startswith("{") and self.common_data_list[p]["params"].endswith("}"):
                data_list[p]["params"] = self.common_data_list[p]["params"]
            else:
                org_params = self.common_data_list[p]["params"].replace("\r", "").split("\n")
                for h in org_params:
                    if h != "":
                        var_temp = h.split("=", 1)

                        if len(var_temp) != 2:
                            print("\n!!!!!!!! params中必须按 key=value 的形式填入 !!!!!!!!\n")

                        # 判断 key=value 中value是否为${key},当不为${key}
                        m = re.findall(r'^\${.+}$', var_temp[1])
                        if not m:
                            var_key = var_temp[0] if var_temp[0] not in var else var_temp[0] + str(
                                var.count(var_temp[0]))
                            var += var_key + "\n" + var_temp[1] + "\n"
                            temp = h.split("=")
                            params += temp[0] + "=${" + var_key + "}\n"
                        # 若 key=${key}时，无需生成新的Var参数
                        else:
                            params += h + "\n"

                data_list[p]["params"] = params.rstrip().rstrip()

            headers = ""
            org_headers = self.common_data_list[p]["headers"].replace("\r", "").split("\n")
            for h in org_headers:
                if h != "":
                    temp = h.split(":", 1)

                    if len(temp) != 2:
                        print("\n!!!!!!!! headers中必须按 key:value 的形式填入 !!!!!!!!\n")

                    # 判断 key=value 中value是否为${key},当不为${key}
                    m = re.findall(r'^\${.+}$', temp[1])
                    if not m:
                        var_key = re.sub(r'\W', "", temp[0])
                        # var += h.replace(":", "\n", 1) + "\n"
                        var_key = var_key if var_key not in var else var_key + str(var.count(var_key))
                        var += var_key + "\n" + temp[1] + "\n"

                        headers += temp[0] + ":${" + var_key + "}\n"

                    # 若 key=${key}时，无需生成新的Var参数
                    else:
                        headers += h + "\n"
            data_list[p]["headers"] = headers.rstrip().rstrip()

        for p in range(0, len(self.common_data_list)):
            data_list[p]["Var"] = var
            data_list[p]["Global_Var"] = global_var.rstrip().rstrip()
        return data_list

    # 接口文档sheet 中 type = field 类型的用例生成
    def field_case(self, rows_value):
        """
        接口文档sheet 中 type = field 类型的用例生成

        :param rows_value: [[],[]....] excle获取的多行数据
        :return: [{
                "name": "",
                "priority": "",
                "encryption": "",
                "sig": "",
                "env": "",
                "method": ",
                "HOST": "",
                "PATH": "",
                "headers": "",
                "params": "",
                "validate": "",
                "export": "",
                "Var": ""
            },{}...]

        """

        # 生成case：准备 case 公共字段的数据
        case_data = []
        case_data_row_list = self.common_data_analysis()
        case_data_row = case_data_row_list[0]

        # 对字段进行分析，并生成适用于接口自动化的用例 [*] {keyexist:trure}
        rows_value = self.field_key_analysis(rows_value, 'body')

        # --------生成case 生成取值用例
        for i in range(0, len(case_data_row_list)):
            if self.common_data_list[i]["export"] != "":
                temp_case_data = copy.deepcopy(case_data_row_list[i])
                name = str('%05d' % self.case_id) + "_" + self.common_data_list[i]["content"] + "值获取"
                validate = "eq\ncode\n200"
                temp_case_data["name"] = name
                temp_case_data["validate"] = validate
                temp_case_data["export"] = self.common_data_list[i]["export"]
                case_data.append(copy.deepcopy(temp_case_data))
                self.case_id += 1

        # --------生成case:获取接口数据，并存入参数
        case_data_get_body = copy.deepcopy(case_data_row)
        case_data_get_body["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0]["content"] + "：返回体数据获取"
        case_data_get_body["validate"] = "eq\ncode\n200"
        case_data_get_body["export"] = "QARESDATA\nbody"
        case_data.append(copy.deepcopy(case_data_get_body))
        self.case_id += 1

        # 修改用例公共数据 case_data_row
        case_data_row["method"] = ""
        case_data_row["sig"] = ""
        case_data_row["env"] = ""
        case_data_row["HOST"] = "${QARESDATA}"
        case_data_row["PATH"] = ""
        case_data_row["headers"] = ""
        case_data_row["params"] = ""

        # --------生成case：字段值类型检查用例
        case_data_row_tq = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            key = row[self.field_key_head.index("字段")]
            key_type = row[self.field_key_head.index("值类型")]
            validate += "tq\n" + key + "\n" + key_type + "\n"

            # 针对 list 中的值类型校验
            if key_type == "list":
                type_item = row[self.field_key_head.index("list值类型")]
                validate += "tq\n" + key + "[*]\n" + type_item + "\n"

        case_data_row_tq["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0]["content"] + "：字段值类型校验"
        case_data_row_tq["validate"] = validate.rstrip().rstrip()
        case_data.append(copy.deepcopy(case_data_row_tq))
        self.case_id += 1

        # --------生成case: 字段下发逻辑用例，是否下发字段
        case_data_row_ke = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            key = row[self.field_key_head.index("字段")]
            must_exist = row[self.field_key_head.index("是否必下发")]
            must_exist = "" if must_exist == "" else str(int(float(must_exist)))

            if must_exist == "1":
                validate += "ke\n" + key + "\ntrue\n"

        case_data_row_ke["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0][
            "content"] + "：字段必须存在与否校验"
        case_data_row_ke["validate"] = validate.rstrip().rstrip()
        case_data_row_ke["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_ke))
        self.case_id += 1

        # --------生成case: url 链接检查
        case_data_row_url = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            # 将 url前的最后一个取数据变为取【0】
            key = row[self.field_key_head.index("字段")]
            # key2 = re.sub(r'(^.+\[)(\*)(\])(.*)$', "\g<1>0\g<3>\g<4>", key)
            key2 = re.sub(r'\[\*\]', '[0]', key)
            is_url = row[self.field_key_head.index("是否为url")]
            is_url = "" if is_url == "" else str(int(float(is_url)))

            if is_url == "1":
                validate += "url\n" + key2 + "\ntrue\n"

        case_data_row_url["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0][
            "content"] + "：url访问、url格式校验"
        case_data_row_url["validate"] = validate.rstrip().rstrip()
        case_data_row_url["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_url))
        self.case_id += 1

        # --------生成case: 字段值是否可为空值检查（"",[],{}...）
        case_data_row_empty_value = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:

            key = row[self.field_key_head.index("字段")]
            is_empty = row[self.field_key_head.index("是否可为空值")]
            is_empty = "" if is_empty == "" else str(int(float(is_empty)))

            if is_empty != "1":
                key_type = row[self.field_key_head.index("值类型")]
                assert_value = []
                if key_type == "str":
                    assert_value = [""]
                elif key_type == "list":
                    assert_value = [[]]
                elif key_type == "dict":
                    assert_value = [{}]

                if assert_value:
                    validate += "niv\n" + key + "\n" + str(assert_value) + "\n"

        case_data_row_empty_value["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0][
            "content"] + "：字段值是否可为空值检查（"",[],{}...）"
        case_data_row_empty_value["validate"] = validate.rstrip().rstrip()
        case_data_row_empty_value["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_empty_value))
        self.case_id += 1

        # --------生成case: 字段值是否可为null检查
        case_data_row_null = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            key = row[self.field_key_head.index("字段")]
            is_null = row[self.field_key_head.index("是否可为null")]
            is_null = "" if is_null == "" else str(int(float(is_null)))

            if is_null == "1":
                # assert_value = '["null"]'
                validate += "in\n" + key + "\ntrue\n"
            else:
                validate += "in\n" + key + "\nfalse\n"

        case_data_row_null["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0][
            "content"] + "：字段值是否可为null检查"
        case_data_row_null["validate"] = validate.rstrip().rstrip()
        case_data_row_null["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_null))
        self.case_id += 1

        # --------生成case: 字段值正确性校验
        case_data_row_iv = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            key = row[self.field_key_head.index("字段")]
            temp_value = row[self.field_key_head.index("值")]
            key_type = row[self.field_key_head.index("值类型")].split(",")

            # 值一列是取出的值为浮点型，进行此字段类型判断，若为int，强转为int
            if isinstance(temp_value, float):
                if key_type == "int":
                    temp_value = int(float(temp_value))
                temp_value = str(temp_value)

            # 获取值一列中的数据并切片，最终生成正确类型值的list
            if temp_value != "":
                if temp_value.find("\r\n") > 0:
                    temp_value = temp_value.split("\r\n")
                else:
                    temp_value = temp_value.split("\n")
                assert_value = []

                # 对值序列中的值进行类型转换
                for v in temp_value:
                    # if v != "":
                    if "int" in key_type:
                        if v != "null":
                            assert_value.append(int(float(v)))
                        else:
                            assert_value.append("null")
                    if "float" in key_type:
                        assert_value.append(float(v))
                    if "dict" in key_type:
                        assert_value.append(json.loads(v))
                    if "list" in key_type:
                        assert_value.append(eval(v))
                    if "bool" in key_type:
                        assert_value.append(v.lower())
                    if "str" in key_type:
                        assert_value.append(v)
                assert_value = str(assert_value).replace("'null'", 'null')  # 处理值中为 null的情况
                # 保存为true、false，以便后期使用json.loads可转化为python可识别的True,False
                if "bool" in key_type:
                    assert_value = assert_value.replace("'", '"').replace('"', '')

                validate += "iv\n" + key + "\n" + assert_value + "\n"

        case_data_row_iv["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0]["content"] + "：字段值正确性校验"
        case_data_row_iv["validate"] = validate.replace("'", '"').rstrip().rstrip()
        case_data_row_iv["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_iv))
        self.case_id += 1

        # --------生成case: 字段值规则正确性校验
        case_data_row_reg = copy.deepcopy(case_data_row)
        validate = ""
        # 遍例每行数据并生成断言内容
        for row in rows_value:
            key = row[self.field_key_head.index("字段")]
            reg_value = row[self.field_key_head.index("值规则")]

            if reg_value != "":
                validate += "reg\n" + key + "\n" + reg_value + "\n"

        case_data_row_reg["name"] = str('%05d' % self.case_id) + "_" + self.common_data_list[0][
            "content"] + "：字段值规则正确性校验"
        case_data_row_reg["validate"] = validate.replace("'", '"').rstrip().rstrip()
        case_data_row_reg["Var"] = ""
        case_data.append(copy.deepcopy(case_data_row_reg))
        self.case_id += 1

        case_data = self.var_list2(case_data)

        return case_data

    # 对字段进行分析，并生成适用于接口自动化的key [*] {keyexist:true} {isnot:}
    def field_key_analysis(self, rows_value, pre_key):
        """
        对字段进行分析，并生成适用于接口自动化的用例 [*] {keyexist:trure}

        :param type: 此时key字段类型，body：响应体中json校验
        :param rows_value: [[],[]....] excle获取的多行数据
        :return: [[],[]] 与rows_value中一样，仅替换list中 key元素

        """
        # 获取 字段在 字段表头中的下标
        key_head_index = self.field_key_head.index("字段")

        # 添加字段前缀 headers、code、body
        # 当key为 headers、code、body时无需再添加前缀
        for index in range(0, len(rows_value)):
            row = rows_value[index]
            key = row[self.field_key_head.index("字段")]
            key = (pre_key + "." if key != pre_key and not key.startswith("body.") and pre_key != '' else '') + key
            # key = key.replace("body.body", "body")  # 修复多个body.body
            rows_value[index][key_head_index] = key

        # 对字段进行分析，并生成适用于接口自动化的用例 [*] {keyexist:trure}
        new_rows_value = copy.deepcopy(rows_value)
        print("== 处理后的字段key ==")
        for index in range(0, len(rows_value)):
            row = rows_value[index]
            key = row[key_head_index]

            key_list = key.split(".")
            new_key = ""
            for key_index in range(0, len(key_list)):
                key_item = key_list[key_index]
                new_key = ".".join(list(filter(None, [new_key, key_item])))
                temp_key = ".".join(key_list[0:key_index + 1])

                this_row = None
                for r in rows_value:
                    if r[key_head_index] == temp_key:
                        this_row = copy.deepcopy(r)
                        break
                if this_row is not None:
                    must_exist = this_row[self.field_key_head.index("是否必下发")]
                    must_exist = "" if must_exist == "" else str(int(float(must_exist)))

                    key_type = this_row[self.field_key_head.index("值类型")]

                    is_null = this_row[self.field_key_head.index("是否可为null")]
                    is_null = "" if is_null == "" else str(int(float(is_null)))

                    if must_exist != "1":
                        new_key += '{"keyexist":true}.' + key_item

                    if key_index < len(key_list) - 1:
                        if key_type == "list":
                            new_key += '[*]'
                        if is_null == "1":
                            new_key += '{"isnot":null}.' + key_item
            print(new_key)
            new_rows_value[index][key_head_index] = new_key

        return new_rows_value

    # 接口文档sheet 中 type = compare 类型的用例生成
    def compare_case(self, rows_value):
        # 生成case：准备 case 公共字段的数据
        case_data = []
        case_data_row_list = self.common_data_analysis()

        # --------生成case 生成取值用例
        for i in range(0, len(case_data_row_list)):
            if self.common_data_list[i]["export"] != "":
                temp_case_data = copy.deepcopy(case_data_row_list[i])
                name = str('%05d' % self.case_id) + "_" + self.common_data_list[i]["content"] + "值获取"
                validate = "eq\ncode\n200"
                temp_case_data["name"] = name
                temp_case_data["validate"] = validate
                temp_case_data["export"] = self.common_data_list[i]["export"]
                case_data.append(copy.deepcopy(temp_case_data))
                self.case_id += 1

        # --------生成case
        var = case_data_row_list[0]["Var"]  # 获取当前参数情况
        varlist = var.split("\n")
        if len(varlist) % 2 != 0:
            var = "\n".join(varlist[0:-1])

        # 获取2个接口需返回的Response data数据
        for i in range(0, 2):
            temp_case_data = copy.deepcopy(case_data_row_list[i])
            name = str('%05d' % self.case_id) + "_" + self.common_data_list[i]["content"] + "Response data获取"
            validate = "eq\ncode\n200"
            temp_case_data["name"] = name
            temp_case_data["validate"] = validate
            temp_case_data["export"] = "QACMPDATA" + str(i + 1) + "\nbody"
            case_data.append(copy.deepcopy(temp_case_data))
            self.case_id += 1

        # 清空case_data_row_list中不需要的参数值
        case_data_row_list[0]["method"] = ""
        case_data_row_list[0]["sig"] = ""
        case_data_row_list[0]["env"] = ""
        case_data_row_list[0]["HOST"] = ""
        case_data_row_list[0]["PATH"] = ""
        case_data_row_list[0]["headers"] = ""
        case_data_row_list[0]["params"] = ""

        # 生成cmp 断言用例
        for row in rows_value:
            row_name = row[self.field_key_head.index("字段说明")]
            field_key_1 = row[self.field_key_head.index("字段")]
            field_key_2 = row[self.field_key_head.index("字段2")]
            cmp_list_seq = row[self.field_key_head.index("不验证list顺序")]
            cmp_list_seq = "" if cmp_list_seq == "" else str(int(float(cmp_list_seq)))

            cmp_file = row[self.field_key_head.index("比对文件")]
            cmp_file = "" if cmp_file == "" else str(int(float(cmp_file)))

            cmp_filename = row[self.field_key_head.index("比对文件名")]
            cmp_filename = "" if cmp_filename == "" else str(int(float(cmp_filename)))

            cmp_listlength = row[self.field_key_head.index("比对list长度")]
            cmp_listlength = "" if cmp_listlength == "" else str(int(float(cmp_listlength)))

            value_map = row[self.field_key_head.index("值映射")]
            value_map_type = row[self.field_key_head.index("值映射类型")]

            if field_key_1 != "" and field_key_2 != "":
                name = str('%05d' % self.case_id) + "_" + '"' + row_name + '":' + "2组数据比较"
                temp_case_data = copy.deepcopy(case_data_row_list[0])

                str1 = 'QACMPKEY' + str(var.count('QACMPKEY'))
                str2 = 'QACMPKEY' + str(var.count('QACMPKEY') + 1)

                var += "\n" + str1 + "\n" + field_key_1.replace('"', "'")
                var += "\n" + str2 + "\n" + field_key_2.replace('"', "'")

                validate = 'cmp\n'
                validate += '["${' + str1 + '}","${' + str2 + '}"]\n'
                validate += '{"value1":${QACMPDATA1},"value2":${QACMPDATA2}'

                validate += ',"cmp_list_seq":' + ('""' if cmp_list_seq == "" else cmp_list_seq)
                validate += ',"cmp_file":' + ('""' if cmp_file == "" else cmp_file)
                validate += ',"cmp_filename":' + ('""' if cmp_filename == "" else cmp_filename)
                validate += ',"cmp_listlength":' + ('""' if cmp_listlength == "" else cmp_listlength)
                validate += ',"value_map":' + ('""' if value_map == "" else str(
                    [x.split("->") for x in value_map.replace("\r", "").split("\n")]).replace("'", '"'))
                validate += ',"value_map_type":' + (
                    '""' if value_map_type == "" else str(value_map_type.split("->")).replace("'", '"'))
                validate += '}'

                temp_case_data["name"] = name
                temp_case_data["validate"] = validate
                case_data.append(copy.deepcopy(temp_case_data))
                self.case_id += 1

        # 获取varlist设置，生成修改参数后的用例组
        case_data = self.var_list2(case_data)

        case_data[0]["Var"] = var
        for i in range(1, len(case_data)):
            case_data[i]["Var"] = ""
        return case_data

    # 接口文档sheet 中 type = global 类型的用例生成
    def global_case(self, rows_value):
        # 生成case：准备 case 公共字段的数据
        case_data = []
        case_data_row_list = self.common_data_analysis()

        # --------生成case 生成取值用例
        for i in range(0, len(case_data_row_list)):
            if self.common_data_list[i]["export"] != "":
                temp_case_data = copy.deepcopy(case_data_row_list[i])
                name = str('%05d' % self.case_id) + "_" + self.common_data_list[i]["content"] + "值获取"
                validate = "eq\ncode\n200"
                temp_case_data["name"] = name
                temp_case_data["validate"] = validate
                temp_case_data["export"] = self.common_data_list[i]["export"]
                if i != 0:
                    temp_case_data["Var"] = ""
                    temp_case_data["Global_Var"] = ""
                case_data.append(copy.deepcopy(temp_case_data))
                self.case_id += 1
        print("生成Global取值用例 %s 条" % len(case_data_row_list))
        return case_data

    # 已抛弃
    def var_list(self, case_data):
        # 判断是否有varlist需要利用参数遍历用例
        var_list = []
        var_value = []
        temp = self.common_data_list[0]["varlist"].replace("\r", "").split("\n")
        for j in range(0, int(len(temp) / 2)):
            var_list.append([])
            var_value.append("")

        for i in range(0, len(self.common_data_list)):
            temp = self.common_data_list[i]["varlist"].replace("\r", "").split("\n")

            for j in range(0, int(len(temp) / 2)):
                var_list[j].append(temp[j * 2])
                var_value[j] = temp[j * 2 + 1]

        if var_list:
            for i in range(0, len(var_list)):
                temp_case_3 = []
                for j in json.loads(var_value[i].replace("'", '"')):
                    temp_case_2 = copy.deepcopy(case_data)
                    for m in range(0, len(temp_case_2)):
                        temp_case_2[m]["name"] = str('%05d' % self.case_id) + "_" + j + " " + \
                                                 temp_case_2[m]["name"].split("_", 1)[1]
                        for k in var_list[i]:
                            k = k.split(",")
                            for w in k:
                                temp_case_2[m]["headers"] = re.sub(r'(.*)(' + w + ':)(\$\{\w+\})(.*)',
                                                                   "\g<1>\g<2>" + j + "\g<4>",
                                                                   temp_case_2[m]["headers"],
                                                                   re.DOTALL)
                                temp_case_2[m]["params"] = re.sub(r'(.*)(' + w + '=)(\$\{\w+\})(.*)',
                                                                  "\g<1>\g<2>" + j + "\g<4>", temp_case_2[m]["params"],
                                                                  re.DOTALL)
                        self.case_id += 1

                    temp_case_3 += temp_case_2
                case_data += temp_case_3
        return case_data

    def var_list2(self, case_data):
        # 判断是否有varlist需要利用参数遍历用例
        var_list = []
        var_value = []
        var_value_prio = []
        temp = self.common_data_list[0]["varlist"].replace("\r", "").split("\n")

        # 针对老数据补充 varlist 参数优先级
        def add_prio(temp):
            temp2 = []
            for i in range(len(temp)):
                if len(temp2) % 3 == 2:
                    if not re.match(r"^[0-9]+$", temp[i]):
                        temp2.append("")
                        temp2.append(temp[i])
                    else:
                        temp2.append(temp[i])
                else:
                    temp2.append(temp[i])
            if len(temp2) % 3 != 0:
                temp2.append("")
            temp3 = []
            for i in range(int(len(temp2) / 3)):
                temp3.append([temp2[i * 3], temp2[i * 3 + 1], temp2[i * 3 + 2]])
            temp3 = sorted(temp3, key=lambda x: 4 if x[2] == "" else int(x[2]), reverse=True)
            return sum(temp3, [])

        temp = add_prio(temp)

        for j in range(0, int(len(temp) / 3)):
            var_list.append([])
            var_value.append([])

        for var_i in range(0, len(self.common_data_list)):
            temp = self.common_data_list[var_i]["varlist"].replace("\r", "").split("\n")
            temp = add_prio(temp)
            for j in range(0, int(len(temp) / 3)):
                var_list[j].append(temp[j * 3].split(","))
                var_value[j].append([y if y.endswith("]") else y + "]" for y in
                                     [x if x.startswith("[") else "[" + x for x in temp[j * 3 + 1].split("],[")]])
                var_value_prio.append(temp[j * 3 + 2])

        # 当一个表头一行参数为多个，以,隔开，但是对应的值只有一组 比如
        """
        PG-Language,PG-Locale
        ["en2","ja2","th","vi","zh-Hant","ko","hi","id","mes-MX","pt-BR","tr-CN"]
        """

        # 使用表中最后一组数据进行补充
        for var_list_i in range(0, len(var_list)):
            for var_list_i_index in range(0, len(var_list[var_list_i])):
                for key_i in range(0, len(var_list[var_list_i][var_list_i_index])):
                    if key_i >= len(var_value[var_list_i][var_list_i_index]):
                        add = var_value[var_list_i][var_list_i_index][len(var_value[var_list_i][var_list_i_index]) - 1]
                        var_value[var_list_i][var_list_i_index].append(add)

        if var_list:
            # 遍例 varlist 参数组 （2行为一组）
            for var_i in range(0, len(var_list)):
                # 获取当前参数组中的值
                key_value = var_value[var_i]

                # 获取当前参数组中的值个数
                key_value_count = len(json.loads(key_value[0][0]))

                temp_case_3 = []

                # 遍例当前参数组中的每一个值 如["en","ja","th","vi","zh-Hant","ko","hi","id","mes-MX","pt-BR","tr-CN"]
                for key_value_id in range(0, key_value_count):

                    temp_case_2 = copy.deepcopy(case_data)
                    # 遍例每一条用例，判断是否包含参数组中，的所有参数，满足时需要替换值
                    for case_i in range(0, len(temp_case_2)):

                        find_all_key_flag = [True for x in var_list[var_i]]
                        # 遍便参数组中请求头与体数据（当前为：var_list[var_i]）
                        for var_i_index in range(0, len(var_list[var_i])):
                            # 获取检查的key
                            this_key_list = var_list[var_i][var_i_index]

                            for this_key in this_key_list:

                                # 判断是否为path.key（修改path中的参数）
                                if this_key.lower().startswith("path."):
                                    if temp_case_2[case_i]["PATH"] == "" and not re.match(
                                            r'.*(\${' + this_key.split(".", 1)[1] + '}).*', temp_case_2[case_i]["PATH"],
                                            re.DOTALL):
                                        find_all_key_flag[var_i_index] = False

                                elif not re.match(r'(.*)(' + this_key + ':)(\$\{\w+\})(.*)',
                                                  temp_case_2[case_i]["headers"],
                                                  re.DOTALL) and not re.match(r'(.*)(' + this_key + '=)(\$\{\w+\})(.*)',
                                                                              temp_case_2[case_i]["params"], re.DOTALL):
                                    find_all_key_flag[var_i_index] = False

                        name_add = ''
                        # 开始替换用例中的参数值
                        for var_i_index in range(0, len(var_list[var_i])):
                            # 获取检查的key
                            this_key_list = var_list[var_i][var_i_index]

                            for this_key_index in range(0, len(this_key_list)):

                                if find_all_key_flag[var_i_index]:
                                    temp_case_2[case_i]["headers"] = re.sub(
                                        r'(.*)(' + this_key_list[this_key_index] + ':)(\$\{\w+\})(.*)',
                                        "\g<1>\g<2>" + str(json.loads(key_value[var_i_index][this_key_index])[
                                                               key_value_id]) + "\g<4>",
                                        temp_case_2[case_i]["headers"],
                                        re.DOTALL)
                                    temp_case_2[case_i]["params"] = re.sub(
                                        r'(.*)(' + this_key_list[this_key_index] + '=)(\$\{\w+\})(.*)',
                                        "\g<1>\g<2>" + str(json.loads(key_value[var_i_index][this_key_index])[
                                                               key_value_id]) + "\g<4>",
                                        temp_case_2[case_i]["params"],
                                        re.DOTALL)

                                    if this_key_list[this_key_index].lower().startswith("path."):
                                        temp_case_2[case_i]["PATH"] = re.sub(
                                            r'(.*)(\${' + this_key_list[this_key_index].split(".", 1)[1] + '})(.*)',
                                            "\g<1>" + str(json.loads(key_value[var_i_index][this_key_index])[
                                                              key_value_id]) + "\g<3>",
                                            temp_case_2[case_i]["PATH"],
                                            re.DOTALL)

                        # if name_add == '':
                        name_add += "_" + str(json.loads(key_value[0][0])[key_value_id])

                        temp_case_2[case_i]["name"] = str('%05d' % self.case_id) + copy.deepcopy(name_add) + (
                            " " if var_i == 0 else "_") + temp_case_2[case_i]["name"].split("_", 1)[1]
                        temp_case_2[case_i]["priority"] = var_value_prio[var_i]
                        self.case_id += 1

                    temp_case_3 += temp_case_2
                case_data += temp_case_3

        return case_data


CaseAutoCreate().create()
