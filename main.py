#!/usr/bin/python3
import gc
import subprocess
import sys
import os
import re
from Common.Log import Log
from Common.BaseOS import BaseOS
import pytest
import shutil
from Common.ConfMsg import ConfMsg


if __name__ == '__main__':
    Log.logger('-----------*开始初始化环境*-------------')

    # 获取命令行中参数，并执行 pre_exec.py 文件，初始化环境
    # 初始化环境如下：设置config.yaml 文件，根据参数获取所需执行的用例，从excle文件中获取所需用例并生成yaml
    ini_argv_list = ["pre_exec.py", "-vs"]

    # 获取命令行参数
    argv = list(sys.argv)
    if len(argv) > 1:
        ini_argv_list += argv[1:]

    # 生成初始化python 命令行
    ini_cmd_line = "pytest " + (" ".join(ini_argv_list))
    if sys.platform == 'linux':
        ini_cmd_line = 'python3.8 -m '+ini_cmd_line
    Log.logger('开始执行python命令行：%s' % ini_cmd_line)

    # 执行 pytest pre_exec.py 文件
    os.system(ini_cmd_line)
    # result = subprocess.Popen(ini_cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = result.communicate()
    # if stderr.decode('utf-8') != "":
    #     Log.logger("出现异常："+stderr.decode('utf-8'))
    #
    # result = None
    # stdout = None
    # stderr = None

    gc.collect()

    # allure报告存储在工程目录Report/allure-report下
    allure_report_path = os.path.join(BaseOS().get_project_path(), "Report", "allure-Report")
    if not os.path.exists(allure_report_path):
        os.makedirs(allure_report_path)

    conf = None
    conf = ConfMsg()

    print("")
    Log.logger('==============================* 开始获取Global参数值 *==============================')
    re_str = r'.+/[Gg]lobal/.+\.py'
    global_TestList = [x for x in conf.get_TestList() if re.match(re_str, x)]

    global_flag = False

    if global_TestList != []:
        # 生成 pytest 用例执行命令行
        test_cmd_list = ["-v", "-s", ] + list(sys.argv)[1:] + global_TestList + ["--alluredir", str(allure_report_path), "--clean-alluredir"]
        test_cmd_line = ' '.join(test_cmd_list)
        Log.logger('开始执行Global 取值pytest命令行：%s\n' % test_cmd_line)
        pytest.main(test_cmd_list)

        gc.collect()

        global_flag = True
    else:
        Log.logger("无需获取Global参数")

    # 执行Global取值后 Config.yaml中的值已经变化，重新获取conf对象
    conf = None
    conf = ConfMsg()

    # 将Global参数获取用例从执行用例中删除、设置Global 参数获取标示为True(已取值)
    conf.set_msg(TestList=[x for x in conf.get_TestList() if not re.match(re_str, x)])
    conf.set_msg(Global_Exported=True)

    # 将Global 数据写入environment.properties   用于生成allure报告
    if conf.get_Global_Var() is not None:
        properties_path = os.path.join(BaseOS().get_project_path(), "Conf", "environment.properties")
        with open(properties_path, "a") as p:
            p.write('Global_Var=' + "".join(
                [str(x) + " = " + str(conf.get_Global_Var()[x]) + "\n" for x in conf.get_Global_Var().keys()]) + '\n')

    print("")
    Log.logger('==============================* 开始执行用例 *==============================')
    Log.logger("即将执行的测试用例产品：%s" % conf.get_APP())
    Log.logger('即将执行的测试用例环境：%s' % conf.get_ENV())
    Log.logger('即将执行的测试用例模块：%s' % conf.get_MOD())
    Log.logger('即将执行的测试用例优先级：>=%s' % conf.get_PRIO())
    Log.logger('即将执行的测试用例Log级别：%s' % conf.get_LOG_Level())
    Log.logger('即将执行的测试用例Asssert展示区间：%s' % conf.get_Assert_Msg())
    Log.logger('即将执行的测试用例接口请求超时时间：%ss' % conf.get_TimeOut())
    Log.logger('即将执行的测试用例Global参数：%s' % conf.get_Global_Var())
    Log.logger('即将执行的测试用例列表：%s ' % conf.get_TestList())

    if not global_flag:
        test_cmd_list = ["-v", "-s", ] + list(sys.argv)[1:] + conf.get_TestList() + ["--alluredir", str(allure_report_path), "--clean-alluredir"]
    else:
        test_cmd_list = ["-v", "-s", ] + list(sys.argv)[1:] + conf.get_TestList() + ["--alluredir", str(allure_report_path)]
    test_cmd_line = ' '.join(test_cmd_list)

    # del conf

    Log.logger('开始执行pytest命令行：%s' % test_cmd_line)
    pytest.main(test_cmd_list)

    Log.logger('----------*开始生成allure报告*-----------')
    allure_cmd_line = "allure generate  --clean " + str(allure_report_path) + " -o temp"
    Log.logger('开始执行命令行：%s' % allure_cmd_line)
    # os.system(allure_cmd_line)

    result = subprocess.Popen(allure_cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()

    if stderr.decode('utf-8') != "":
        Log.logger("Allure报告生成失败："+stderr.decode('utf-8'))
    else:
        Log.logger("Allure报告生成成功："+stdout.decode('utf-8'))

    # 手动释放内存
    result = None
    stdout = None
    stderr = None

    # 将 environment.properties 文件复制到 allure报告路径下
    en_path = os.path.join(BaseOS().get_project_path(), "Conf", "environment.properties")
    shutil.copy(en_path, allure_report_path)
    shutil.copy(en_path, os.path.join(BaseOS().get_project_path(), 'temp'))
    gc.collect()

# python3 main.py --env=PROD --app=C360_iOS --mod=bmall-unityFont-iOS2 --prio=4 --assert_msg=All --timeout=10
