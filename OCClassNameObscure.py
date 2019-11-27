# coding: utf-8
import os
import re
import random
import chardet
import hashlib
import sys

system_class_list = []

(filepath, temp_filename) = os.path.split(sys.argv[0])
dir_path = filepath
class_path = os.path.join(dir_path, "file/OC_Class.txt")
file_category_names = []
obscure_class_dic_path = "dir_path/OCClassObscure.txt"
with open(class_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_class_list = file_object.readlines()
temp_special_import_list = []
min_length = 8
category_super_class_list = []
top_dir = ''
'''忽略文件，例如.a的头文件'''
ignore_file_path_list = []
'''不忽略的特殊文件'''
no_ignore_files = ['Assets/config.xml']
'''需要忽略的类名
'''
ignore_class_name_list = ['AppDelegate', 'AFHTTPBodyPart']

'''需要忽略的文件名'''
ignore_file_list = ['RUIKit', 'R']
'''需要过滤的类名前缀 Theme里边用了某些自己的静态库，静态库中引用了某些GCTTheme开头的类'''
ignore_class_pre_list = ['GCTTheme']
'''去除\n'''
# ignore_dir_list = ['Pods']
ignore_dir_list = ['.framework', 'Protobuf', 'AFNetworking', 'FMDB']
for value in system_class_list:
    index = system_class_list.index(value)
    if value.endswith('\n'):
        value = value.replace('\n', '')
    system_class_list[index] = value

oc_file_types = [".h", ".cpp", ".inl", ".hpp", ".m", ".mm", ".c", ".cc", ".frag", ".vert"]
'''类名列表'''
oc_class_name_list = []
'''混淆后的映射表'''
oc_class_name_dic = {}
prefix_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
               "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
oc_file_type = [".h", ".m", ".mm"]
oc_obscure_file_type = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]


def get_random_number_5_10():
    return random.randint(5, 10)


def get_random_string(length=8):
    seed = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
        salt = ''.join(sa)
    return salt


def get_class_name_with_match_string(local_match_string):
    global modification_list
    match_string = local_match_string.strip()
    match_list = []
    if '@interface' in match_string:
        match_string = match_string.split(":")[-1]
    if ":" in match_string:
        match_list = match_string.split(":")
        match_string = match_list[0]
        match_string = match_string.strip()
    match_list = match_string.split(" ")
    match_string = match_list[-1]
    match_string = match_string.replace(";", "")
    match_string = match_string.replace("<", "")
    return match_string


def is_no_ignore_file(file_path):
    for path in no_ignore_files:
        if path in file_path:
            return True
    return False


def is_ignore_path(file_path):
    for ignore_file_path in ignore_file_path_list:
        if ignore_file_path in file_path:
            return True
    return False


def is_ignore_class_name_pre(name):
    string = str(name)
    for value in ignore_class_pre_list:
        if string.startswith(value):
            return True
    return False


def is_ignore_file(s_file):
    for value in ignore_class_name_list:
        if value in s_file:
            return True
    return False


def is_in_ignore_dir_list(match_string):
    for v in ignore_dir_list:
        if v in match_string:
            return True
    return False


def is_category_file(file_name):
    for name in file_category_names:
        file_name = file_name
        if file_name in name.split('+'):
            return True
        if file_name == name:
            return True
    return False


def get_string_md5(match_string):
    md5obj = hashlib.md5()
    md5obj.update(match_string.encode("utf8"))
    _hash = md5obj.hexdigest()
    return str(_hash).upper()


# parm-mark 执行程序
def obfuscated_code():
    global oc_class_name_list
    global oc_class_name_dic
    global oc_file_type
    global oc_obscure_file_type
    global system_class_list
    global obscure_class_dic_path
    global ignore_file_path_list
    global top_dir
    top_dir = input("输入项目路径或直接拖入文件夹（例:E:\svn_reposition\ZheJiang）：\n")
    if top_dir == '':
        print("未输入,程序结束")
        return
    else:
        top_dir = top_dir.strip()
    if top_dir == '':
        print("未输入,程序结束")
        return
    if not os.path.exists(top_dir):
        print("文件夹不存在")
        return
    if not os.path.isdir(top_dir):
        print("文件不存在")
        return
    print("正在生成替换列表......")
    ''' 匹配声明类名 '''
    class_pattern = re.compile(
        r'(.)*@interface+[\s]*[_a-zA-Z]+([\s]+|;|<|:)')
    ''' 匹配类别类名 '''
    class_pattern_2 = re.compile(r'@interface.*\([\s]*[_a-zA-Z]+\)')
    ''' 匹配需要过滤特殊导入 例：#import<AA.h>'''
    class_pattern_3 = re.compile(r'#import[\s]+<((?!/).)*>')
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_in_ignore_dir_list(dir_path):
            print("过滤特殊文件夹，例如Pods、framework")
            continue
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            # if '+' in file_name:
            #     file_category_names.append(file_name)
            if file_type == '.a':
                ignore_file_path_list.append(dir_path)
                for dir_path2, sub_paths2, files2 in os.walk(dir_path, False):
                    for s_file2 in files2:
                        file_name2, file_type2 = os.path.splitext(s_file2)
                        ignore_file_list.append(file_name2)
    temp = []
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_in_ignore_dir_list(dir_path):
            print("过滤特殊文件夹，例如Pods、framework")
            continue
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            file_path = os.path.join(dir_path, s_file)
            print("正在扫描文件:" + file_path)
            if file_type not in oc_file_type:
                continue
            if file_name in ignore_file_list:
                continue
            if is_ignore_path(file_path):
                print("遍历类名：跳过静态库对应的头文件")
                continue
            if is_ignore_file(s_file):
                print("跳过忽略文件：" + file_path)
                continue
            # if is_category_file(file_name):
            #     print("跳过类别："+file_name)
            #     continue
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            # 获取结构体、类名列表
            with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
                file_content = file_object.readlines()
                for line_val in file_content:
                    m3 = class_pattern_3.match(line_val)
                    if m3:
                        g_list3 = m3.group()
                        if isinstance(g_list3, str):
                            match_string3 = str(g_list3)
                            match_string3 = match_string3.split('<')[-1]
                            match_string3 = match_string3.split('>')[0]
                            match_string3 = match_string3.strip()
                            match_string3 = match_string3.split('.')[0]
                            if match_string3 not in temp_special_import_list:
                                temp_special_import_list.append(match_string3)
                    if '@interface' not in line_val:
                        ''' 此行没有@interface直接跳过 '''
                        continue
                    line_val = line_val.replace('\n', '')
                    m = class_pattern.match(line_val)
                    m2 = class_pattern_2.match(line_val)
                    if m2:
                        ''' 匹配类别类名 '''
                        g_list2 = m2.group()
                        if isinstance(g_list2, str):
                            match_string2 = str(g_list2)
                            match_string2 = match_string2.split('(')[-1]
                            match_string2 = match_string2.split(')')[0]
                            if match_string2 in oc_class_name_list:
                                continue
                            if match_string2 in system_class_list:
                                continue
                            # 加入类名列表
                            if (match_string2 not in ignore_class_name_list) and (len(match_string2) >= min_length):
                                print("Object-C类名%d\n：" % len(oc_class_name_list))
                                temp.append(match_string2)
                            '''匹配到就不再匹配不是类别的类名'''
                            continue

                    if m:
                        g_list = m.group()
                        if isinstance(g_list, str):
                            match_string = str(g_list)
                            match_string = get_class_name_with_match_string(match_string)
                            if match_string in oc_class_name_list:
                                continue
                            if match_string in system_class_list:
                                continue
                            # 加入类名列表
                            if (match_string not in ignore_class_name_list) and (len(match_string) >= min_length):
                                print("Object-C类名%d\n：" % len(oc_class_name_list))
                                if not is_ignore_class_name_pre(match_string):
                                    oc_class_name_list.append(match_string)


    print("==========替换列表生成完成==========")
    ''' 过滤#import<AA.h>这种的类名AA '''
    for i in range(len(oc_class_name_list) - 1, -1, -1):
        special_value = oc_class_name_list[i]
        if special_value in temp_special_import_list:
            del oc_class_name_list[i]
    oc_class_name_list = sorted(oc_class_name_list, key=lambda i: len(i), reverse=True)
    test_index = 0
    for class_value in oc_class_name_list:
        test_index = test_index + 1
        random_string = "CCT" + get_random_string(get_random_number_5_10()) + get_random_string(get_random_number_5_10())
        oc_class_name_dic[class_value] = random_string
    temp_w_list = []
    for key1, value1 in oc_class_name_dic.items():
        string1 = key1+'    ->     '+value1+'\n'
        temp_w_list.append(string1)
    with open(obscure_class_dic_path, encoding="utf-8", mode="w+", errors="ignore") as file_object:
        file_object.write(''.join(temp_w_list))
    print('遍历：' + top_dir)
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_in_ignore_dir_list(dir_path):
            print("过滤特殊文件夹，例如Pods、framework")
            continue
        for s_file in files:
            file_path = os.path.join(dir_path, s_file)
            is_ignore = is_ignore_path(file_path)
            if is_ignore:
                print("遍历类名：跳过静态库对应的头文件"+file_path)
                continue
            if ".framework" in str(file_path):
                print('路径有.framework'+file_path)
                continue
            file_name, file_type = os.path.splitext(s_file)
            if file_name in ignore_file_list:
                print('文件名在忽略列表'+file_name)
                continue
            if file_type not in oc_obscure_file_type:
                if not is_no_ignore_file(file_path):
                    print('不是混淆文件类型' + s_file)
                    continue

            print("正在替换类名...:" + file_path)
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            obscure_oc_class_name(file_path, encode_type)


def obscure_oc_class_name(file_path, encode_type):
    global oc_class_name_dic
    global oc_class_name_list
    print(file_path)
    w_file_content = ''
    with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
        w_file_content = file_object.read()
    start_md5 = get_string_md5(w_file_content)
    file_name, file_type = os.path.splitext(file_path)

    for i, val in enumerate(oc_class_name_list):
        if val in w_file_content:
            random_class_string = oc_class_name_dic[val]
            left_list = [" ", ")", "(", "~", "<", "\n", ":", ",", ">", "\t", "\r", "*", "&", "!", "[", "=",
                         "{", "^", "return +", "return -"]
            right_list = [" ", ")", ":", ";", "\r", "\n", "*", "&", "(", ">", ",", "{", "\t", "<",
                          "]", ".", ' *)']
            for left_value in left_list:
                for right_value in right_list:
                    object_string = "%s%s%s" % (left_value, val, right_value)
                    change_string = "%s%s%s" % (left_value, random_class_string, right_value)
                    w_file_content = w_file_content.replace(object_string, change_string)
            left_list2 = ['initWithModuleClass:@\"', 'NSClassFromString(@\"', 'cacheName : @\"', ': @\"', '): @\"', '\n@\"', '\":@\"', '\": @\"', '- (', '[[']
            right_list2 = ['\" title', '\")', '\"];', '\"};' '\"\n};', '\":@{', '\",', '\"\n', ' *)', ' service]']
            for left_value2 in left_list2:
                for right_value2 in right_list2:
                    object_string = "%s%s%s" % (left_value2, val, right_value2)
                    change_string = "%s%s%s" % (left_value2, random_class_string, right_value2)
                    w_file_content = w_file_content.replace(object_string, change_string)
            w_file_content = replace(': @\"', '\"};', w_file_content, val, random_class_string)
            w_file_content = replace('itemClassName:@\"', '\"', w_file_content, val, random_class_string)
            if str(file_type) == '.xml':
                w_file_content = replace('name=\"', '\"', w_file_content, val, random_class_string)
                w_file_content = replace('value=\"', '\"', w_file_content, val, random_class_string)

    end_md5 = get_string_md5(w_file_content)
    if not start_md5 == end_md5:
        with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
            file_object.write(w_file_content)
    print("处理完成: " + file_path)


def replace(left, right, string, val, random_class_string):
    object_string = "%s%s%s" % (left, val, right)
    change_string = "%s%s%s" % (left, random_class_string, right)
    string = string.replace(object_string, change_string)
    return string


obfuscated_code()
print("混淆Object-C类名完成")
