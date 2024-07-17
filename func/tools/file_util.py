# 文件类操作
import os

class FileUtil:
    #获取子文件夹所有文件路径
    @staticmethod
    def get_child_file_paths(directory):
        child_file_paths = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                child_file_paths.append(os.path.join(root, file))
        return child_file_paths
    
    #获取子文件夹所有文件名称
    @staticmethod
    def get_subfolder_names(path):
        subfolder_names = []
        for root, dirs, files in os.walk(path):
            for file in files:
                subfolder_names.append(file.replace(".mp4",""))
        return subfolder_names