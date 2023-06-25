import ast
import copy
import hashlib
import os
import random
import re
import zipfile
from json.decoder import JSONDecodeError

from Common.BaseOS import BaseOS
from Common.ConfMsg import ConfMsg
from Common.Log import Log
import json
from urllib import request
import ssl


class Assert:
    """
    断言数据：headers、body 中的数据均可断言
        headers.xx...
        body.xx...
    可支持的断言标志说明：
        eq：校验某个字段是否相等
        co: 校验某个字段是否包含某字符串
        nq：校验某个字段是否不相等
        il: 校验某个字符串是否在通过key查询出来的[]中
        tq: 校验某个字段值的类型是否与接口需求相符
        ke: 校验某个字段是否存在
    断言数据来源格式：
        body.XX.YY[0].ZZ.DD[2]...,
        实例：
            取值参数：body.A.B[0].C ； A、B、C均代表字典的键，因键B对应的值为list，故用[0]取list中0号位的值
            body json实例：
            {
                A: {
                    B: [{C：c, D：d},{...}]
                }
                ...
            }
            取值结果：c
    """

    @classmethod
    # 校验某个字段是否相等
    def eq_assert(self, data, expected):
        msg = ["【eq】校验某个字段是否相等：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]
        try:
            if expected[0] == "code":
                text = [data.status_code]
            # elif "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            #     text = self.field_special_process(this_data, expected[0])
            # elif "body" in expected[0]:
                # this_data = json.loads(data.text)
                # try:
                #     this_data = json.loads(data.text)
                # except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
                #     this_data = data.text
            else:
                text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            text = ["null" if x is None else x for x in text]
            text = [str(x) for x in text]
            for v in text:
                if v != expected[1]:
                    msg.append("Result: False")
                    return False, msg
            msg.append("Result: True")

            return True, msg
        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段是否包含某字符串
    def co_assert(self, data, expected):

        msg = ["【co】校验某个字段是否包含某字符串：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            #
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 将list中的元素转换为str,用于后期比较
            text = ["null" if x is None else x for x in text]
            text = [str(x) for x in text]

            for v in text:
                if expected[1] not in v:
                    msg.append("Result: False")
                    return False, msg
            msg.append("Result: True")
            return True, msg
        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段是否不相等
    def nq_assert(self, data, expected):
        result, msg = self.eq_assert(data, expected)
        msg[0] = "【nq】校验某个字段是否不相等："
        if result:
            msg[4] = 'Result: False'
            return False, msg
        else:
            if msg[3].find('未找到') != -1:
                return False, msg
            msg[4] = 'Result: True'
            return True, msg

    @classmethod
    # 校验某个值是否在利用key取值取出的list中，支持[*]
    def il_assert(self, data, expected):

        msg = ["【il】校验某个值是否在利用key取值取出的list中：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            #
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 将list中的元素转换为str,用于后期比较
            text = ["null" if x is None else x for x in text]
            text = [str(x) for x in text]

            if expected[1] in text:
                msg.append("Result: True")
                return True, msg
            else:
                msg.append("Result: False")
                return False, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段值的类型是否与接口需求相符，支持[*]
    def tq_assert(self, data, expected):

        msg = ["【tq】校验某个字段值的类型是否与接口需求相符：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        type_dict = {"int": int, "str": str, "float": float, "dict": dict, "list": list, "bool": bool}

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            #
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 解析预期的类型
            type_list = [type_dict[x] for x in expected[1].split(",")]
            for i in list(filter(lambda x: x is not None, text)):
                if type(i) not in type_list:
                    msg.append("Result: False")
                    return False, msg
            msg.append("Result: True")
            return True, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到所有需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到所有需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段是否存在，支持[*]
    def ke_assert(self, data, expected):
        # Log.logger("    Expected_key: {a}".format(a=expected[0]))
        # Log.logger("    Expected_value: {a}".format(a="存在" if expected[1].lower() == "true" else "不存在"))

        msg = ["【ke】校验某个字段是否存在：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a="存在" if expected[1].lower() == "true" else "不存在")]
        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a},{b}".format(a=text, b="存在"))

            if expected[1].lower() == "true":
                msg.append("Result: True")
                return True, msg
            else:
                msg.append("Result: False")
                return False, msg
        except KeyError:
            msg.append("Actual_value: {b}".format(b="不存在"))

            if expected[1].lower() == "true":
                msg.append("Result: False")
                return False, msg
            else:
                msg.append("Result: True")
                return True, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段值是否在提供的列表中，支持[*]
    def iv_assert(self, data, expected):

        msg = ["【iv】校验某个值是否在结果list中：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 将 [] 结构的字符串转换为 list
            expected_value = json.loads(expected[1].replace("'", '"'))
            for i in text:
                if i not in expected_value:
                    msg.append("Result: False")
                    return False, msg

            msg.append("Result: True")
            return True, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段值是否在提供的列表中，支持[*]
    def niv_assert(self, data, expected):

        msg = ["【niv】校验某个值不在结果list中：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 将 [] 结构的字符串转换为 list
            expected_value = ast.literal_eval(expected[1])

            for i in text:
                if i in expected_value:
                    msg.append("Result: False")
                    return False, msg

            msg.append("Result: True")
            return True, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验某个字段值是否可以为null
    def in_assert(self, data, expected):

        msg = ["【in】校验某个字段值是否可以为null：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            flag = True if expected[1] == "true" else False
            for i in text:
                if not flag and i is None:
                    msg.append("Result: False")
                    return False, msg
            msg.append("Result: True")
            return True, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验url链接是否可正常访问
    def url_assert(self, data, expected):
        ssl._create_default_https_context = ssl._create_unverified_context

        msg = ["【url】校验url是否可正常返回：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            # text = self.field_special_process(this_data, expected[0])

            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 处理掉空字符串和None
            text = list(filter(None, text))

            flag = True
            for i in text:
                try:
                    with request.urlopen(i, timeout=20) as file:
                        if expected[1] != "true":
                            flag = False
                            msg.append("Url {b} 访问正常，但预期为不能正常访问".format(b=i))
                        file.close()
                except Exception as e:
                    if expected[1] == "true":
                        flag = False
                        msg.append("\nUrl: {b} connection Error: {a}".format(a=e, b=i))
            if flag:
                msg.append("Result: True")
                return True, msg
            else:
                msg.append("Result: False")
                return False, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value:  异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验字符串是否满足规则
    def reg_assert(self, data, expected):

        msg = ["【reg】校验值是否满足规则：", "Expected_key: {a}".format(a=expected[0]),
               "Expected_value: {a}".format(a=expected[1])]

        try:
            # if "headers" in expected[0]:
            #     this_data = json.loads(str(data.headers).replace("'", '"'))
            # elif "body" in expected[0]:
            #     try:
            #         this_data = json.loads(data.text)
            #     except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
            #         this_data = data.text
            #
            # text = self.field_special_process(this_data, expected[0])
            text = self.field_special_process(data, expected[0])

            msg.append("Actual_value: {a}".format(a=text))

            # 处理掉空字符串和None
            text = list(filter(None, text))

            flag = True

            reg_str = expected[1]
            pattern = re.compile(reg_str)
            for i in text:
                m = pattern.match(i)
                if m is None:
                    flag = False
                    msg.append("\n值: {b}  正则校验未通过 {a}".format(a=reg_str, b=i))
            if flag:
                msg.append("Result: True")
                return True, msg
            else:
                msg.append("Result: False")
                return False, msg

        except KeyError:
            # Log.logger_error("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Actual_value: {a}".format(a='在返回数据中未查找到需断言的字段'))
            msg.append("Result: False")
            return False, msg
        except Exception as e:
            # Log.logger_error("Actual_value: {a}".format(a=str(e)))
            msg.append("Actual_value: 异常捕获，{a}".format(a=str(e)))
            msg.append("Result: False")
            return False, msg

    @classmethod
    # 校验2组数据是否按规则比较相同
    def cmp_assert(self, expected, var):
        ssl._create_default_https_context = ssl._create_unverified_context

        msg = ["\n【cmp】校验2组值是否在规则内相同："]

        # 开始断言检查

        # 解析规则数据
        """
        {
            "value1": ${QACMPDATA1},   # 比对数据源1
            "value2": ${QACMPDATA2},    # 比对数据源2
            "cmp_list_seq": "",     # 值为1时，无需验证结果值list顺序；值为非1时，需验证结果值list顺序
            "cmp_file": "",     # 比对文件是否相同，下载文件并hash值比对
            "cmp_filename": "",     # 仅比对文件名（如：http://a/b/a.jpg http://c/d/a.jpb）
            "value_map": [
                ["true", "1"],
                ["false","0"]
            ],      # 值结果映射（如：true 映射为1 ）,无需映射时为""
            "value_map_type": ["bool","str"]        # 值结果需映射，结果值类型说明，补充 value_map 信息
        }
        """
        value_key_json = json.loads(expected[0])
        value_key1 = value_key_json[0]
        value_key2 = value_key_json[1]

        value_reg = json.loads(expected[1])
        value1 = value_reg["value1"]
        value2 = value_reg["value2"]

        cmp_list_seq = value_reg["cmp_list_seq"]
        cmp_file = value_reg["cmp_file"]
        cmp_filename = value_reg["cmp_filename"]
        cmp_listlength = value_reg["cmp_listlength"]
        value_map = value_reg["value_map"]

        value_map_type = value_reg["value_map_type"]

        # 针对 映射中 null * 特殊处理
        value_map = [
            [x[y] if (x[y] != 'null' and value_map_type[y] == 'str') or x[y] == "*" else json.loads(x[y]) for y in
             range(0, len(x))] for x in
            value_map]

        variable_regex_compile = re.compile(r"\$\{(\w+)\}")
        m1 = variable_regex_compile.findall(value_key1)
        m1.reverse()
        m2 = variable_regex_compile.findall(value_key2)
        m2.reverse()
        result_flag = True

        # 准备测试结果数据
        msg.append(" • 字段1：{a}".format(a=value_key1))
        msg.append(" • 字段2：{a}".format(a=value_key2))

        if value_map:
            msg.append(" • 值映射关系为：{a}".format(a=value_map))

        # cmp断言比对数据
        def cmp_func(key1, key2, this_key1, this_key2, i1, i2, result_msg_fail, result_msg_pass, result_msg_empty_1,
                     result_msg_empty_2, i_index=1):
            result_flag_temp = True
            res_temp = []

            # 取值1、2
            try:
                res1 = self.field_special_process(value1, key1.replace("'", '"'))
            except KeyError:
                result_msg_fail.append("\n-----------------------✂---------------------------")
                result_msg_fail.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_fail.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_fail.append(" • 取值1：{a} 在返回数据中未查找到需断言的字段".format(a=key1.replace("'", '"')))

                result_flag_temp = False
                return result_flag_temp
            except Exception as e:
                result_msg_fail.append("\n-----------------------✂---------------------------")
                result_msg_fail.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_fail.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_fail.append(" • 取值1：异常捕获，{a} ".format(a=str(e)))

                result_flag_temp = False
                return result_flag_temp

            try:
                res2 = self.field_special_process(value2, key2.replace("'", '"'))
            except KeyError:
                result_msg_fail.append("\n-----------------------✂---------------------------")
                result_msg_fail.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_fail.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_fail.append(" • 取值2：{a} 在返回数据中未查找到需断言的字段".format(a=key2.replace("'", '"')))

                result_flag_temp = False
                return result_flag_temp
            except Exception as e:
                result_msg_fail.append("\n-----------------------✂---------------------------")
                result_msg_fail.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_fail.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_fail.append(" • 取值2：异常捕获，{a} ".format(a=str(e)))

                result_flag_temp = False
                return result_flag_temp

            # pyj ops未指定选项值类型时使用
            # res1 = [(str(x) if isinstance(x, (str, float)) or type(x) == int else x) for x in res1]
            # res2 = [(str(x) if isinstance(x, (str, float)) or type(x) == int else x) for x in res2]

            # 判断res1、res2是否有空[]
            if not res1:
                result_msg_empty_1.append("\n-----------------------✂---------------------------")
                result_msg_empty_1.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_empty_1.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_empty_1.append(" • 结果1：{a}".format(a=res1))
                result_msg_empty_1.append(" • 结果2：{b}".format(b=res2))
                result_msg_empty_1.append(" • 值-文件名比对：参考组中找不到相应数据\n")

            elif not res2:
                # result_msg_empty_2.append("\n-----------------------✂---------------------------")
                # result_msg_empty_2.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                # result_msg_empty_2.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                # result_msg_empty_2.append(" • 结果1：{a}".format(a=res1))
                # result_msg_empty_2.append(" • 结果2：{b}".format(b=res2))
                # result_msg_empty_2.append(" • 值-文件名比对：比较组中找不到相应数据\n")

                # 当res1中有值，res2也必须有此值时，打开程序
                result_flag_temp = False
                result_msg_fail.append("\n-----------------------✂---------------------------")
                result_msg_fail.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                result_msg_fail.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                result_msg_fail.append(" • 结果1：{a}".format(a=res1))
                result_msg_fail.append(" • 结果2：{b}".format(b=res2))
                result_msg_fail.append(" • 值-文件名比对：比较组中找不到相应数据\n")

            else:
                res_temp.append("\n-----------------------✂---------------------------")
                res_temp.append(" • 参数1：{a} = {b}".format(a=this_key1, b=i1))
                res_temp.append(" • 参数2：{a} = {b}".format(a=this_key2, b=i2))
                res_temp.append(" • 结果1：{a}".format(a=res1))
                res_temp.append(" • 结果2：{b}".format(b=res2))

                # 仅比对文件名的情况 取值结果list中的值必为string类型
                if cmp_filename == 1:

                    # 判断是否检查结果list的长度
                    if cmp_listlength == 1:
                        if len(res1) != len(res2):
                            result_flag_temp = False
                            res_temp.append(" • 值长度比较：{a} 【不等于】 长度{b}".format(a=len(res1), b=len(res2)))
                        else:
                            res_temp.append(" • 值长度比较：长度 {a} 【等于】 长度{b}".format(a=len(res1), b=len(res2)))

                    for j in range(0, min([len(res1), len(res2)])):
                        path1, temp1 = os.path.split(res1[j])
                        path2, temp2 = os.path.split(res2[j])

                        # pyj 处理链接有?token的情况
                        temp1 = temp1.split("?")[0]
                        temp2 = temp2.split("?")[0]

                        if temp1 != temp2:
                            result_flag_temp = False
                            res_temp.append(" • 值-文件名比对：{a} 【不等于】 {b}".format(a=temp1, b=temp2))
                        else:
                            res_temp.append(" • 值-文件名比对：{a} 【等于】 {b}".format(a=temp1, b=temp2))

                # 对于比对文件 不比对名称 返回的数据进行全值匹配比对
                elif cmp_file != 1:
                    # 映射处理
                    res1_temp = copy.deepcopy(res1)
                    res2_temp = copy.deepcopy(res2)
                    map_str = ""
                    if value_map:
                        value_map1 = [value_map[x][0] for x in range(0, len(value_map))]
                        value_map2 = [value_map[x][1] for x in range(0, len(value_map))]
                        for ii in range(0, len(res1)):

                            # 将映射后的值保存在res1_temp 用于后期比较
                            if "*" in value_map1:
                                res1_temp[ii] = (value_map2[value_map1.index("*")])

                            if "*" in value_map2:
                                for jj in range(0, len(res2)):
                                    res2_temp[jj] = (value_map1[value_map2.index("*")])


                            # 若除了*以外，仍可以使用映射将有值映射优先级是高
                            # if res1[ii] in value_map1:
                            if "*" not in value_map2 and res1[ii] in value_map1:
                                res1_temp[ii] = (value_map2[value_map1.index(res1[ii])])

                        map_str = "映射后"

                    # 比对值，无需验证list顺序
                    if cmp_list_seq != 1:

                        # 验证list长度
                        if cmp_listlength == 1:
                            if len(res1) != len(res2):
                                result_flag_temp = False
                                result_flag_temp = False
                                # result_flag = False
                                res_temp.append(
                                    " • 值长度比较：长度 {a} 【不等于】 长度{b}".format(a=len(res1), b=len(res2)))

                            else:
                                res_temp.append(
                                    " • 值长度比较：长度 {a} 【等于】 长度{b}".format(a=len(res1), b=len(res2)))

                        # if [i1 for i1 in res1_temp if i1 not in res2] + [i2 for i2 in res2 if
                        #                                                  i2 not in res1_temp] != [] or (
                        #         len(res1) != len(res2) and cmp_listlength == 1):
                        if [i1 for i1 in res1_temp if i1 not in res2_temp] + [i2 for i2 in res2_temp if
                                                                         i2 not in res1_temp] != [] or (
                                len(res1) != len(res2) and cmp_listlength == 1):
                            result_flag_temp = False

                            res_temp.append(
                                " • 值比对(list不验证顺序)：{a} {c}【不等于】 {b}".format(a=res1, b=res2, c=map_str))

                        else:
                            res_temp.append(
                                " • 值比对(list不验证顺序)：{a} {c}【等于】 {b}".format(a=res1, b=res2, c=map_str))

                    # 比对值，需验证list顺序
                    else:
                        # if res1_temp != res2:
                        if res1_temp != res2_temp:
                            result_flag_temp = False

                            res_temp.append(" • 值比对(list验证顺序)：{a} {c}【不等于】 {b}".format(a=res1, b=res2, c=map_str))

                        else:
                            res_temp.append(" • 值比对(list验证顺序)：{a} {c}【等于】 {b}".format(a=res1, b=res2, c=map_str))

                # 比对文件是+否为同一个
                if cmp_file == 1:
                    pass
                    # pyj 模板临时添加的创建文件夹 else cmp_file ==1 也是临时添加
                    # for k in range(0, len(res1)):
                    #     try:
                    #         path1, temp1 = os.path.split(res1[k])
                    #         file_name1, extension1 = os.path.splitext(temp1)
                    #         # 创建文件路径
                    #         file_temp1 = os.path.join(BaseOS().get_project_path(), "Report", temp_folder,
                    #                                   str(i_index)+"_1" + extension1)
                    #         # 下载素材
                    #         with request.urlopen(res1[k], timeout=120) as response:
                    #             if response.getcode() == 200:
                    #                 with open(file_temp1, "wb") as f:
                    #                     f.write(response.read())
                    #                     f.close()
                    #
                    #         path2, temp2 = os.path.split(res2[k])
                    #         file_name2, extension2 = os.path.splitext(temp2)
                    #         file_temp2 = os.path.join(BaseOS().get_project_path(), "Report", temp_folder,
                    #                                   str(i_index) + "_2" + extension2)
                    #         with request.urlopen(res2[k], timeout=120) as response:
                    #             if response.getcode() == 200:
                    #                 with open(file_temp2, "wb") as f:
                    #                     f.write(response.read())
                    #                     f.close()
                    #     except Exception as e:
                    #         print(e)

                    # 正式用例，暂时屏蔽
                    for k in range(0, len(res1)):
                        path1, temp1 = os.path.split(res1[k])
                        file_name1, extension1 = os.path.splitext(temp1)
                        path2, temp2 = os.path.split(res2[k])
                        file_name2, extension2 = os.path.splitext(temp2)

                        # 创建文件路径
                        file_temp1 = os.path.join(BaseOS().get_project_path(), "Report",
                                                  "file_temp1" + extension1)
                        file_temp2 = os.path.join(BaseOS().get_project_path(), "Report",
                                                  "file_temp2" + extension2)

                        try:
                            # 下载素材
                            with request.urlopen(res1[k], timeout=120) as response:
                                if response.getcode() == 200:
                                    with open(file_temp1, "wb") as f:
                                        f.write(response.read())
                                        f.close()
                                response.close()
                            with request.urlopen(res2[k], timeout=120) as response:
                                if response.getcode() == 200:
                                    with open(file_temp2, "wb") as f:
                                        f.write(response.read())
                                        f.close()
                                response.close()
                            # 以zip包中的文件进行比对
                            if extension1.lower() == '.zip' and extension2.lower() == '.zip':
                                target_path1 = os.path.join(BaseOS().get_project_path(), "Report", "file_temp1")
                                target_path2 = os.path.join(BaseOS().get_project_path(), "Report", "file_temp2")

                                # 解压文件
                                z1 = zipfile.ZipFile(file_temp1, 'r')
                                z1.extractall(target_path1)
                                z2 = zipfile.ZipFile(file_temp2, 'r')
                                z2.extractall(target_path2)
                                z1.close()
                                z2.close()

                                # 处理中文文件名
                                BaseOS().get_all_dirs_and_files(path=target_path1)
                                BaseOS().get_all_dirs_and_files(path=target_path2)

                                root1, dirs1, files1 = list(os.walk(target_path1))[0]
                                root2, dirs2, files2 = list(os.walk(target_path2))[0]

                                dirs1 = list(filter(lambda x: x != '__MACOSX', dirs1))
                                dirs2 = list(filter(lambda x: x != '__MACOSX', dirs2))

                                # 判断解压后是否仅一个目录
                                if len(dirs1) == 1 and len(dirs1) == 1 and len(files1) == 0 and len(files2) == 0:
                                    target_path1_temp = os.path.join(target_path1, dirs1[0])
                                    target_path2_temp = os.path.join(target_path2, dirs2[0])

                                    # 临时处理、用于处理获取一个目录下某一文件的特殊处理，定制代码，特定情况使用，平时不用使用 （艺术滤镜对照表中特效sheet使用）
                                    # target_path2_temp = target_path2

                                    if dirs1[0] != dirs2[0]:
                                        pass
                                        # result_flag_temp = False
                                        # res_temp.append(" • 解压后主文件目录不相同： {a}【不等于】{b} ".format(a=dirs1[0], b=dirs2[0]))
                                else:
                                    target_path1_temp = target_path1
                                    target_path2_temp = target_path2

                                d_f_1 = BaseOS().get_all_dirs_and_files(path=target_path1_temp)
                                d_f_2 = BaseOS().get_all_dirs_and_files(path=target_path2_temp)

                                # 比对文件目录是否相同
                                m_1 = [x.replace(target_path1_temp, "") for x in d_f_1]
                                m_2 = [x.replace(target_path2_temp, "") for x in d_f_2]

                                # 临时处理 字体 font_前缀的问题
                                # m_2 = [x.replace("/", "/font_") if re.match(r'^.+\.(ttf|ttc|otf|otc)$', x) else x for x
                                #        in m_2]

                                dif_file1 = [x for x in m_1 if x not in m_2]
                                dif_file2 = [x for x in m_2 if x not in m_1]

                                if dif_file1:
                                    result_flag_temp = False
                                    res_temp.append(" • 参考组ZIP文件中比对比组多了如下数据： {a} ".format(a=dif_file1))

                                if dif_file2:
                                    result_flag_temp = False
                                    res_temp.append(" • 对比组ZIP文件中比参考组多了如下数据： {a} ".format(a=dif_file2))

                                # 比对2个zip文件中均存在的文件hash
                                hash_target = list(set(m_1).intersection(set(m_2)))
                                for hash_target_i in hash_target:
                                    temp_1 = target_path1_temp + hash_target_i

                                    temp_2 = target_path2_temp + hash_target_i

                                    # 临时处理 字体 font_前缀的问题
                                    # temp_2 = target_path2_temp + (
                                    #     re.sub(r'font_', "", hash_target_i) if re.match(r'^.+\.(ttf|ttc|otf|otc)$',
                                    #                                                     hash_target_i) else hash_target_i)

                                    if not os.path.isdir(temp_1):
                                        # 计算文件hash
                                        hasher1 = hashlib.md5()
                                        afile1 = open(temp_1, 'rb')
                                        buf1 = afile1.read()
                                        hasher1.update(buf1)
                                        hash_1 = str(hasher1.hexdigest())

                                        hasher2 = hashlib.md5()
                                        afile2 = open(temp_2, 'rb')
                                        buf2 = afile2.read()
                                        hasher2.update(buf2)
                                        hash_2 = str(hasher2.hexdigest())

                                        afile1.close()
                                        afile2.close()

                                        if hash_1 == hash_2:
                                            res_temp.append(" • 文件hash值 {c} ：{a} 【等于】 {b}".format(a=hash_1, b=hash_2,
                                                                                        c=hash_target_i))
                                        else:
                                            result_flag_temp = False
                                            res_temp.append(" • 文件hash值 {c} ：{a} 【不等于】 {b}".format(a=hash_1, b=hash_2,
                                                                                         c=hash_target_i))
                                # 删除文件
                                BaseOS().clear_folder(root_path=target_path1, ignore_type=[])
                                BaseOS().clear_folder(root_path=target_path2, ignore_type=[])
                                os.rmdir(target_path1)
                                os.rmdir(target_path2)
                                os.remove(file_temp1)
                                os.remove(file_temp2)

                            # 非zip文件直接比对
                            else:
                                # 计算文件hash
                                hasher1 = hashlib.md5()
                                afile1 = open(file_temp1, 'rb')
                                buf1 = afile1.read()
                                hasher1.update(buf1)
                                hash_1 = str(hasher1.hexdigest())

                                hasher2 = hashlib.md5()
                                afile2 = open(file_temp2, 'rb')
                                buf2 = afile2.read()
                                hasher2.update(buf2)
                                hash_2 = str(hasher2.hexdigest())

                                afile1.close()
                                afile2.close()

                                # 删除文件
                                os.remove(file_temp1)
                                os.remove(file_temp2)

                                if hash_1 == hash_2:
                                    res_temp.append(" • 文件hash值：{a} 【等于】 {b}".format(a=hash_1, b=hash_2))
                                else:
                                    result_flag_temp = False
                                    res_temp.append(" • 文件hash值：{a} 【不等于】 {b}".format(a=hash_1, b=hash_2))

                        except Exception as e:
                            if res1[k] == "" and res2[k] == "" and result_flag_temp:
                                result_flag_temp = True
                            else:
                                result_flag_temp = False
                            res_temp.append(" • 素材下载失败无法比对: {a},{b}".format(a=res1[k], b=res2[k]))

                            # 当出现异常时，判断下载、解压的文件是否存在，存在则删除
                            for f in [file_temp1, file_temp2]:
                                if os.path.exists(f):
                                    path, temp = os.path.split(f)
                                    file_name, extension = os.path.splitext(temp)
                                    if os.path.exists(os.path.join(path, file_name)):
                                        BaseOS().clear_folder(root_path=os.path.join(path, file_name), ignore_type=[])
                                        os.rmdir(os.path.join(path, file_name))
                                    os.remove(f)

            if not result_flag_temp:
                result_msg_fail += res_temp
            else:
                result_msg_pass += res_temp

            return result_flag_temp

        # 若目标字段有参数值时
        if m1 and m2:
            for this_key_index in range(0, len(m1)):
                this_key1 = m1[this_key_index]
                this_key2 = m2[this_key_index]
                # for this_key1 in m1:
                result_msg_pass = []
                result_msg_fail = []
                result_msg_empty_1 = []
                result_msg_empty_2 = []

                # 当参数对应的值不是list时，处理为list
                if var[this_key1].startswith("[") and var[this_key1].endswith("]"):
                    this_key_var_value1 = json.loads(var[this_key1])
                else:
                    this_key_var_value1 = [var[this_key1]]

                if var[this_key2].startswith("[") and var[this_key2].endswith("]"):
                    this_key_var_value2 = json.loads(var[this_key2])
                else:
                    this_key_var_value2 = [var[this_key2]]

                # pyj 临时代码段 模板临时添加的创建文件夹
                temp_folder = str(random.randint(0, 1000)) + "_" + str(random.randint(0, 1000))
                if not os.path.exists(os.path.join(BaseOS().get_project_path(), "Report", temp_folder)):
                    os.makedirs(os.path.join(BaseOS().get_project_path(), "Report", temp_folder))

                # 开始遍例比对指定key中每一个值的数据
                for i_index in range(0, len(this_key_var_value1)):

                    i1 = this_key_var_value1[i_index]
                    i2 = this_key_var_value2[i_index]

                    reg = re.compile(r"(.*)(\$\{\w+\})(.*)")
                    if isinstance(i1, str):
                        i1 = "'" + i1 + "'"
                    if isinstance(i2, str):
                        i2 = "'" + i2 + "'"
                    key1 = reg.sub(r'\g<1>' + i1 + r'\g<3>', value_key1)
                    key2 = reg.sub(r'\g<1>' + i2 + r'\g<3>', value_key2)

                    # 执行比较
                    if not cmp_func(key1, key2, this_key1, this_key2, i1, i2, result_msg_fail, result_msg_pass,
                                    result_msg_empty_1, result_msg_empty_2, i_index):
                        result_flag = False

                # 临时代码段 ，提交前需删除，用于模板
                ccc = list(os.walk(os.path.join(BaseOS().get_project_path(), "Report", temp_folder)))
                if ccc[0][1] == [] and ccc[0][2] == []:
                    os.rmdir(os.path.join(BaseOS().get_project_path(), "Report", temp_folder))

                # msg中添加数据
                msg += result_msg_fail
                msg += result_msg_empty_1
                msg += result_msg_empty_2
                msg += result_msg_pass

                msg.append("\n=======================✂===========================")
                msg.append("【参数值】")
                msg.append(" • {a}={b}\n".format(a=this_key1, b=var[this_key1]))
                msg.append(" • {a}={b}\n".format(a=this_key2, b=var[this_key2]))

        else:
            result_msg_pass = []
            result_msg_fail = []
            result_msg_empty_1 = []
            result_msg_empty_2 = []

            key1 = value_key1
            key2 = value_key2
            # 执行比较
            if not cmp_func(key1, key2, "无需参数", "无需参数", "None", "None", result_msg_fail, result_msg_pass,
                            result_msg_empty_1, result_msg_empty_2):
                result_flag = False
            # msg中添加数据
            msg += result_msg_fail
            msg += result_msg_empty_1
            msg += result_msg_empty_2
            msg += result_msg_pass

        if result_flag:
            msg.append("Result: True")
        else:
            msg.append("Result: False")
        return result_flag, msg

    @classmethod
    # 处理[]{}的逻辑 【。。。已抛弃。。。。】
    def special_process(self, text, field_list):
        # text 为传为了初始返回体字典，即初始查找数据体
        # filed_list 为断言的目标字段 list （以用例中断言进行.分割后的list)

        list_flag = False  # 标记是否为list

        # 遍例 断言的目标字段 list
        for field_list_index in range(1, len(field_list)):
            key = field_list[field_list_index]
            # print("--------==============", key)
            # print("--------((((((((((((((", text)

            # 若仍有后续字段需要获取，但此时可校验数据全为None时,即不可能再往后查询，
            if text is None:
                raise Exception("值为null，找不到相应字段")

            if isinstance(text, list):
                for i in text:
                    if i is None:
                        raise Exception("值为null，找不到相应字段")

            # 判断 【供查找数据体text】 是否为 list （初始text 传入时为 字典）
            # (每一个【遍例 断言的目标字段 list】for循环均根据当前字段目标获取值后更新一次text)
            # 【供查找数据体text】 为list时，读取list中的每一个值，进行当前key字段获取后续值后，继续保存为新的list
            if isinstance(text, list):
                text_temp = []

                # 遍例 【供查找数据体text】list
                for j in text:
                    value_flag = False  # 标记是否使用了 {value:} {isnot:} {keyexist:} 字段值/字段校验
                    value_type_flag = 0  # 标记 value_flag为True时，使用的类型 0：{value:}， 1：{isnot:}， 2：{keyexist:}

                    # 判断是否为 字段X[*/数字] 取值（包含[，且没有{},用于排除其它字段判断类型比如：guid{"value":[""]}）
                    # if '[' in key and len(key.split("{")) == 1:
                    if '[' in key and "{" not in key:
                        keytemp = key.split("[")

                        # 为[*]时，将 "字段X" 赋值于key2
                        if '*' in keytemp[1]:
                            key2 = keytemp[0]
                            # print("------------@@@@@@@@", key2)

                        # 为[数字]时，需取出当前字段的值，赋值给j；并取出[数字]中的数字赋值key2,以便后续取出值中的对应序列的值
                        else:
                            key2 = int(keytemp[1].replace("[", "").replace("]", ""))
                            j = j[keytemp[0]]
                            # print("------------@@@@@@@@", key2)
                            # print("-------------jjjjjjjjj",j)

                    # 判断是否 包含 {} 时，获取{}中的键值赋值给 value，同时设置 value_type_flag、 value_flag
                    elif '{' in key:
                        keytemp2 = key.split("{")
                        key2 = keytemp2[0]
                        v_json = json.loads("{" + keytemp2[1])
                        if "value" in v_json.keys():
                            value = v_json["value"]
                        if "isnot" in v_json.keys():
                            value = v_json["isnot"]
                            value_type_flag = 1
                        if "keyexist" in v_json.keys():
                            value = v_json["keyexist"]
                            value_type_flag = 2
                        value_flag = True
                        # print(key2, value)

                    # 此时 key 为单存的字段，无[]、{}在字段中
                    else:
                        key2 = key

                    # 当前key中没有{}
                    if not value_flag:
                        # print("-----------------*******", j[key2])
                        # 此时的key2 可能是一个[数字]中的数字、字段字符串
                        # 若j[key2]取出的是一个list,将list中的每一个值单独取出拼接为新的list（因为后续会针对每一个值进行新的字段校验取值）
                        # 标记 list_flag=true 最后取出的值为list，以保障后后续字段取值循环将每一个值都遍例到
                        if isinstance(j[key2], list):
                            if field_list_index == len(field_list) - 1 and "*" not in key:
                                text_temp.append(j[key2])
                                list_flag = True
                            else:
                                for k in j[key2]:
                                    text_temp.append(k)
                                    list_flag = True
                        else:
                            text_temp.append(j[key2])
                            list_flag = True

                    # 当前key中有{}
                    else:
                        # value
                        if value_type_flag == 0:
                            # if key2 in j.keys() and j[key2] == value:
                            if key2 in j.keys() and j[key2] in value:
                                text_temp.append(j)
                                list_flag = True

                        # isnot
                        elif value_type_flag == 1:
                            # if key2 in j.keys() and j[key2] != value:
                            if key2 in j.keys() and j[key2] not in value:
                                text_temp.append(j)
                                list_flag = True

                        # keyexist
                        elif value_type_flag == 2:
                            if key2 in j.keys() and value == True:
                                text_temp.append(j)
                                list_flag = True
                            elif key2 not in j.keys() and value == False:
                                text_temp.append(j)
                                list_flag = True
                        list_flag = True

                # 将当前字段取出的值 赋值给 text， 进入下一个循环，进入新的取值校验
                text = text_temp
                # print("-------------$$$$$$$$$$", text)

            # 如果 text 不为 list时
            else:
                value_flag = False
                value_type_flag = 0  # True "value"
                # if '[' in key and len(key.split("{")) == 1:
                if '[' in key and "{" not in key:
                    keytemp = key.split("[")
                    if '*' in keytemp[1]:
                        key = keytemp[0]
                    else:
                        key = int(keytemp[1].replace("[", "").replace("]", ""))
                        text = text[keytemp[0]]
                        # print(key, text)
                elif '{' in key:
                    keytemp2 = key.split("{")
                    key2 = keytemp2[0]

                    v_json = json.loads("{" + keytemp2[1])
                    if "value" in v_json.keys():
                        value = v_json["value"]
                    if "isnot" in v_json.keys():
                        value = v_json["isnot"]
                        value_type_flag = 1
                    if "keyexist" in v_json.keys():
                        value = v_json["keyexist"]
                        value_type_flag = 2
                    value_flag = True

                    # value = json.loads("{" + keytemp2[1])["value"]
                    # value_flag = True

                if not value_flag:
                    text = text[key]
                else:
                    if value_type_flag == 0:
                        if value == text[key2]:
                            text = text
                    elif value_type_flag == 1:
                        if value != text[key2]:
                            text = text
                    elif value_type_flag == 2:
                        if key2 in text.keys() and value == True:
                            text = text
                        elif key2 not in text.keys() and value == False:
                            text = text
                        else:
                            text = []
            # print(text)
            # else:  # 处理需要取子字段，但是返回数据非字典，返回一个[]时的异常
            #     raise KeyError("数组没有可查找的字段")
        if list_flag is not True:
            text = [text]

        return text

    @classmethod
    # 处理[] {} 逻辑总方法
    def field_special_process(self, data, field):
        """
        处理 [] {} 逻辑的总方法

        :param field: 例如：body[*].data.locale
        :param data: 返回数据转换为的字典，即初始查找数据体
        :param field_list: 需 查询的 字段 list
        :return: list 字段查找出的结果组成的list
        """
        this_data = ""

        if "headers" in field:
            this_data = json.loads(str(data.headers).replace("'", '"'))

        elif "body" in field:
            try:
                if type(data) != dict:
                    this_data = json.loads(data.text)
                else:
                    this_data = data
            except JSONDecodeError:  # 解决data.text 值为"xxx"字符串的情况，无法json.loads
                this_data = data.text

        # data = this_data

        # 初始结果为 response返回体文本字符串通过json.loads()转换为相应的类型，比如dict、list
        result = {'body': this_data}

        # 获取字段列表 field 例如：body[*].data.locale
        # field_list = field.split('.')
        # m = re.findall(r'([\w-]+\{.+\})|([\w-]+\[(\d+|\*)\])|([\w-]+)', field)
        m = re.findall(r'([\w-]+\{[^{]*\})|([\w-]+\[(\d+|\*)\])|([\w-]+)', field)
        field_list = [list(filter(None, x))[0] for x in m]

        # 遍例 断言的目标字段 list
        for field_list_index in range(0, len(field_list)):
            # 获取 查询的字段
            key = field_list[field_list_index]

            # 正则判断是为 key, 无[]、{}
            m = re.search(r'^([\w-]+)$', key)
            if m:
                result = self.field_value_brackets(result, m.group(1))

            # 正则判断是否为 key[数字/*]
            m = re.search(r'^([\w-]+)\[(\d+|\*)\]$', key)
            if m:
                result = self.field_value_brackets(result, m.group(1), m.group(2))

            # 正则判断是否为 key{}
            m = re.search(r'^([\w-]+)(\{.+\})$', key)
            if m:
                result = self.field_value_braces(result, m.group(1), m.group(2))

        # # 处理null值的情况，最终考虑不将None
        # result = ["null" if x is None else x for x in result]
        return result

    @classmethod
    # 处理key, key[*/数字]取值
    def field_value_brackets(self, target_data, key, index=None):
        """
        处理key[*/数字]取值

        :param target_data: 查询的目标数据，可能为 dict，list, 或者其它数据类型（如 str, int, bool...）
        :param key: 字段名
        :param index: None时，表示直接取字段的值，若index为*、数字时必须传值进入
        :return: [] 此字段查询出的结果组成的list
        """

        # 判断 target_data类型
        target_data_type = type(target_data)
        result = []

        # 目标数据 不为 列表，直接取值
        if target_data_type is not list:
            target_data = [target_data]

        # 目标数据为 列表，遍例取值
        for target_data_item in target_data:
            value = target_data_item[key]

            # 如果index 为数字，则取 值中对应下标的值
            if not (index is None or index == '*'):
                value = value[int(index)]

            # 当 index 是None时，不取下标，表示直接取值做为后续字段查询
            # if index is None and type(value) != list:
            if index is None:
                result.append(value)
            # 当 index 为数字 或 * 时，需直接list拼接，表示里面的每一个值都要用于后续查询，但若值不为list时，不能和list拼接，使用添加
            elif type(value) == list:
                result += value
            else:
                result.append(value)
        return result

    @classmethod
    # 处理 key{} 筛值
    def field_value_braces(self, target_data, key, condition):
        """
        处理 key{} 筛值

        :param target_data: 需按照condition条件筛值的目标数据，可能为 dict，list
        :param key: 筛值的目标字段
        :param condition: 条件:{"value/isnot/keyexist": []/str/int/bool/float... }
        :return: list 此字段筛选出的结果组成的list
        """

        # 判断 target_data类型
        target_data_type = type(target_data)

        # 获取条件数据
        condition_json = json.loads(condition)

        # 获取是否为子字段判断
        sub_key_list = []
        if "subKey" in list(condition_json.keys()):
            sub_key_list = condition_json["subKey"].split(".")

        condition_key = list(filter(lambda x: x != "subKey", list(condition_json.keys())))[0]
        condition_value = condition_json[condition_key]

        # 处理 value/isnot/keyexist: 1 修改为value/isnot/keyexist:[1] 的标准形式
        if type(condition_value) is not list or condition_value == []:
            condition_value = [condition_value]

        result = []

        # 若 value 不为list，如 "value":0 修改为 "value":[0]，兼容用例多种输写方式
        if target_data_type is not list:
            target_data = [target_data]

        for target_data_item in target_data:

            if condition_key == 'value':
                # 获取校验所需要的值
                key_value = target_data_item[key]
                if sub_key_list:
                    for sub_key_i in sub_key_list:
                        key_value = key_value[sub_key_i]

                # 校验
                if key_value in condition_value:
                    result.append(target_data_item)

            elif condition_key == 'isnot':
                # 获取校验所需要的值
                key_value = target_data_item[key]

                if sub_key_list:
                    for sub_key_i in sub_key_list:
                        key_value = key_value[sub_key_i]

                # 校验
                if key_value not in condition_value:
                    result.append(target_data_item)

            elif condition_key == 'keyexist':
                key_exist = key in target_data_item.keys()
                if sub_key_list and key_exist:
                    key_value = target_data_item[key]
                    for sub_key_i in sub_key_list:
                        if sub_key_i not in key_value.keys():
                            key_exist = False
                            break
                        else:
                            key_value = key_value[sub_key_i]

                if True in condition_value and key_exist:
                    result.append(target_data_item)
                if False in condition_value and not key_exist:
                    result.append(target_data_item)
            else:
                # 当条件错误时，不做筛选
                result.append(target_data_item)
        return result

    @classmethod
    # 多种断言的集合
    def assertion(self, data, expected, var):
        """

        :param data: response 数据
        :param expected: 类型：list[list,list...]
        :return: True、False
        """
        result = []
        error_msg = []
        com_flag = True
        for i in expected:  # 校验接口返回,返回结果是一个以True或False的列表
            for k, v in i.items():
                if k == "eq":
                    # Log.logger("Equal Assert!!! Expected_value =Actual_value ... ")
                    flag, msg = self.eq_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "co":
                    # Log.logger("Contain Assert!!! Actual_value contains Expected_value ... ")
                    flag, msg = self.co_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "nq":
                    # Log.logger("Not Equal Assert!!! Expected_value !=Actual_value ... ")
                    flag, msg = self.nq_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == 'il':
                    # Log.logger("In List Assert!!! Expected_value in [*] ... ")
                    flag, msg = self.il_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == 'tq':
                    # Log.logger("TypeEqual Assert!!! Expected_value = Actual_value ... ")
                    flag, msg = self.tq_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "ke":
                    # Log.logger("TypeEqual Assert!!! Expected_value =Actual_value ... ")
                    flag, msg = self.ke_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "iv":
                    # Log.logger("In Value Assert!!! Expected_value in Actual_value( [...] ) ... ")
                    flag, msg = self.iv_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "niv":
                    # Log.logger("Not In Value Assert!!! Expected_value not in Actual_value( [...] ) ... ")
                    flag, msg = self.niv_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "in":
                    # Log.logger("Is Null Assert!!! Expected_value can it be null ... ")
                    flag, msg = self.in_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "url":
                    # Log.logger("Url Connection Assesrt!!! URL can be connection ... ")
                    flag, msg = self.url_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "reg":
                    # Log.logger("Regular Connection Assesrt!!!  ... ")
                    flag, msg = self.reg_assert(data, v)
                    result.append(flag)
                    error_msg.append(msg)
                elif k == "cmp":
                    # Log.logger("Compare Assesrt!!!  ... ")
                    flag, msg = self.cmp_assert(v, var)
                    result.append(flag)
                    error_msg.append(msg)
        for i in result:  # 对断言列表进行校验,只要含有Flase测试结果就为False
            if i == False:
                com_flag = False
                # Log.logger("Assert: {a}".format(a=com_flag), level='critical')
                break
        # Log.logger("Assert: {a}".format(a=com_flag))

        # 获取 assert_msg 值
        assert_msg = ConfMsg().get_Assert_Msg()
        assert_msg = assert_msg.capitalize() if assert_msg.lower() in ["all", "failed"] else "All"

        if assert_msg == 'Failed':
            error_msg = [x for x in error_msg if "Result: True" not in x]

        return com_flag, error_msg
