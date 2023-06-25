import os
from urllib.parse import urlencode

import requests
# from Common.Encryption import Encryption
import yaml

from Common.BaseOS import BaseOS
from Common.BaseUrl import BaseUrl
import sys

from Conf.EnvHost_Conf import HOST_YAML_PATH
import http.client

if sys.platform == 'darwin':
    from Common.Encryption_MAC import Encryption
elif sys.platform == 'linux':
    from Common.Encryption_LINUX import Encryption
else:
    from Common.Encryption_WIN import Encryption


class BaseRequest:
    """
    用于发起get、post请求
    调用 base_request(self, url, method='GET', params=None, **kwargs) ：通过method 值区分get、post请求
    """

    # C360、Mix Android 非老接口（bmall、dispatcher、i、cdn-bm以外），无需在参数后添加 &
    # 利用以下Android_No_Add_Host、Andorid_App指定哪些host不添加，哪些产品是需要判断 & 添加逻辑
    Android_No_Add_Host = ["ops"]   # 无需添加&的host，任意产品均加入此处
    Andorid_App = ["Mix_Android", "C360_Android"]   # 需进行&添加与否判断的产品
    App_Env = ["PROD", "QA", "PROD-O/S", "PROD-PRE", "DEV"]

    # 调用此方法，自动区分 get、post请求,
    def base_request(self, url='', method='GET', encryption=0, params=None, headers=None, timeout=10, **kwargs):
        """
        request请求
        :param url: 请求api
        :param method: 请求方式，值需为 GET、POST
        :param params: 请求参数
        :param kwargs: 其它的请求参数，可传入不定长度的有名参数，如 headers=
        :return: class:`Response  ` object
        """
        params = params
        headers = headers
        app = BaseUrl().get_app()
        cryp = Encryption()

        # -------------------* 特殊处理 *-----------------------------
        # [特殊处理] 针对 c360、MIX android 请求参数结尾需要有一个&，否则无法通过sig验证
        if encryption == 0 and app in self.Andorid_App:
            config_path = []
            for i in self.Andorid_App:
                config_path.append(HOST_YAML_PATH[i])
            base_path = os.path.join(BaseOS().get_project_path(), "Conf")
            config_path = [os.path.join(base_path, x) for x in config_path]
            host_path = []
            for p in config_path:
                with open(p, 'r') as f:
                    cof = yaml.safe_load(f)
                    for h in self.Android_No_Add_Host:
                        for e in self.App_Env:
                            if e in cof.keys() and h in cof[e].keys():
                                host_path.append(cof[e][h])
                    f.close()
            if not list(filter(lambda x: x, [url.startswith(x) for x in host_path])):
                params = cryp.encryption_0_android(params)

        # -------------------* 处理加密 *-----------------------------
        # Camera360 登录注册销毁（敏感信息加密）
        if encryption == 1:
            params, headers = cryp.encryption_1(params, headers)

        # -------------------* 发起请求 *-----------------------------
        if method.lower() == 'get':
            return self.base_get(url=url, params=params, headers=headers, timeout=timeout, **kwargs)
        elif method.lower() == 'post':
            return self.base_post(url=url, data=params, encryption=encryption, headers=headers, timeout=timeout,
                                  **kwargs)

        return response
        # # 处理 br 解析
        # if response.headers.get('Content-Encoding') == 'br':
        #     data = brotli.decompress(response.content)
        #     return data.decode('utf-8')
        # else:
        #     return response

    # get请求
    def base_get(self, url='', params=None, headers=None, timeout=10, **kwargs):
        i = 0
        except_msg = ""
        while i < 3:  # 重试3次
            try:
                return requests.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
            except requests.exceptions.RequestException as e:
                i += 1
                except_msg += str(e) + "\n"
        return except_msg

    # post请求
    def base_post(self, url='', data=None, encryption=0, headers=None, timeout=10, **kwargs):
        re = None
        i = 0
        except_msg = ""
        while i < 3:  # 重试3次
            try:
                # 当IDCamera、Blurrr ios产品使用 json作为请求体时应用json传数据
                if encryption == 2:
                    re = requests.post(url, json=data, headers=headers, timeout=timeout, **kwargs)
                else:
                    re = requests.post(url, data=data, headers=headers, timeout=timeout, **kwargs)
                # 当加密为1时，对返回结果进行解密
                if encryption == 1:
                    re = Encryption().decryption_response_1(re)
                return re
            except requests.exceptions.RequestException as e:
                i += 1
                except_msg += str(e) + "\n"
        return except_msg


if __name__ == '__main__':
    # data = BaseRequest().base_request(url='https://qyapi.weixin.qq.com/cgi-bin/gettoken',
    #                                   method='Post',
    #                                   params={'corpid': 'ww83b24471a9f1e306',
    #                                           'corpsecret': 'gTo9ePkgpXWC2rc2SEHT02eeybb_zT0sMnSe6ljdCZM'},
    #                                   headers=None)
    # data2 = BaseRequest().base_request(
    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/create?access_token=qmF4OUhhF64vvT4fVzMSDfZjW5h9B8APUV3IeTea-HJKtkrAyMuTaY-jKKRCCpcuCdRalvbEy0eEqygbNaEt65Yhj90wQG64o1KNBOb3RteuLa6AycTrbKJh2YUdiJf2QPVO5gyngbM4Uiw9pwSOpGJlFb8kAvPNG5ffO1imkI4edM076tO641RPH-DfZYF7NGa7MRP4eTCz9nirwDv_8g',
    #     method='POST',
    #     params={'userid': 4, 'name': 'wdq', 'department': [1], 'email': 'db@aa.aa'},
    #     headers=None)

    data = BaseRequest().base_request(url='https://dispatchertest.camera360.com/api/v1/list',
                                      method='post',
                                      params={'UTCOffset': '28800',
                                              'appName': 'Camera360',
                                              'appVersion': '9.9.46',
                                              'appVersionCode': 9948,
                                              'appkey': 'uku4m1rw5yno8ms4',
                                              'appname': 'Camera360',
                                              'appversion': '9.9.46',
                                              'channel': 'appstore_dev',
                                              'checkSum': '323cdcb15245c6f40fbdc8cf5d32aa9c',
                                              'device': 'iPhone6,1',
                                              'deviceId': 'F01B6359-4B49-4CA3-A07D-515FC5509833',
                                              'geoinfo': '0.000000,0.000000',
                                              'growingIOUserId': 'ED947CA2-C4D2-4E24-99BC-03B2F50B27F9',
                                              'idfa': '97CCAF77-2027-4817-B8DC-6A1C5B1939EC',
                                              'initStamp': 1618906147,
                                              'language': 'zh-Hans',
                                              'latitude': 0,
                                              'localTime': 1620370975.034687,
                                              'locale': 'zh-Hans',
                                              'longitude': 0,
                                              'mcc': None,
                                              'mnc': None,
                                              'newAddToday': 0,
                                              'platform': 'ios',
                                              'screenSize': '320*568',
                                              'sig': 'e5ac3ecc1b462d7aa357faf24981c0ab',
                                              'systemVersion': '10.3.2',
                                              'timeZone': 'Asia/Shanghai',
                                              'upgradeTime': 1620370974.794,
                                              'version': 34391,
                                              'vipStatus': 'expired'},
                                      headers=None)

    data2 = {
        'UTCOffset': '28800',
        'appName': 'Camera360',
        'appVersion': '9.9.69',
        'appVersionCode': '9969',
        'appkey': 'uku4m1rw5yno8ms4',
        'appname': 'Camera360',
        'appversion': '9.9.69',
        'channel': 'toolchain',
        'cid': 'c30ec166e9bc96a0ec2b8b1d8e1da923679a1d82074552746834c403ce1e05fd',
        'device': 'iPhone10,2',
        'deviceId': 'E40AD2B2-A18D-4858-B085-AE27042F1A67',
        'email': 'a005@aa.aa',
        'geoinfo': '30.541605,104.066379',
        'growingIOUserId': '2F0C7493-4048-48B4-BE6D-705759E99104',
        'initStamp': '0.000000',
        'latitude': '30.54160541107346',
        'localTime': '1639379224.567226',
        'locale': 'zh-Hans',
        'longitude': '104.0663787734136',
        'mcc': '',
        'mnc': '',
        'newAddToday': 0,
        'password': '7c3d596ed03ab9116c547b0eb678b247',
        'platform': 'ios',
        'sig': 'd6fa0f57c83497729cfa4e71986744bd',
        'systemVersion': '13.6.1',
        'time': '1639379225',
        'timeZone': 'Asia/Shanghai'
    }
    headers = {
        'Host': 'itest.camera360.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Camera360/9.9.69 (iPhone; iOS 13.6.1; Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1, ja-CN;q=0.9, en-CN;q=0.8, zh-Hant-CN;q=0.7, es-CN;q=0.6, ar-CN;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    url = "https://itest.camera360.com/api/v2/mailLogin"

    response = BaseRequest().base_request(url=url, encryption=1, method='POST', params=data2, headers=headers)
    # Encryption().decryption_response_1(response)
