import os

import yaml

from Common.BaseOS import BaseOS


class ConfMsg:
    """
    使用方法：
    conf = ConfMsg()
    conf.set_msg(**kwargs) # kwargs: APP= ,ENV =, MOD=, PRIO=, LOG_Level=, TestList=, Global_Var=, Global_Exported=
    conf.get_msg(msg_key) # msg_key: APP ,ENV, MOD, PRIO, LOG_Level, TestList, Global_Var,Global_Exported
    conf.get_APP()/ENV(), MOD(), PRIO(), LOG_Level(), TestList(),Global_Var,Global_Exported
    """
    def __init__(self):
        self.config_path = os.path.join(BaseOS().get_project_path(), "Conf", "Config.yaml")
        with open(self.config_path, 'r') as f:
            self.cof = yaml.safe_load(f)
            f.close()

    def get_ENV(self):
        return self.cof["ENV"]

    def get_APP(self):
        return self.cof["APP"]

    def get_MOD(self):
        return self.cof["MOD"]

    def get_PRIO(self):
        return self.cof["PRIO"]

    def get_LOG_Level(self):
        return self.cof["LOG_Level"]

    def get_Assert_Msg(self):
        return self.cof["Assert_Msg"]

    def get_TimeOut(self):
        return self.cof["TIMEOUT"]

    def get_TestList(self):
        return self.cof["TestList"]

    def get_Global_Var(self):
        return self.cof["Global_Var"]

    def get_Global_Exported(self):
        return self.cof["Global_Exported"]

    def get_msg(self, msg_key):
        """
        :param msg_key: APP ,ENV, MOD, PRIO, LOG_Level, TestList,Global_Var,Global_Exported
        :return:
        """
        return self.cof[msg_key]

    def set_msg(self, **kwargs):
        """
        :param kwargs: APP= ,ENV =, MOD=, PRIO=, LOG_Level=, TestList=, Global_Var=, Global_Exported=
        :return:
        """
        args = kwargs.keys()
        for i in args:
            self.cof[i] = kwargs[i]

        with open(self.config_path, 'w')as f:
            yaml.dump(self.cof, f)
            f.close()