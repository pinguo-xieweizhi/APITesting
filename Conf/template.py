import copy
import gc

import pytest
import os
from Common.BaseData import BaseData
from Common.BaseRequest import BaseRequest
from Common.ConfMsg import ConfMsg
from Common.Log import Log
from Common.YamlAnalysis import YamlAnalysis
from Common.Assert import Assert
# from Common.SigCal import SigCal
import allure
import re
import sys

if sys.platform == 'darwin':
    from Common.SigCal_MAC import SigCal
elif sys.platform == 'linux':
    from Common.SigCal_LINUX import SigCal
else:
    from Common.SigCal_WIN import SigCal


# 从yaml文件中获取并解析出标准格式的测试用例
# test_data = [(name, method, url, headers, params, validate, export),()...]
this_file_path = os.path.realpath(__file__)
obj = YamlAnalysis(BaseData().get_data_path(this_file_path))
test_data, timeout = obj.test_data()

# 获取报告所需的feature名称
a, b = os.path.split(this_file_path)
feature_name = a.split(os.path.sep)[-1]
# suite_name = a.split(os.path.sep)[-2]

# 优先级
serverity = ['trivial', 'minor', 'normal', 'critical', 'blocker']

"""
5 - blocker级别：中断缺陷（客户端程序无响应，无法执行下一步操作）
4 - critical级别：临界缺陷（ 功能点缺失）
3 - normal级别：普通缺陷（数值计算错误）
2 - minor级别：次要缺陷（界面错误与UI需求不符）
1 - trivial级别：轻微缺陷（必输项无提示，或者提示不规范）
"""


@allure.feature(feature_name)
class TestDispatcher:
    @pytest.fixture(scope="class", autouse=True)
    def class_logging(self):
        Log.logger("Start Class...")
        yield
        Log.logger("Finish Class...")

    @pytest.fixture(autouse=True)
    def method_logging(self):
        Log.logger("Start Method...")
        yield
        Log.logger("Finish Method...")

    @allure.step("step1: 获取Global_Var参数")
    def set_globalVar(self):
        global_var = obj.Global_Var
        var = obj.var
        if global_var is not None:
            text = '<font size="2" color="green">' + \
                   "<li>Global_Var:</li>" + str("<br>".join([str(x)+" = " + str(global_var[x]) for x in global_var.keys()])) + "<br><br>"
        else:
            text = '<font size="2" color="green">' + "<li>Global_Var: </li>"+"无<br><br>"
        # text += "<li>Var:</li>" + str("<br>".join([str(x)+" = " + str(var[x]) for x in var.keys()]))  + "<br><br>"

        allure.attach(text, attachment_type=allure.attachment_type.HTML)

    @allure.step("step2: 设置<url>参数")
    def set_url(self, url):
        try:
            # -------------------* 设置<请求头>参数 *---------------------
            url = obj.get_var({"url": url})["url"]  # 判断请求头中是否有变量,有的话需获取变量值

            # -------------------* 设置allure结果数据、日志 *---------------------
            allure.attach(
                '<font size="2" color="green">' + "<br>" + url,
                '设置后的<url>：', attachment_type=allure.attachment_type.HTML)
            return True, url
        except (KeyError, TypeError) as e:
            return False, e

    @allure.step("step3: 设置<请求头>参数")
    def set_headers(self, headers):
        try:
            # -------------------* 设置<请求头>参数 *---------------------
            headers = obj.get_var(headers)  # 判断请求头中是否有变量,有的话需获取变量值

            # -------------------* 设置allure结果数据、日志 *---------------------
            allure.attach(
                '<font size="2" color="green">' + "<br>".join([i + "=" + str(headers[i]) for i in headers.keys()]),
                '设置后的<请求头>：', attachment_type=allure.attachment_type.HTML)
            return True, headers
        except (KeyError, TypeError) as e:
            return False, e

    @allure.step("step1-1: 从参数中获取供应用使用的response body数据")
    def set_data(self, data):
        try:
            data = obj.get_var(data)  # 判断请求消息体中是否有变量,有的话需获取变量值

            # -------------------* 设置allure结果数据、日志 *---------------------

            # text = '<font size="2" color="green">' + \
            #        "<li>Get status_code:</li>" + str(data.status_code) + "<br><br>" + \
            #        "<li>Get headers:</li>" + str(data.headers) + "<br><br>" + \
            #        "<li>Get body:</li>" + str(data.text) + "<br><br>"
            # allure.attach(text, '从参数中拼出的Response数据：', attachment_type=allure.attachment_type.HTML)

            allure.attach('<font size="2">请到获取response数据的用例查看', '从参数中拼出的Response数据：', attachment_type=allure.attachment_type.HTML)

            return True, data
        except (KeyError, TypeError) as e:
            return False, e

    @allure.step("step4: 设置<请求体>参数")
    def set_parmars(self, params):
        try:
            params = obj.get_var(params)  # 判断请求消息体中是否有变量,有的话需获取变量值

            # -------------------* 设置allure结果数据、日志 *---------------------
            allure.attach(
                '<font size="2" color="green">' + '<br>'.join([i + "=" + str(params[i]) for i in params.keys()]),
                '设置后的<请求体> ', attachment_type=allure.attachment_type.HTML)
            return True, params
        except (KeyError, TypeError) as e:
            return False, e

    @allure.step("step: 设置<请求头>Content_Length参数")
    def set_content_length(self, headers, parmas):

        # -------------------* 设置<请求头>Content_Length 参数 *---------------------
        headers = obj.get_content_length(headers, parmas)

        # -------------------* 设置allure结果数据、日志 *---------------------
        allure.attach(
            '<font size="2" color="green">' + "<br>".join([i + "=" + str(headers[i]) for i in headers.keys()]),
            '设置后的<请求头>：', attachment_type=allure.attachment_type.HTML)
        return headers

    @allure.step("step5: 设置请求体中<sig>参数")
    def set_sig(self, method, url, headers, params, sig, env):
        sig_c = SigCal()
        if sig != 0:
            headers, params = sig_c.sig_cal(method, url, headers, params, sig, env)

        # -------------------* 设置allure结果数据、日志 *---------------------
        text = '<font size="2" color="green">请求头：<br>'
        text += "<br>".join([i + "=" + str(headers[i]) for i in headers.keys()])
        text += "<br><br>请求体：<br>"
        text += "<br>".join([i + "=" + str(params[i]) for i in params.keys()])

        allure.attach(text, '设置后的<请求头、体> ', attachment_type=allure.attachment_type.HTML)
        return headers, params

    @allure.step("step6: 发起请求")
    def request(self, url, method, params, encryption, headers, timeout):
        # -------------------* 发起请求 *---------------------
        data = BaseRequest().base_request(url=url, method=method, params=params, encryption=encryption,
                                          headers=headers, timeout=timeout)
        if not isinstance(data, str):
            # -------------------* 设置allure结果数据、日志 *---------------------
            text = '<font size="2" color="green">' + \
                   "<li>status_code:</li>" + str(data.status_code) + "<br><br>" + \
                   "<li>headers:</li>" + str(data.headers) + "<br><br>" + \
                   "<li>body:</li>" + str(data.text) + "<br><br>"
            allure.attach(text, 'Response数据：', attachment_type=allure.attachment_type.HTML)
        return data

    @allure.step("step7: export取值")
    def get_var_from_response(self, export, data):
        if export == "NULL":  # 接口返回是否需要输出变量供其他接口使用
            allure.attach('<font size="2"><br>无需获取参数', attachment_type=allure.attachment_type.HTML)
            # allure.attach('<font size="2"><br>无需获取参数' + '<br><br>当前参数情况：<br>' + str(obj.var), '获取情况：',
            #               attachment_type=allure.attachment_type.HTML)
            return True, ""
        else:
            text = '<p><font size="2" color="green">需要取出的值为：</p> <li><font size="2" color="black">'
            text += '<li><font size="2" color="black">'.join(
                [i + " ：" + str(export[i]) + "</li>" for i in export.keys()])

            # -------------------* 设置 Var *---------------------
            try:
                obj.set_var(export, data)

                text += '<p><font size="2" color="green">取出值为:</p><li><font size="2" color="black">'
                text += '<li><font size="2" color="black">'.join(
                    [i + "=" + (str(export[i]) if i != "QARESDATA" else "请从取response body中获取") + "</li>" for i in export.keys()])
                # (str(export[i]) if i != "QARESDATA" else "请从取response用例中获取") 处理内存问题做的特殊处理
                # text += '<br><br>当前参数情况：<br>' + str(obj.var)
                allure.attach(text, '获取情况：', attachment_type=allure.attachment_type.HTML)

                return True, ""
            except (KeyError, TypeError) as e:
                return False, e

    @allure.step("step8: 设置<断言>中的参数")
    def set_expected(self, expected):
        try:
            expected = obj.get_var(expected)  # 判断请求消息体中是否有变量,有的话需获取变量值

            # -------------------* 设置allure结果数据、日志 *---------------------
            allure.attach(
                '<font size="2" color="green">' + '<br><br><br>'.join(
                    [str(i) for i in expected]),
                '设置后的<断言> ', attachment_type=allure.attachment_type.HTML)
            return True, expected
        except (KeyError, TypeError) as e:
            return False, e

    @allure.step("step9: 断言")
    def mul_assert(self, data, expected):
        # -------------------* 断言 *---------------------
        com_flag, error_msg = Assert.assertion(data, expected, obj.var)

        # 获取 assert_msg 值
        assert_msg = ConfMsg().get_Assert_Msg()
        assert_msg = assert_msg.capitalize() if assert_msg.lower() in ["all", "failed"] else "All"

        # -------------------* 设置allure结果数据、日志 *---------------------
        text = '<font size="2" color="green">'
        if com_flag:
            text += "最终结果：" + str(com_flag) + "<br>"
        else:
            text += '<font color="red">' + "最终结果：" + str(com_flag) + "<br>"

        if assert_msg == "Failed":
            text += '<br><br>'.join(list(filter(lambda msg: False if msg.endswith("Result: True") else True, ['<br>'.join(x) for x in error_msg])))
        else:
            text += '<br><br>'.join(['<br>'.join(x) for x in error_msg])
        allure.attach(text, '断言结果：', attachment_type=allure.attachment_type.HTML)

        assert com_flag, '\n' + '\n\n'.join(list(filter(lambda msg: False if msg.endswith("Result: True") else True,
                                                        ['\n'.join(x) for x in error_msg]))) + '\n'

    def teardown_class(self):
        obj = None
        test_data = None
        gc.collect()

    @pytest.mark.parametrize("name, priority, encryption, sig, env, method, url, headers, params, expected, export",
                             test_data)
    def test_api(self, name, priority, encryption, sig, env, method, url, headers, params, expected, export):

        allure.dynamic.story("{i}".format(i=name))  # 设置用例story名
        allure.dynamic.severity(serverity[(priority - 1) if priority <= 5 else 4])  # 设置用例优先级
        allure.dynamic.title("{i}".format(i=url))  # 设定用例标题
        allure.dynamic.description("{i}".format(i=name))  # 设定用例描述

        Log.logger("开始执行用例：" + str(name))
        Log.logger("Request url:" + str(url))

        # 获取Global_Var参数
        self.set_globalVar()

        # 当url不为NULL 与 ${key}
        url_re = re.findall(r'(\$\{\w+\})', url)

        # url_re2 = re.match(r'^https?://([0-9a-zA-Z\-._]*\/)*', url)
        # 修复 url链接中带有参数的情况
        url_re2 = re.match(r'^https?://([\w\-.=${}&?]*\/*)*', url)

        # 若 url 不为纯参数（如：非${QADATA}）
        if url_re2:
            # 当url中带有参数时，给url添加参数
            if url_re:
                urs_flag, url = self.set_url(url)
                if not urs_flag:
                    assert False, "url：参数获取失败\r\n Error: {a}".format(a=headers)

            # 设置请求头、请求体
            # 设置 var ${}参数
            hrs_flag, headers = self.set_headers(headers)
            prs_flag, params = self.set_parmars(params)

            if not hrs_flag:
                assert False, "请求头headers：参数获取失败\r\n Error: {a}".format(a=headers)

            elif not prs_flag:
                assert False, "请求体params：参数获取失败\r\n Error: {a}".format(a=params)

            # 设置签名
            headers, params = self.set_sig(method, url, headers, params, sig, env)

            # 设置 header 中Content_length
            # headers = self.set_content_length(headers, params)

            # Log.logger("Request Headers:" + str(headers))
            # Log.logger("Request Body:" + str(params))

            # 发起请求
            data = self.request(url=url, method=method, params=params, encryption=encryption,
                                headers=headers, timeout=timeout)
            if not isinstance(data, str):

                # 获取返回中的数据供后续用例使用
                grs_flag, e_msg = self.get_var_from_response(copy.deepcopy(export), data)
                if not grs_flag:
                    assert False, "从返回数据中提取参数失败\r\n Error: {a}".format(a=e_msg)

                # 设置断言参数
                exp_flag, expected = self.set_expected(expected)
                if not exp_flag:
                    assert False, "断言：参数获取失败\r\n Error: {a}".format(a=expected)

                # 断言
                self.mul_assert(data, expected)
            else:
                allure.attach(data, '返回结果：', attachment_type=allure.attachment_type.HTML)
                assert False, data

        elif url != "" and url_re:
            d_res, data = self.set_data(url_re[0])
            if not d_res:
                assert False, "通过host参数获取 response伪数据失败\r\n Error: {a}".format(a=data)

            if not isinstance(data, str):
                # Log.logger("Get Body:" + str(data))

                # 获取返回中的数据供后续用例使用
                grs_flag, e_msg = self.get_var_from_response(copy.deepcopy(export), data)
                if not grs_flag:
                    assert False, "从返回数据中提取参数失败\r\n Error: {a}".format(a=e_msg)

                # Log.logger("目前参数情况：---- %s" % str(obj.var))

                # 设置断言参数
                exp_flag, expected = self.set_expected(expected)
                if not exp_flag:
                    assert False, "断言：参数获取失败\r\n Error: {a}".format(a=expected)

                # 断言
                self.mul_assert(data, expected)
            else:
                allure.attach(data, '断言结果：', attachment_type=allure.attachment_type.HTML)
                assert False, data

        elif url == "":
            # 设置断言参数
            exp_flag, expected = self.set_expected(expected)
            if not exp_flag:
                assert False, "断言：参数获取失败\r\n Error: {a}".format(a=expected)
            # 断言
            self.mul_assert(None, expected)

        else:
            assert False, "请求url为NULL，请查看用例或EvnHost文件配置是否正确"

