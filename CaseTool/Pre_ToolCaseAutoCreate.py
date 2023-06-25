import copy
import os
import json
import re
import urllib.parse

import xlwt

from Common.BaseOS import BaseOS

# 请将postman导出的 collection json文件放入 Tool 目录下：生成抓取到的接口的表头文件
# 请将postman中 接口send时，使用send and save 自动下载的返回数据json文件放入Tools目录下：生成字段检查内容
# 将上面2部的内容对应并拼接即
# varlist一行所需填写的部分，请在以下参数填写，以\n为换行符
# 若想预填入sig、encryption 请在下面参数填定
varlist = ""
sig = ""
encryption = ""



key_explain = {
    "is_exist": 1,
    "type": "",
    "list_type": "",
    "is_url": "",
    "is_empty": "",
    "is_null": "",
    "value_reg": "",
    "value_list": []
}
url_reg_list = ["^https?://([0-9a-zA-Z\-._]*\/)*(\w+\.)(jpg|png|webp|jpeg|JPG|PNG|WEBP|JPEG)(\??.+)?",
                "^https?://([0-9a-zA-Z\-._]*\/)*\w+\.(zip|ZIP)$"]
str_reg_list = ["^#[0-9A-Fa-f]{6}$",  # 色值
                # "^[a-zA-Z0-9_]+$",  # 商品ID
                "^[0-9a-zA-Z]{32}",  # MD5
                "^[0-9]{10}",  # 时间戳
                "^[¥\$](([1-9]{1}[0-9]*)|0)\.+[0-9]{2}$|^¥[1-9]{1}[0-9]*$"  # 商品价格
                ]

all_keys = {"body": copy.deepcopy(key_explain)}

ops_key = ["PG-AppID", "PG-Platform", "PG-Time", "PG-UserID", "PG-UserToken", "PG-Sign", "PG-AppVersion",
           "PG-OSVersion", "PG-Model", "PG-EID", "PG-FA", "PG-FV", "PG-AID", "PG-OAID", "PG-AAID", "PG-LL",
           "PG-Channel", "PG-InitStamp", "PG-UpgradeStamp", "PG-Density", "PG-ScreenSize", "PG-Language",
           "PG-UtcOffset", "PG-Network", "PG-ENCH", "PG-ENCB", "PG-Locale", "PG-DataEnv", "PG-Debug"]


def get_key(dict_data, pre_str):
    keys = dict_data.keys()

    for key in keys:
        this_key = pre_str + "." + key

        # 若没有这个key，添加key
        if this_key not in all_keys.keys():
            all_keys[this_key] = copy.deepcopy(key_explain)

        # 添加当前key的值类型 返回值为"list"
        this_type = set_type(dict_data[key], this_key)

        if this_type == "list" and len(dict_data[key]) > 0:
            this_list_type = set_type(dict_data[key][0], this_key, "list_type")

        if this_type == "str" and dict_data[key].startswith("http"):
            all_keys[this_key]["is_url"] = 1

            for reg_str in url_reg_list:
                pattern = re.compile(reg_str)
                m = pattern.match(dict_data[key])
                if m:
                    all_keys[this_key]["value_reg"] = reg_str
                    break
        elif this_type == "str":
            for reg_str in str_reg_list:
                pattern = re.compile(reg_str)
                m = pattern.match(dict_data[key])
                if m:
                    all_keys[this_key]["value_reg"] = reg_str
                    break

        if (this_type == "str" and dict_data[key] == "") or (this_type == "list" and dict_data[key] == []) or (
                this_type == "dict" and dict_data[key] == {}):
            all_keys[this_key]["is_empty"] = 1

        if this_type == "":
            all_keys[this_key]["is_null"] = 1

        # 若有这个key，key的值不是dict、list，将值加入

        if this_type not in ["dict", "list"] and dict_data[key] not in all_keys[this_key] and all_keys[this_key][
            "value_reg"] == "" and dict_data[key] not in ["", None]:
            all_keys[this_key]["value_list"].append(dict_data[key])

        if this_type == "list" and len(dict_data[key]) > 0 and type(dict_data[key][0]) == dict:
            for i in dict_data[key]:
                get_key(i, this_key)

        if this_type == "dict":
            get_key(dict_data[key], this_key)


# 设置key 值类型，若为None类型，返回""  explain_key = "type"、"list_type"
def set_type(this_value, this_key, explain_key="type"):
    this_type = get_type(this_value)

    if this_type != "" and all_keys[this_key][explain_key] != "" and this_type not in all_keys[this_key][
        explain_key].split(","):
        all_keys[this_key][explain_key] += ","

    if this_type != "" and this_type not in all_keys[this_key][explain_key]:
        all_keys[this_key][explain_key] += this_type

    return this_type


# 获取值的type
def get_type(this_value):
    this_type = type(this_value)
    if this_type == dict:
        return "dict"
    elif this_type == list:
        return "list"
    elif this_type == str:
        return "str"
    elif this_type == float:
        return "float"
    elif this_type == int:
        return "int"
    elif this_type == bool:
        return "bool"
    elif this_type == type(None):
        return ""


# 生成响应体描述 xls
def create_response_xls(dict_data, xls_name):
    if type(dict_data) not in [list, dict]:
        all_keys["body"]["type"] = set_type(dict_data, "body")
    elif type(dict_data) == list:
        all_keys["body"]["type"] = "list"

        for list_i in dict_data:
            this_type = type(list_i)

            set_type(list_i, "body", "list_type")

            if this_type == dict:
                get_key(list_i, "body")
    elif type(dict_data) == dict:
        all_keys["body"]["type"] = "dict"

        get_key(dict_data, "body")

    print("=======================================  当前json 字段的 key 生成完成  =======================================\n")

    title = ["字段说明", "后台配置项", "字段", "是否必下发", "值类型", "list值类型", "是否为url", "是否可为空值", "是否可为null", "值规则", "值", "值说明", "备注"]

    # 创建新的 用例.xls 文件
    new_xls = xlwt.Workbook(encoding='utf-8')
    new_sheet = new_xls.add_sheet("预生成用例")

    row_value_list = []

    for this_key in all_keys.keys():
        if len(set(all_keys[this_key]["value_list"])) == len(all_keys[this_key]["value_list"]):
            value_str = ""
            value_str2 = ""
        else:

            value_list = list(filter(lambda x: not re.match(r'[0-9]{10}', str(x)), all_keys[this_key]["value_list"]))
            value_str = ",".join([str(x) for x in list(set(value_list))])
            value_str2 = "\n".join([str(x) for x in list(set(value_list))])
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(this_key, all_keys[this_key]["is_exist"],
                                                          all_keys[this_key]["type"], all_keys[this_key]["list_type"],
                                                          all_keys[this_key]["is_url"], all_keys[this_key]["is_empty"],
                                                          all_keys[this_key]["is_null"],
                                                          all_keys[this_key]["value_reg"],
                                                          value_str))

        row_value_list.append(["", "",
                               this_key,
                               all_keys[this_key]["is_exist"],
                               all_keys[this_key]["type"], all_keys[this_key]["list_type"],
                               all_keys[this_key]["is_url"], all_keys[this_key]["is_empty"],
                               all_keys[this_key]["is_null"], all_keys[this_key]["value_reg"],
                               value_str2, "", ""])

    for row in range(0, len(row_value_list) + 1):
        for col in range(0, len(title)):
            if row == 0:
                new_sheet.write(row, col, title[col])
            else:
                new_sheet.write(row, col, row_value_list[row - 1][col])

    file_name = xls_name.replace("-", "_") + ".xls"

    case_path = os.path.join(os.path.join(BaseOS().get_project_path(), "Tool", "Case"))
    if not os.path.exists(case_path):
        os.makedirs(case_path)
    new_xls.save(os.path.join(case_path, file_name))


# 生成 表头 xls
def create_url_xls(item):
    # 获取host、path
    host_type = type(item["request"]["url"])
    if host_type == dict:
        host = item["request"]["url"]["host"][0]
        path = "/".join(item["request"]["url"]["path"])
    elif host_type == str:
        result = urllib.parse.urlparse(item["request"]["url"])
        host = result.hostname.split(".")[0]
        path = result.path[1:]
    else:
        host = ""
        path = ""

    # 处理header中PG-参数大小写
    lower_ops = [y.lower() for y in ops_key]
    for headers_i in item["request"]["header"]:
        if headers_i["key"].lower() in lower_ops:
            headers_i["key"] = ops_key[lower_ops.index(headers_i["key"].lower())]

    # 处理请求体不同格式时的数据获取
    if "body" in item["request"].keys():
        body_type = item["request"]["body"]["mode"]
        if body_type == "raw":
            params = "\n".join(item["request"]["body"]["raw"].split("&"))
        elif body_type in ["formdata", "urlencoded"]:
            if "urlencoded" in item["request"]["body"].keys():
                params = "\n".join(x["key"] + "=" + x["value"] for x in item["request"]["body"]["urlencoded"])
            else:
                params = "\n".join(x["key"] + "=" + x["value"] for x in item["request"]["body"]["formdata"])
        else:
            params = ""
    elif type(item["request"]["url"]) ==dict and "query" in item["request"]["url"].keys():
        # print(item["request"]["url"])
        params = "\n".join(x["key"] + "=" + x["value"] for x in item["request"]["url"]["query"] if x["key"] != None)
    elif type(item["request"]["url"]) == str:
        if len(item["request"]["url"].split("?")) > 1:
            params = "\n".join(item["request"]["url"].split("?", 1)[1].split("&"))
        else:
            params = ""


    xls_data = {
        "content": "",
        "type": "field",
        "sig": sig,
        "env": "",
        "encryption": encryption,
        "host": host,
        "path": path,
        "method": "Post" if item["request"]["method"].lower() == "post" else "Get",
        "headers": "\n".join(x["key"] + ":" + x["value"] for x in item["request"]["header"] if
                             x["key"].lower() not in ["host", "content-length", "x-postman-captr"]),
        "params": params,
        "export": "",
        "varlist": varlist,
        "Var": ""
    }

    xls_name = host + "-" + path.split("/")[-1]

    # 创建新的 用例.xls 文件
    new_xls = xlwt.Workbook(encoding='utf-8')
    new_sheet = new_xls.add_sheet("预生成用例")

    for i in range(len(xls_data.keys())):
        new_sheet.write(i, 0, list(xls_data.keys())[i])
        new_sheet.write(i, 1, xls_data[list(xls_data.keys())[i]])

    file_name = xls_name.replace("-", "_") + ".xls"
    print(file_name)

    case_path = os.path.join(os.path.join(BaseOS().get_project_path(), "Tool", "Case"))
    if not os.path.exists(case_path):
        os.makedirs(case_path)
    new_xls.save(os.path.join(case_path, file_name))

# postman数据中多层item的处理
def post_collect_item(items_i):
    if "item" in items_i.keys():
        for items_i_i in items_i["item"]:
            post_collect_item(items_i_i)
    else:
        create_url_xls(items_i)


# 读取 Tool 目录下的json文件
tool_path = os.path.join(os.path.join(BaseOS().get_project_path(), "Tool"))
json_path = BaseOS().get_all_files_dir(tool_path, need_type=[".json"])

if not os.path.exists(tool_path):
    os.makedirs(tool_path)


for json_path_i in json_path:
    dict_data = None
    print("\n=======================================  " + json_path_i + "  =======================================")
    with open(json_path_i) as f:
        org_data = f.readlines()
    dict_data = json.loads("".join([x.lstrip().rstrip() for x in org_data]))

    if type(dict_data) == dict and "info" in dict_data.keys() and "_postman_id" in dict_data["info"].keys():
        all_keys = {"body": copy.deepcopy(key_explain)}
        # items = dict_data["item"]
        # for items_i in items:
        #
        #     create_url_xls(items_i)
        post_collect_item(dict_data)

    else:
        all_keys = {"body": copy.deepcopy(key_explain)}
        xls_name = os.path.basename(json_path_i).replace(".json", "")
        create_response_xls(dict_data, xls_name)

