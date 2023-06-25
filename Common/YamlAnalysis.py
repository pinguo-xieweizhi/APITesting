import copy
import json
import re

import yaml
import os
import sys

from Common.BaseUrl import BaseUrl
from Common.BaseOS import BaseOS
from Common.Assert import Assert
from Common.ConfMsg import ConfMsg

if sys.platform == 'darwin':
    from Common.Encryption_MAC import DecryptionResponse
elif sys.platform == 'linux':
    from Common.Encryption_LINUX import DecryptionResponse
else:
    from Common.Encryption_WIN import DecryptionResponse
# from Common.Encryption import DecryptionResponse


class YamlAnalysis:
    """
    用于yaml用例解析

    使用方法::
    >>> ya = YamlAnalysis(casedata_path) # 传入Data目录下的用例yaml文件路径实例化对象
    >>> test_data = ya.test_data() # 使用test_data() 方法解析yaml用例数据
    >>> # test_data ：[(name, priority, encryption, method, url, headers, params, validate, export),()]
    >>> ya.get_var(di) # 将请求数据中的参数设置好，用于request请求；di：headers, params （test_data数据中的值）
    >>> ya.set_var(di,res) # 将接口返回数据设置到Var数据中，供后续使用；传入 di:export（test_data数据中的值）; 传入res: 接口请求后返回的response数据

    """

    def __init__(self, casedata_path):
        """

        :param casedata_path: 用例数据.yaml路径
        """

        self.conf = ConfMsg()

        self.casedata_path = casedata_path
        # self.env = env

        # 读取yaml文件
        with open(casedata_path, 'r') as f:
            self.data = yaml.safe_load(f)

        # 获取测试环境
        with open(os.path.join(BaseOS().get_project_path(), 'Conf', 'Config.yaml'), 'r') as f:
            f_data = yaml.safe_load(f)
            self.env = f_data["ENV"]
            self.prio = int(f_data["PRIO"])
            self.timeout = float(f_data["TIMEOUT"])

        # 获取用例中的参数 ,并拼接Global参数
        self.var = self.data["Var"]
        self.Global_Var = self.conf.get_Global_Var()

        # 将当前用例中的Global_Var 添加到Config.yaml中
        self.Global_Var.update(self.data["Global_Var"])
        self.conf.set_msg(Global_Var=self.Global_Var)

        temp = copy.deepcopy(self.Global_Var)
        # if temp is not None:
        temp.update(self.var)
        self.var = temp

        del temp

    # 解析.yaml中用例数据
    def test_data(self):
        """
        解析.yaml中用例数据
        :return: [(name, priority, encryption, method, url, headers, params, validate, export),()]
        """
        name = self.get_case_name()
        priority = self.get_priority()
        encryption = self.get_encryption()
        sig = self.get_sig()
        env = self.get_env()
        method = self.get_method()
        url = self.get_url()
        headers = self.get_headers()
        params = self.get_params()
        validate = self.get_validate()
        export = self.get_export()
        timeout = self.timeout

        # 将获取到的各个list 组合[(),()...]列表
        data = [(a, b, c, d, e, f, g, h, i, j, k) for a, b, c, d, e, f, g, h, i, j, k in
                zip(name, priority, encryption, sig, env, method, url, headers, params, validate, export)]  # 长度相同的几个列表组合成一个

        # 过滤掉优先级低于prio的用例
        ind = 0
        for i in data[:]:
            if priority[ind] < self.prio:
                data.remove(i)
            ind += 1
        return data, timeout

    # 获取用例中的用例：Test:{}
    def get_case(self):
        test_list = []
        case = self.data["TestCase"]
        for a in case:
            for k, v in a.items():
                if k == "Test":
                    test_list.append(v)
        return test_list

    # 获取用例名称
    def get_case_name(self):
        data = self.get_case()
        url_li = []
        for i in data:
            if "name" not in i.keys():
                i["name"] = "NULL"
            for k, v in i.items():
                if "name" == k:
                    url_li.append(v)
        return url_li

    # 获取用例优先级
    def get_priority(self):
        data = self.get_case()
        pro_li = []
        for i in data:
            pro_li.append(i["priority"])
        return pro_li

    # 获取加密方式
    def get_encryption(self):
        data = self.get_case()
        enc_li = []
        for i in data:
            enc_li.append(i["encryption"])
        return enc_li

    # 获取签名方式
    def get_sig(self):
        data = self.get_case()
        sig_li = []
        for i in data:
            sig_li.append(i["sig"])
        return sig_li

    # 获取环境
    def get_env(self):
        data = self.get_case()
        env_li = []
        for i in data:
            env_li.append(i["request"]["env"])
        return env_li

    # 获取请求方式：post、get
    def get_method(self):
        data = self.get_case()
        method_li = []
        for i in data:
            re = i["request"]
            for k, v in re.items():
                if k == "method":
                    method_li.append(v.upper() if v != "" else "POST")
        return method_li

    # 获取请求headers
    def get_headers(self):
        data = self.get_case()
        headers_li = []
        for i in data:
            re = i["request"]
            for k, v in re.items():
                if k == "headers":
                    headers_li.append(v)
        return headers_li

    # 获取请求参数
    def get_params(self):
        data = self.get_case()
        params_li = []
        for i in data:
            re = i["request"]
            for k, v in re.items():
                if k == "params":
                    params_li.append(v)
        return params_li

    # 拼接出用例request url
    def get_url(self):
        """
        获取testdata yaml 中值生成 url list

        :param env: 默认值"QA"，可传参：QA（测试环境）、PROD（线上环境）、DEV（开发环境）
        :return: 返回 请求url list ，list中值为："https://wxx.sss.xxx", NULL, '${key}'

        注：若TestData yaml文件中 Test 中 request下必需配置HOST、PATH参数，并有可用于场景测试（不同接口间）
            HOST 、PATH 任一不存在：该用例的请求url将为'NULL'
        """
        data = self.get_case()
        url_li = []

        for i in data:
            req = i["request"]
            # HOST 与 PATH 均有值时可拼接出完整接口，否则加入NULL
            if "HOST" in req.keys() and "PATH" in req.keys():
                if req["PATH"] == "":
                    if req["HOST"] != "":
                        url_li.append(req["HOST"])
                    else:
                        url_li.append("")
                else:
                    host = BaseUrl().get_host(req["HOST"],
                                              self.env if "env" in req.keys() and req["env"] == "" else req["env"])
                    url_li.append(host + "/" + req["PATH"])
            else:
                url_li.append("NULL")
        return url_li

    # 获取用例断言
    def get_validate(self):
        data = self.get_case()
        validate_li = []
        for i in data:
            re = i["validate"]
            validate_li.append(re)
        return validate_li

    # 获取用例需从返回数据中取出的参数，供后续用例使用
    def get_export(self):
        data = self.get_case()
        export_li = []
        for i in data:
            if "export" in i.keys():
                value = i["export"]
            else:
                value = "NULL"
            export_li.append(value)
        return export_li

    # 设定全局变量值
    def set_var(self, di, res):
        """
        设定此测试用例的全局变量
        :param di: [(name, priority, encryption, method, url, headers, params, validate, export),()]中的 export,是一个list
        :param res: 接口 response 返回的数据
        :return: 无返回值，仅修改 self.var的值
        """
        for k, v in di.items():
            # if "headers" in v:
            #     this_data = json.loads(str(res.headers).replace("'", '"'))
            # elif "body" in v:
            #     this_data = json.loads(res.text)
            # text = Assert().field_special_process(this_data, v)
            text = Assert().field_special_process(res, v)

            # 上面方法取值为list，若仅有一个值时，则需直接设置参数值为值，而非list
            if len(text) == 1:
                text = text[0]

            # 若上面方法取出的值不是str、float、bool、int 可能是dict、list，此时 以字符串的形式存入参数中
            if not isinstance(text, (str, float, bool, int)):
                di[k] = json.dumps(text)
            else:
                di[k] = text
        self.var.update(di)

        # 执行Globale用例并取值后，向Config.yaml 添加Global_Var (需判断Global_Exported=False时才能添加)
        if not self.conf.get_Global_Exported():
            self.Global_Var.update(di)
            self.conf.set_msg(Global_Var=self.Global_Var)
            # if self.Global_Var is None:
            #     self.conf.set_msg(Global_Var=di)
            #     self.Global_Var = di
            # else:
            #     self.Global_Var.update(di)
            #     self.conf.set_msg(Global_Var=self.Global_Var)

    # 设置header、parmars、validate、host中￥{key}伪Response中的参数数据
    def get_var(self, di):
        """
        将request 请求数据中的headers、parmars 的参数设置为self.var中对应的值
        :param di: # [(name, priority, encryption, method, url, headers, params, validate, export),()]中的 headers, params
        :return: 返回，替换参数值后的headers、parmars数据
        """
        # 设置headers、parmars 参数值
        if isinstance(di, dict):
            for k, v in di.items():
                if isinstance(v, str) and "${" in v:
                    variable_regex_compile = re.compile(r"\$\{(\w+)\}|\$(\w+)")
                    m = variable_regex_compile.search(v)
                    l = m.group().split('{')[-1].split('}')[0]
                    di[k] = v.replace(m.group(), str(self.var[l]))
        # 当 设置expected 参数值
        elif isinstance(di, list):
            di2 = []
            for di_list_item in di:
                dict_1 = {}
                for k, v in di_list_item.items():
                    list_1 = []
                    for i_str in v:
                        m = re.findall(r'\$\{(\w+)\}', i_str)
                        if m:
                            # temp_str = ""
                            for l in m:
                                i_str = i_str.replace("${" + l + "}", str(self.var[l]))
                            # i_str = temp_str
                        list_1.append(i_str)
                    dict_1[k] = list_1
                di2.append(dict_1)
            di = di2
        # 设置HOST中 ${key}
        elif isinstance(di, str):
            variable_regex_compile = re.compile(r'\$\{(\w+)\}')
            m = variable_regex_compile.findall(di)
            di = self.var[m[0]]
            res = DecryptionResponse()
            res.set_text(str(di))
            res.set_status_code(200)
            di = res
        return di

    # 计算 Headers中的content_length,并返回新的headers
    def get_content_length(self, headers, params):
        length = len(params.keys()) * 2 - 1
        total = ''.join(list(params.keys()) + list(params.values()))
        length += len(total)
        length = len(json.dumps(params).replace(' ', '').replace('"', ''))
        key_flag = False

        for i in headers.keys():
            if i.lower() == "content-length":
                headers[i] = str(length)
                key_flag = True

        if not key_flag:
            headers["Content-Length"] = str(length)

        return headers
