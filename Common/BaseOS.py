import os
import shutil


class BaseOS:
    """
    BaseOS 提供一些文件/目录操作方法
    get_project_path(): 获取当前工程目录
    get_all_files_dir(): 获取当前目录及其子目录下的的满足筛选条件的文件绝对路径
    path_list(): 将路径通过路径分隔符拆分为list
    clear_folder(): 除主目录下的ignore_type类型以外的所有文件夹及文件
    create_dirs(): 创建目录
    """

    def get_project_path(self, project_name=None):
        """
        获取当前工程目录
        :param project_name: 工程名称
        :return: 工程绝对路径
        """
        c_name = 'Common' if project_name is None else project_name
        project_path = os.path.abspath((os.path.dirname(__file__)))
        root_path = project_path[:(project_path.find(c_name))]
        return root_path

    def get_all_files_dir(self, path, exc_file_name=['__init__.py'], need_type=['.py']):
        """
        获取当前路径下所有的文件路径
        :param path: 需查找的路径
        :param exc_file_name: 排除的文件名称列表，不会返回此文件的路径
        :param need_type: list 类型， list中为需要保留的并返回的文件格式，此类型的文件路径会被返回
        :return: [路径1, 路径2, 路径3...]查找到的所有符合要求的文件绝对路径组成的list
        """
        # from Common.Log import Log

        # Log.logger('开始扫描：%s 路径，获取需要执行的用例文件' % path)
        dir_list = []
        for root, dirs, files in os.walk(path):
            for f in files:
                filename, type = os.path.splitext(f)
                if f not in exc_file_name and type in need_type:
                    dir_list.append(os.path.join(root, f))
        return dir_list

    def get_all_dirs_and_files(self, path, exc_dir_name=['__MACOSX']):
        """
        获取当前路径下所有的文件路径
        :param path: 需查找的路径
        :param exc_file_name: 排除的文件名称列表，不会返回此文件的路径
        :param need_type: list 类型， list中为需要保留的并返回的文件格式，此类型的文件路径会被返回
        :return: [路径1, 路径2, 路径3...]查找到的所有符合要求的文件绝对路径组成的list
        """
        # from Common.Log import Log

        # Log.logger('开始扫描：%s 路径，获取需要执行的用例文件' % path)
        dir_list = []

        need_change_dirs_name = []
        for root, dirs, files in os.walk(path):
            # print(a)
            # print(root)
            # print(dirs)
            dirs = list(filter(lambda x: x not in exc_dir_name, dirs))
            # print(dirs)
            # print(files)
            files = list(filter(lambda x: not x.startswith("."), files))
            # print(files)
            # print(root.split(os.pathsep))
            # print(root.split(os.sep))
            # print(list(set(root.split(os.sep)).intersection(set(exc_dir_name))))
            # print("")

            if not list(set(root.split(os.sep)).intersection(set(exc_dir_name))):
                for d in dirs:
                    if d not in exc_dir_name:
                        # 处理文件名乱码的问题
                        try:
                            real_d = d.encode('cp437').decode('utf-8')
                        except:
                            try:
                                real_d = d.encode('cp437').decode('gbk')
                            except:
                                real_d = d
                        if real_d != d:
                            need_change_dirs_name.append([os.path.join(root, d), os.path.join(root, real_d)])
                            # os.rename(os.path.join(root, d), os.path.join(root, real_d))
                            d = real_d
                        dir_list.append((os.path.join(root, d)))
                for f in files:
                    # 处理文件名乱码的问题
                    try:
                        real_f = f.encode('cp437').decode('utf-8')
                    except:
                        try:
                            real_f = f.encode('cp437').decode('gbk')
                        except:
                            real_f = f
                    if real_f != f:
                        os.rename(os.path.join(root, f), os.path.join(root, real_f))
                        f = real_f
                    dir_list.append(os.path.join(root, f))

        for c_n in need_change_dirs_name:
            os.rename(c_n[0], c_n[1])
            for f_n in range(0, len(dir_list)):
                if dir_list[f_n].startswith(c_n[0]):
                    dir_list[f_n] = dir_list[f_n].replace(c_n[0], c_n[1])
        return dir_list

    def get_all_dirs(self, path, exc_dir_name=['__MACOSX']):
        """
        获取当前路径下所有的文件夹路径
        :param path: 需查找的路径
        :param exc_file_name: 排除的文件名称列表，不会返回此文件的路径
        :param need_type: list 类型， list中为需要保留的并返回的文件格式，此类型的文件路径会被返回
        :return: [路径1, 路径2, 路径3...]查找到的所有符合要求的文件绝对路径组成的list
        """
        dir_list = []
        dir_list.append(path)
        for root, dirs, files in os.walk(path):
            for dir_i in dirs:
                dir_list.append(os.path.join(root, dir_i))
        return dir_list

    def path_list(self, folder_path):
        """
        将路径以路径分隔符：/ ，\\进行拆分转化为list
        :param folder_path: 文件路径、目录:例如 a/b/c/d
        :return: [a,b,c,d]
        """
        separator = os.path.sep
        list_path = folder_path.split(separator)
        return list_path

    def clear_folder(self, root_path, ignore_type=[".xls", ".xlsx"]):
        """
        清除 root_path 目录下，除主目录下的ignore_type类型以外的所有文件夹及文件（若二级文件夹中存在ignore_type类型的文件，不会被保留）
        :param root_path: 需要清除的目录
        :param ignore_type: 主目录下需要被保留的文件格式
        :return: 无返回值
        """

        ls = os.listdir(root_path)
        for i in ls:
            c_path = os.path.join(root_path, i)
            if os.path.isdir(c_path):
                shutil.rmtree(c_path)
            elif os.path.splitext(c_path)[1] not in ignore_type:
                os.remove(c_path)

    def create_dirs(self, path_list):
        """
        创建path_list中的目录,当文件存在时，不生成新的py文件
        :param path_list: [dir1, dir2, dir3...]
        :return: 无返回值
        """
        for path in path_list:
            if os.path.exists(path):
                pass
            else:
                os.makedirs(path)
