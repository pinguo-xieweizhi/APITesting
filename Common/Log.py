import logging
import os
import time
from Common.BaseOS import BaseOS
import yaml
from logging.handlers import RotatingFileHandler

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class Log:
    date = '%Y-%m-%d %H:%M:%S'
    pro_path = BaseOS().get_project_path()

    path = os.path.join(pro_path, "Conf", "Config.yaml")
    log_path = os.path.join(pro_path, "Report", "Log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = os.path.join(pro_path, "Report", "Log", "log")

    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    if "LOG_Level" not in data.keys():
        level = "info"
    else:
        level = data["LOG_Level"]
    logging.basicConfig(level=LEVELS[level])  # 指定要输出的文件以及log的输出形式、包括时间格式、日志级别等等
    # handler = logging.FileHandler(log_file, encoding='utf-8')
    handler = RotatingFileHandler(filename=log_file, maxBytes=100 * 1024 * 1024, backupCount=3, encoding='utf-8')

    @classmethod
    def get_current_time(cls):
        return time.strftime(cls.date, time.localtime(time.time()))

    @classmethod
    def logger(cls, meg, **kwargs):
        lv = cls.level
        if 'level' in kwargs.keys():
            lv = kwargs['level']
        logging.getLogger().addHandler(cls.handler)
        if lv == "debug":
            cls.logger_debug(meg)
        elif lv == "warn":
            cls.logger_warn(meg)
        elif lv == "error":
            cls.logger_error(meg)
        elif lv == "critical":
            cls.logger_critical(meg)
        elif lv == "info":
            cls.logger_info(meg)
        else:
            raise ("Level is error...Please Try Again!!!")

    @classmethod
    def logger_critical(cls, meg):
        logging.critical("[CRITICAL " + cls.get_current_time() + "]" + meg)

    @classmethod
    def logger_error(cls, meg):
        logging.error("[ERROR " + cls.get_current_time() + "]" + meg)

    @classmethod
    def logger_warn(cls, meg):
        logging.warning("[WARNING " + cls.get_current_time() + "]" + meg)

    @classmethod
    def logger_info(cls, meg):
        logging.info("[INFO " + cls.get_current_time() + "]" + meg)

    @classmethod
    def logger_debug(cls, meg):
        logging.debug("[DEBUG " + cls.get_current_time() + "]" + meg)


