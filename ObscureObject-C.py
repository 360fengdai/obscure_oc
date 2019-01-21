# coding: utf-8
import os
import re
import random
import chardet
import hashlib
import sys

system_func_list = []
system_class_list = []
system_property_list = []

(filepath, temp_filename) = os.path.split(sys.argv[0])
dir_path = filepath
property_path = os.path.join(dir_path, "OC_property.txt")
func_path = os.path.join(dir_path, "OC_Function.txt")
class_path = os.path.join(dir_path, "OC_Class.txt")

with open(property_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_property_list = file_object.readlines()
with open(func_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_func_list = file_object.readlines()
with open(class_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_class_list = file_object.readlines()

ignore_file_list = []
ignore_class_name_list = ["QuadCommand", "UserWrapper", "PaymentInterface", "UserInterface", "AVAudioSession", "CCDirectorCaller", "ProgressTimer", "FileUtils", "ScriptEngineManager", "LuaEngine", "GLViewImpl", "Application", "EventCustom", "EventListenerCustom", "Scheduler", "EventDispatcher", "Director"]

ignore_file_path_list = ["SDKConfig", "CCScheduler", "CCRef", "CCFileUtils", "CCDirector", "cocos/network", "TalkingDataBF", "PlatformInvoke", "cocos2d/external/curl",
                         "plugins/bfTalkingdata",
                    "mySdk/XianliaoSDK_iOS",
                    "cocos2d/external/tiff",
                    "cocos2d/external/lua/luajit",
                    "bianfeng/External/live2d/include",
                    "cocos2d/external/png",
                    "cocos2d/external/webp",
                    "cocos2d/external/websockets",
                    "cocos2d/external/freetype2",
                    "cocos2d/external/chipmunk",
                    "cocos2d/external/spidermonkey",
                    "cocos2d/external/jpeg",
                    "bianfeng/ProtocolManager",
                    "PluginTK",
                    "ios/InterfaceTk.h",
                    "cocos2d/cocos/platform/ios",
                    "cocos2d/cocos/renderer"]

cpp_type_list = [".cpp", ".h", ".hpp"]
cpp_type_with_header = [".h", ".cpp", ".inl", ".hpp", ".m", ".mm", ".c", ".cc",  ".frag", ".vert"]
change_file_type_list = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]
# key:file_name  value:replace_name
file_replace_name_dic = {}
file_replace_name_dic_keys = []
file_to_much_call_dic = {}
file_to_much_call_keys = []
# 类名列表
cpp_class_name_list = []
cpp_class_name_dic = {}
modification_list = ["CC_GUI_DLL", "CC_STUDIO_DLL", "CC_DLL", "CC_LUA_DLL", "CC_EX_DLL", "CC_DEPRECATED_ATTRIBUTE"]

prefix_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
               "V", "W", "X", "Y", "Z"]
stuck_list = []
oc_file_type = [".h", ".m", ".mm"]
oc_obscure_file_type = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]
oc_func_list = []
oc_func_dic = {}
oc_property_list = []


ignore_sys_func_start_list = ["preferred", "Request", "Delegate", "Text", "ForKey", "replaceObject", "interst", "finish", "dismiss", "remove", "appendString", "removeLastObject", "closeKeyboard", "performSelector",
                              "removeObserver", "isBackgroundMusicPlaying", "rewind", "resume", "pause", "stop", "play",
                              "preload", "disableScreenSaver", "supported", "should", "insertObject", "call",
                              "isSupportFunction", "dictionary", "array", "webView", "layout", "resume", "touches",
                              "showAchievements", "audioSession", "caretRectForPosition",
                              "positionFromPosition", "resignFirstResponder", "becomeFirstResponder", "cdAudio",
                              "audioPlayer", "imagePicker", "openAL", "track", "mark", "text", "auto", "alert",
                              "load", "table", "prefer", "can", "dealloc", "application", "Did", "did", "view", "init"]


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
    for m_value in modification_list:
        if m_value in match_string:
            match_string.replace(m_value,"")
    match_list = []
    if ":" in match_string:
        match_list = match_string.split(":")
        match_string = match_list[0]
        match_string = match_string.strip()
    match_list = match_string.split(" ")
    match_string = match_list[-1]
    match_string = match_string.replace(";", "")
    match_string = match_string.replace("<", "")
    return match_string


def is_ignore_path(file_path):
    for ignore_file_path in ignore_file_path_list:
        if ignore_file_path in file_path:
            return True
    return False


def get_cpp_func_string(match_string):
    match_string = str(match_string)

    match_string = match_string.strip()
    match_list = match_string.split(")", 1)
    match_func_string = match_list[-1]
    if ":" in match_string:
        match_temp_list = match_func_string.split(":")
        match_func_string = match_temp_list[0]
    match_func_string = match_func_string.strip()
    match_func_string = match_func_string.replace(";", "")
    match_func_string = match_func_string.replace("{", "")
    match_func_string = match_func_string.strip()
    return match_func_string


def is_ignore_file(s_file):
    for value in ignore_class_name_list:
        if value in s_file:
            return True
    return False


def is_ignore_sys_function(match_string):
    match_string = str(match_string)
    for ignore_start in ignore_sys_func_start_list:
        if ignore_start in match_string:
            return True

    return False


def get_oc_property_string(match_string):
    match_string = str(match_string)

    match_string = match_string.strip()
    if "*" in match_string:
        match_list = match_string.split("*")
        match_string = match_list[-1]
    else:
        match_list = match_string.split(" ")
        match_string = match_list[-1]

    match_string = match_string.strip()
    match_string = match_string.replace(";", "")
    match_string = match_string.replace("{", "")
    match_string = match_string.strip()
    return match_string


def get_string_md5(match_string):
    md5obj = hashlib.md5()
    md5obj.update(match_string.encode("utf8"))
    _hash = md5obj.hexdigest()
    return str(_hash).upper()


# parm-mark 执行程序
def obfuscated_code():
    global stuck_list
    global cpp_type_list
    global file_replace_name_dic
    global file_replace_name_dic_keys
    global file_to_much_call_keys
    global file_to_much_call_dic
    global cpp_class_name_list
    global cpp_class_name_dic
    global oc_file_type
    global oc_obscure_file_type
    global oc_func_list
    global oc_func_dic
    global oc_property_list
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
    class_pattern = re.compile(
        r'[\s]*@interface+[\s]*[_a-zA-Z]+([\s]+|;|<|:)')
    oc_func_pattern = re.compile(r'[\s]*(-)[\s]*([(][\s]*(.*)[\s]*[*]?[\s]*[)])[\s]*[A-Za-z_]+(;|[\s]|{|:)')
    oc_property_pattern = re.compile(r'[\s]*@property[\s]*([(].*[)]).*;')
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            file_path = os.path.join(dir_path, s_file)
            print("正在操作文件:" + file_path)

            if file_type not in oc_file_type:
                continue
            is_ignore = is_ignore_path(file_path)
            if is_ignore:
                print("遍历类名：跳过静态库对应的头文件")
                continue
            ignore_file = is_ignore_file(s_file)
            if ignore_file:
                print("跳过忽略文件：" + file_path)
                continue
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            # 获取结构体、类名列表
            with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
                file_content = file_object.readlines()
                for line_val in file_content:

                    m3 = oc_property_pattern.match(line_val)
                    if m3:
                        m3_list = m3.group()
                        m3_match_string = str(m3_list)
                        property_string = get_oc_property_string(m3_match_string)
                        if property_string not in oc_property_list:
                            oc_property_list.append(property_string)
                    m2 = oc_func_pattern.match(line_val)
                    if m2:
                        m2_list = m2.group()
                        m2_match_string = str(m2_list)
                        func_string = get_cpp_func_string(m2_match_string)
                        if func_string not in oc_func_list:
                            if not is_ignore_sys_function(func_string):
                                print("oc_add_func:" + func_string)
                                oc_func_list.append(func_string)

                    m = class_pattern.match(line_val)
                    if m:
                        g_list = m.group()
                        if isinstance(g_list, str):
                            match_string = str(g_list)
                            match_string = get_class_name_with_match_string(match_string)
                            print("Object-C类名%d\n：" % len(cpp_class_name_list))
                            if match_string in cpp_class_name_list:
                                continue
                            if match_string[0] not in prefix_list:
                                continue
                            if match_string.startswith("UI"):
                                continue
                            if match_string.startswith("NS"):
                                continue
                            # 加入类名列表
                            if match_string not in ignore_class_name_list:
                                cpp_class_name_list.append(match_string)
    print("===========替换列表生成完成===========")
    del_list = []
    del_func_list = []
    del_class_list = []
    for i in range(len(cpp_class_name_list) - 1, -1, -1):
        s_val = cpp_class_name_list[i]
        set_val = "set" + s_val
        get_val = "get" + s_val
        if set_val in oc_func_list:
            del_func_list.append(set_val)
            if s_val not in del_class_list:
                del_class_list.append(s_val)

        if get_val in oc_func_list:
            del_func_list.append(get_val)
            if s_val not in del_class_list:
                del_class_list.append(s_val)
    for set_va in del_func_list:
        index_set = oc_func_list.index(set_va)
        del oc_func_list[index_set]
    for class_value in del_class_list:
        index = cpp_class_name_list.index(class_value)
        del cpp_class_name_list[index]
    del_func_list2 = []
    for i in range(len(oc_func_list) - 1, -1, -1):
        s_val = oc_func_list[i]
        s_val = str(s_val)
        if s_val.startswith("set"):
            del_func_list2.append(s_val)
    for del_func_value in del_func_list2:
        index_set = oc_func_list.index(del_func_value)
        del oc_func_list[index_set]

    get_func_list = []
    for i in range(len(oc_func_list) - 1, -1, -1):
        s_val = oc_func_list[i]
        get_val = "get" + s_val
        if get_val in oc_func_list:
            get_func_list.append(s_val)
            get_func_list.append(get_val)
    for get_va in get_func_list:
        index_set = oc_func_list.index(get_va)
        del oc_func_list[index_set]
    get_func_list2 = []
    for i in range(len(oc_func_list) - 1, -1, -1):
        s_val = oc_func_list[i]
        s_val = str(s_val)
        if s_val.startswith("get"):
            get_func_list2.append(s_val)
    for get_func_value in get_func_list2:
        index_set = oc_func_list.index(get_func_value)
        del oc_func_list[index_set]

    '''
    替换类名策略
    1.读取文件所有内容
    for循环类名表
    根据类名匹配本文件，前后各匹配一个字符
    '''
    for i in range(len(cpp_class_name_list) - 1, -1, -1):
        s_val = cpp_class_name_list[i]
        if len(s_val) < 12:
            del cpp_class_name_list[i]
        if s_val in stuck_list:
            del cpp_class_name_list[i]
    for i in range(len(oc_func_list) - 1, -1, -1):
        s_val = oc_func_list[i]
        if len(s_val) < 15:
            del oc_func_list[i]
    for ignore_value in ignore_class_name_list:
        if ignore_value in cpp_class_name_list:
            index = cpp_class_name_list.index(ignore_value)
            del cpp_class_name_list[index]
    if "ProgressTimer" in cpp_class_name_list:
        del cpp_class_name_list[cpp_class_name_list.index("ProgressTimer")]

    for property_string in oc_property_list:
        if property_string in oc_func_list:
            index = oc_func_list.index(property_string)
            del oc_func_list[index]

    cpp_class_name_list = sorted(cpp_class_name_list, key=lambda i: len(i), reverse=True)
    oc_func_list = sorted(oc_func_list, key=lambda i: len(i), reverse=True)
    test_index = 0
    for class_value in cpp_class_name_list:
        test_index = test_index + 1
        random_string = get_random_string(get_random_number_5_10()) + get_random_string(get_random_number_5_10())
        cpp_class_name_dic[class_value] = random_string
    test_index2 = 0
    for oc_func_value in oc_func_list:
        test_index2 = test_index2 + 1
        random_string2 = get_random_string(get_random_number_5_10()) + get_random_string(get_random_number_5_10())
        oc_func_dic[oc_func_value] = random_string2
    for value in oc_func_list:
        print(value + "  oc->" + oc_func_dic[value])
        if value in system_func_list:
            del system_func_list[value]

    for k in cpp_class_name_list:
        v = cpp_class_name_dic[k]
        if k in system_class_list:
            print("del object in system_class_list：" + k)
            del cpp_class_name_dic[k]

    for dir_path, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            if s_file == "sqlite3.c":
                continue
            file_path = os.path.join(dir_path, s_file)
            if ".framework" in str(file_path):
                continue
            file_name, file_type = os.path.splitext(s_file)
            print("操作文件中...:" + file_path)
            if file_type not in oc_obscure_file_type:
                continue
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            obscure_cpp_class_name(file_path, encode_type)


def obscure_cpp_class_name(file_path, encode_type):
    global cpp_class_name_dic
    global cpp_class_name_list
    print(file_path)
    w_file_content = ''
    with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
        lines = file_object.read()
        w_file_content = lines
    start_md5 = get_string_md5(w_file_content)
    for i, val in enumerate(cpp_class_name_list):
        if val in w_file_content:
            random_class_string = cpp_class_name_dic[val]
            left_list = [" ", ")", "(", "~", "<", "\n", ":", ",", ">", "\t", "\r", "*", "&", "!", "[", "=", "/", "{"]
            right_list = [" ", ")", ":", ";", "\r", "\n", "*", "&", "(", ">", ",", "{", "\t", "<", "]"]
            for left_value in left_list:
                for right_value in right_list:
                    object_string = "%s%s%s" % (left_value, val, right_value)
                    change_string = "%s%s%s" % (left_value, random_class_string, right_value)
                    w_file_content = w_file_content.replace(object_string, change_string)

    for i, val in enumerate(oc_func_list):
        if val in w_file_content:
            random_class_string = oc_func_dic[val]
            left_list = [" ", ")", "(", "~", "<", "\n", ":", ",", ">", "\t", "\r", "*", "&", "!", "[", "=", "/",
                         "{", "."]
            right_list = [" ", ")", ":", ";", "\n", "*", "&", "(", ">", ",", "{", "\t", "<", "-", "]"]
            for left_value in left_list:
                for right_value in right_list:
                    object_string = "%s%s%s" % (left_value, val, right_value)
                    change_string = "%s%s%s" % (left_value, random_class_string, right_value)
                    w_file_content = w_file_content.replace(object_string, change_string)

    end_md5 = get_string_md5(w_file_content)
    if not start_md5 == end_md5:
        with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
            file_object.write(w_file_content)
    print("OC_处理完成: " + file_path)


obfuscated_code()
print("混淆Object-C类名、方法名完成")
