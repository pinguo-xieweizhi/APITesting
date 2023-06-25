import os
from Common.BaseOS import BaseOS
from Common.Log import Log
from Common.YamlCreate import YamlCreate
from Common.PyCreate import PyCreate
from Common.ConfMsg import ConfMsg
import re


# 获取 需要测试的模板xls文件路径列表
# 此方法已弃用
def get_mod_xls_test_list(app, mod):
    test_list = []
    xls_main_path = os.path.join(BaseOS().get_project_path(), 'Data', app)

    xls_path_list = []

    if mod != '*':
        mod_list = mod.split(",")
        # print(mod_list)
        for mod in mod_list:
            mod_xls_path1 = os.path.join(xls_main_path, mod + '.xls')
            mod_xls_path2 = os.path.join(xls_main_path, mod + '.xlsx')
            # print(mod_xls_path)
            if os.path.exists(mod_xls_path1):
                xls_path_list.append(os.path.join(xls_main_path, mod + '.xls'))
            elif os.path.exists(mod_xls_path2):
                xls_path_list.append(os.path.join(xls_main_path, mod + '.xlsx'))
    else:
        xls_path_list += BaseOS().get_all_files_dir(xls_main_path, need_type='.xls')
        xls_path_list += BaseOS().get_all_files_dir(xls_main_path, need_type='.xlsx')

    return xls_path_list


# 获取可执行的.py用例列表（若没有，主动创建）
def get_test_list(app, mod):
    """
    根据 命令行参数，获取可以执行的用例列表(先获取testcase中 mod中的模块下的用例，再通过对应mod Data目录下的excle判断testcase中无.py文件时生成相应的py文件)
    :param app: 需执行的app
    :param mod: 需执行的模块，mod=*时执行app下所有用例
    :return: 需要执行的用例，TestCase/app/目录下对应mod模块中的.py文件路径列表
    """

    test_list = []  # 用于存储返回数据： 所有py用例文件的路径

    tc_main_path = os.path.join(BaseOS().get_project_path(), 'TestCase', app)
    mod_tc_path_list = []   # 用于存储 Testcase 模块名文件夹目录路径

    # mod 传入模糊模块时 如 bmall* ,即匹配开头为bmall的用例excle需要执行，获取当前执行产品下的所有xls、xlsx文件
    xls_main_path = os.path.join(BaseOS().get_project_path(), 'Data', app)
    all_xls_path = BaseOS().get_all_files_dir(xls_main_path, need_type=[".xls", ".xlsx"])
    mod_data_xls_path_list = []  # 用于存储 Data 中需执行用例的xls文件路径


    # 获取需测试模块路径， *号时表示执行该产品所有用例
    if mod != '*':
        mod_list = mod.split(',')

        for m in mod_list:
            # 判断模块是否为模糊查询模块
            if m.endswith("*") or m.startswith("*"):
                # reg_str = "^"+(".*" if m.startswith("*") else "") + list(filter(None, m.split("*")))[0] + (".*" if m.endswith("*") else "") +"$"

                reg_str = "^" + (".*" if m.startswith("*") else "") + list(filter(None, m.split("*")))[0] + (
                    ".*" if m.endswith("*") else "") + "$"

                for xls_i in all_xls_path:
                    xls_i_file_name = os.path.split(os.path.splitext(xls_i)[0])[1]

                    if re.match(reg_str, xls_i_file_name):
                        mod_tc_path_list.append(os.path.join(tc_main_path, xls_i_file_name))
                        mod_data_xls_path_list.append(xls_i)
            else:
                mod_tc_path_list.append(os.path.join(tc_main_path, m))

                mod_xls_path1 = os.path.join(xls_main_path, m + '.xls')
                mod_xls_path2 = os.path.join(xls_main_path, m + '.xlsx')
                if os.path.exists(mod_xls_path1):
                    mod_data_xls_path_list.append(mod_xls_path1)
                elif os.path.exists(mod_xls_path2):
                    mod_data_xls_path_list.append(mod_xls_path2)

    else:
        mod_tc_path_list.append(tc_main_path)
        mod_data_xls_path_list += all_xls_path

    # 先获取测试模块 TestCase 路径下符合模块要求的用例
    for path in mod_tc_path_list:
        test_list += BaseOS().get_all_files_dir(path)

    # 通过Data目录下的，mod.xls文件获取需要创建的.py文件
    # mod_xls_list = get_mod_xls_test_list(app, mod)
    # test_list2 = PyCreate().create_py(mod_xls_list, app)

    # 不存在的文件被成功生成，并得到列表
    test_list2 = PyCreate().create_py(mod_data_xls_path_list, app)

    test_list += test_list2

    return test_list


def set_config(ENV, APP, MOD, PRIO, LOG, ASSERT, TIMEOUT):
    """
    设置config.yaml、environment.properties文件，同时获取需要执行的Testcase 中的.py(支持xls自动创建)
    :param ENV:
    :param APP:
    :param MOD:
    :param PRIO:
    :param LOG:
    :return: 需执行的用例.py文件路径列表
    """

    # 获取 需执行的用例.py文件路径列表
    test_list = get_test_list(APP, MOD)

    # 更新 config.yaml文件
    conf = ConfMsg()
    conf.set_msg(APP=APP, ENV=ENV, MOD=MOD, PRIO=PRIO, LOG_Level=LOG, Assert_Msg=ASSERT, TIMEOUT=TIMEOUT, TestList=test_list, Global_Var={}, Global_Exported=False)

    # 将数据写入environment.properties   用于生成allure报告
    properties_path = os.path.join(BaseOS().get_project_path(), "Conf", "environment.properties")
    with open(properties_path, "w") as p:
        p.seek(0)
        p.truncate()
        p.write("APP=" + APP + '\n')
        p.write('Log_level=' + LOG + '\n')
        p.write('Enveriment=' + ENV + '\n')
        p.write('Test_module=' + MOD + '\n')
        p.write('Execution_priority=>=' + PRIO + '\n')
        p.write('Timeout=' + TIMEOUT + '\n')
        p.write('Assert_Msg=' + ASSERT + '\n')
        # p.write('Case_point='+str(len(test_list))+'\n')
        p.close()
    Log.logger("allure报告-环境信息写入完成")

    return conf.get_TestList()


def create_casedata(test_list, app, env):
    """
    生成需执行用例所需的.yaml文件
    :param test_list: testcase .py文件列表
    :param app: 测试产品
    :return: 无
    """
    by = YamlCreate()
    by.create_yaml(test_list, app, env)


def test_ini():
    """
       初始化测试环境
    1、获取测试相关参数：app\env\mod\prio\
    2、生成测试所需yaml文件（通过excle生成）
    :return: 无返回
    """
    Log.logger("-----------*初始化环境获准备开始*-----------")
    # 将环境数据写入Config.yaml 文件
    APP = os.environ["app"]
    ENV = os.environ["env"]
    MOD = os.environ["mod"]
    PRIO = os.environ["prio"]
    LOG = os.environ["log"]
    ASSERT = os.environ["assert_msg"]
    TIMEOUT = os.environ["timeout"]
    test_list = set_config(ENV, APP, MOD, PRIO, LOG, ASSERT, TIMEOUT)

    # 生成test_case yaml文件
    create_casedata(test_list, APP, ENV)
    Log.logger("-----------*初始化环境获取完成*-----------")
