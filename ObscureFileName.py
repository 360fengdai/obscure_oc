# coding: utf-8
import os
import re
import random
import chardet
import sys

ignore_type_list = [".a"]
ignore_file_list = []

cpp_type_list = [".cpp", ".m", ".mm", ".c", ".cc", ".frag", ".vert"]
cpp_type_with_header = [".h", ".cpp", ".inl", ".hpp", ".m", ".mm", ".c", ".cc",  ".frag", ".vert"]
change_file_type_list = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]
# key:file_name  value:replace_name
file_replace_name_dic = {}
file_replace_name_dic_keys = []
file_to_much_call_dic = {}
file_to_much_call_keys = []
ignore_file_name_list = ["main", "sqlite3", "PluginProtocol", "OpenGLES"]
# xcode工程列表
xcodeproj_list = []
ignore_file_path_list = ["SDKConfig", "cocos/network", "CCRef", "CCFileUtils", "CCDirector", "CCScheduler"]


def is_ignore_path(file_path):
    for ignore_file_path in ignore_file_path_list:
        if ignore_file_path in file_path:
            return True
    return False


def get_random_number_10_20():
    return random.randint(10, 20)


def get_random_string(length=8):
    seed = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
        salt = ''.join(sa)
    return salt


def change_xcode_project(top_dir):
    print("===========修改xcode工程文件===========")
    global file_replace_name_dic
    global xcodeproj_list
    for dir_path1, sub_paths, files in os.walk(top_dir, False):
        if dir_path1.endswith(".xcodeproj"):
            print("xcode_proj_path:" + dir_path1)
            xcodeproj_list.append(dir_path1)
            tmp_path = dir_path1 + "/project.pbxproj_tmp"
            if os.path.exists(tmp_path):
                print("删除project.pbxproj_tmp：" + tmp_path)
                os.remove(tmp_path)
    for project_path in xcodeproj_list:
        print("file_name_path正在处理：" + project_path)
        project_encode_type = ''
        local_xcode_file_path = ''
        w_file_content = ''
        for dir_path2, sub_paths, files in os.walk(project_path, False):
            for s_file in files:
                file_path = os.path.join(dir_path2, s_file)
                if s_file == "project.pbxproj":
                    local_xcode_file_path = file_path
                    f = open(file_path, 'rb')
                    data = f.read()
                    project_encode_type = chardet.detect(data)["encoding"]
                    f.close()
                    break
        with open(local_xcode_file_path, mode='r', encoding=project_encode_type, errors='ignore') as file_object:
            w_file_content = file_object.read()
        for key, value in file_replace_name_dic.items():
            left_list = [" ", "/", "\r", "\n", "\t", "\""]
            right_list = ["."]
            for left_value in left_list:
                for right_value in right_list:
                    object_string = "%s%s%s" % (left_value, key, right_value)
                    change_string = "%s%s%s" % (left_value, value, right_value)
                    w_file_content = w_file_content.replace(object_string, change_string)

        with open(local_xcode_file_path, mode='w', encoding=project_encode_type, errors='ignore') as file_object:
            file_object.write(w_file_content)
        print("xcode工程配置处理完成: " + project_path)


# parm-mark 执行程序
def obfuscated_code():
    global cpp_type_list
    global file_replace_name_dic
    global file_replace_name_dic_keys
    global ignore_type_list
    global file_to_much_call_keys
    global file_to_much_call_dic
    global ignore_file_name_list
    top_dir = input("输入项目路径或直接拖入文件夹（例:E:\svn_reposition\ZheJiang）：\n")
    if top_dir == '':
        print("未输入,程序结束")
        return
    if top_dir == '':
        print("未输入,程序结束")
        return
    if not os.path.exists(top_dir):
        print("文件夹不存在")
        return
    if not os.path.isdir(top_dir):
        print("文件不存在")
        return
    print("file_name_path正在生成替换列表......")
    for dir_path4, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            if file_type not in cpp_type_list:
                continue
            if ".framework" in str(dir_path4):
                continue
            file_path = os.path.join(dir_path4, s_file)
            is_ignore = is_ignore_path(file_path)
            if is_ignore:
                continue
            if file_name not in file_replace_name_dic.keys():
                random_file_name = get_random_string(get_random_number_10_20()) + get_random_string(get_random_number_10_20())
                file_replace_name_dic[file_name] = random_file_name

    print("file_name_path===========替换列表生成完成===========")

    for i, v in file_replace_name_dic.items():
        file_replace_name_dic_keys.append(i)
    for ignore_name in ignore_file_name_list:
        if ignore_name in file_replace_name_dic_keys:
            del file_replace_name_dic[ignore_name]
            index = file_replace_name_dic_keys.index(ignore_name)
            del file_replace_name_dic_keys[index]

    change_xcode_project(top_dir)
    for dir_path5, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            file_path = os.path.join(dir_path5, s_file)
            if ".framework" in str(file_path):
                print("跳过file_name文件名字混淆")
                continue
            file_name, file_type = os.path.splitext(s_file)
            if file_type == ".xcodeproj":
                continue
            if file_type not in cpp_type_with_header:
                continue
            if file_name not in file_replace_name_dic_keys:
                continue
            random_file_name = file_replace_name_dic[file_name]
            new_file_path = file_path.replace(file_name + file_type, random_file_name + file_type)
            os.renames(file_path, new_file_path)
            print("正在重命名文件：" + file_name + file_type + "->" + random_file_name + file_type)
    print("file_name_path===========正在重命名文件完成===========")

    for dir_path6, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            file_path = os.path.join(dir_path6, s_file)
            file_name, file_type = os.path.splitext(file_path)
            if ".framework" in str(file_path):
                print("跳过file_name文件名字混淆")
                continue
            if file_type not in change_file_type_list:
                print("跳过文件：" + file_path)
                continue
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            obscure_file_name(file_path, encode_type, s_file)


def obscure_file_name(file_path, encode_type, s_file):
    global file_to_much_call_dic
    global file_to_much_call_keys
    print(file_path)
    file_content = []
    with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
        lines = file_object.readlines()
        file_content = lines
    for i, val in enumerate(file_content):
        # 导入
        pattern = re.compile(r'^[\s]*#[\s]*(include|import)[\s]*.*')
        m = pattern.match(str(val))
        if m:
            pattern_1 = re.compile(r'.*<.*>')
            m_1 = pattern_1.match(str(val))
            if m_1:
                if "<net" in str(val):
                    print("含有net库")
                    continue
                if "<sys" in str(val):
                    print("含有sys库")
                    continue
                if "<arpa" in str(val):
                    print("含有arpa库")
                    continue
                list_1 = val.split("<")
                list_2 = list_1[1].split(">")
                string_1 = list_2[0]
                list_3 = string_1.split("/")
                string_2 = list_3[-1]
                string_3, file_type = os.path.splitext(string_2)
                if string_3 in file_replace_name_dic_keys:
                    replace_file_name = file_replace_name_dic[string_3]
                    replaced_val = val.replace(string_3 + file_type, replace_file_name + file_type)
                    file_content[i] = replaced_val

            pattern_2 = re.compile(r'.*".*"')
            m_2 = pattern_2.match(str(val))
            if m_2:
                list_1 = val.split("\"")
                string_1 = list_1[1]
                string_2 = string_1
                if "/" in string_1:
                    list_3 = string_1.split("/")
                    string_2 = list_3[-1]
                string_3, file_type = os.path.splitext(string_2)
                if string_3 in file_replace_name_dic_keys:
                    replace_file_name = file_replace_name_dic[string_3]
                    replaced_val = val.replace(string_3 + file_type, replace_file_name + file_type)
                    file_content[i] = replaced_val
    with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
        write_content = ""
        write_content = write_content.join(file_content)
        file_object.write(write_content)
    print("file_name_path处理完成: " + file_path)


obfuscated_code()
print("混淆文件名字完成")
