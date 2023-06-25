# coding=utf-8
import os
import pytest
from Common.Log import Log


# 注册自定义参数 cmdopt 到配置对象
def pytest_addoption(parser):
    """
    增加命令行参数 --env 指定-测试环境
    可配置值： --env=QA、PROD、DEV
    """
    parser.addoption(
        "--env",
        action="store",
        # default: 默认值，命令行没有指定host时，默认用该参数值
        default="QA",
        help="指定环境，默认值为QA，可以配置: QA PROD DEV"
    )

    """
    增加命令行参数 --app 指定-测试产品
    可配置值：
        --app=C360_iOS、C360_Android 
              IDCamera、IDCamera
    """
    parser.addoption(
        "--app",
        action="store",
        help="* 指定产品，必须配置，无默认值，如：C360_iOS、C360_Android "
    )

    """
    增加命令行参数 --mod 指定-测试产品
    可配置值：
        --mod=dispatcher,i...
        可配置多个，以","号分隔
    """
    parser.addoption(
        "--mod",
        action="store",
        default="*",
        help='''指定执行的模块,非必配项,eg:dispatcher,i... 多个值时，以","分隔; 默认*，表示所有模块'''
    )

    """
    增加命令行参数 --prio 指定执行优先级<=值的用例
    可配置值：
        --prio=1,2,3,4,5
        --prio=2时，执行优先级为1、2的用例
    """
    parser.addoption(
        "--prio",
        action="store",
        type=int,
        default=5,
        help="指定执行的用例优先级，非必配项，值为1~5的整数，1表示最高优先级，执行<=该值的用例，默认值5"
    )

    """
        增加命令行参数 --log 指定log日志级别
        可配置值：
            --log=debug、info、warn、error、critical
            默认值：info
    """
    parser.addoption(
        "--log",
        action="store",
        type=str,
        default='info',
        help='指定log日志的默认级别，非必配项，值可以是：debug、info、warn、error、critical，默认值 info'
    )

    """
        增加命令行参数 --timeout 指定接口请求超时时间
        可配置值：
            --timeout=10
            默认值：10 （即10s）
    """
    parser.addoption(
        "--timeout",
        action="store",
        type=float,
        default=10,
        help='指定接口请求的超时时间，非必配项，可以是浮点数，默认值为10，即10s'
    )

    """
        增加命令行参数 --Assert_msg 指定Allure报告中断言信息展示范围
        可配置值：
            --Assert_msg=All、Failed (All:所有添加的msg均展示、Failed：仅展示失败的Assert断言信息)
            默认值：All
    """
    parser.addoption(
        "--assert_msg",
        action="store",
        type=str,
        default="All",
        help='指定Allure报告中断言（Assert）信息展示范围'
    )


@pytest.fixture(scope="session", autouse=True)  # autouse=True自动执行该前置操作
def env(request):
    """获取命令行参数，给到环境变量"""
    os.environ["env"] = request.config.getoption("--env")
    Log.logger("当前用例运行测试环境：%s" % os.environ["env"])
    # print("当前用例运行测试环境：%s" % os.environ["env"])


@pytest.fixture(scope="session", autouse=True)
def app(request):
    os.environ["app"] = request.config.getoption("--app")
    Log.logger("当前用例运行产品：%s" % os.environ["app"])
    # print("当前用例运行产品：%s" % os.environ["app"])


@pytest.fixture(scope="session", autouse=True)
def modules(request):
    os.environ["mod"] = request.config.getoption("--mod")
    Log.logger("当前用例运行模块：%s" % os.environ["mod"])
    # print("当前用例运行模块：%s" % os.environ["mod"])


@pytest.fixture(scope="session", autouse=True)
def priority(request):
    os.environ["prio"] = str(request.config.getoption("--prio"))
    Log.logger("当前用例执行优先级: >=%s " % os.environ["prio"])
    # print("当前用例执行优先级: <=%s " % os.environ["prio"])


@pytest.fixture(scope="session", autouse=True)
def log_level(request):
    os.environ['log'] = str(request.config.getoption("--log"))
    Log.logger("当前日志级默认级别为: %s " % os.environ["log"])


@pytest.fixture(scope="session", autouse=True)
def timeout(request):
    os.environ['timeout'] = str(request.config.getoption("--timeout"))
    Log.logger("当前接口请求超时时间为： %s s" % os.environ["timeout"])


@pytest.fixture(scope="session", autouse=True)
def assert_msg(request):
    os.environ['assert_msg'] = str(request.config.getoption("--assert_msg"))
    Log.logger("当前Allure断言信息区间为：%s" % os.environ["assert_msg"])
