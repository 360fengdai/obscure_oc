# coding: utf-8
import os
import re
import random
import operator as op
import chardet
import shutil
import sys

test_top_dir = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/Library/Frameworks"
temp_list = sys.argv[0].split('/')
user_name = ''

for i in range(0, len(temp_list)):
    value = temp_list[i]
    if value == 'Users':
        user_name = temp_list[i+1]
property_path = "/Users/%s/Desktop/OC_property.txt" % user_name
func_path = "/Users/%s/Desktop/OC_Function.txt" % user_name
class_path = "/Users/%s/Desktop/OC_Class.txt" % user_name
ignore_type_list = [".a"]
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
# file_type_list = [".h", ".m", ".hpp", ".cpp", ".mm"]
# .frag|.vert
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
oc_header_dic_list = []
oc_func_dic = {}
oc_class_dic = {}
oc_property_dic = {}

modification_list = ["CC_GUI_DLL", "CC_STUDIO_DLL", "CC_DLL", "CC_LUA_DLL", "CC_EX_DLL", "CC_DEPRECATED_ATTRIBUTE"]

prefix_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
               "V", "W", "X", "Y", "Z"]
stuck_list = []

oc_system_header_type = [".h"]
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


def get_oc_func_string(match_string):
    match_string = str(match_string)

    match_string = match_string.strip()
    match_list = match_string.split(")", 1)
    match_func_string = match_list[-1]
    match_func_string = match_func_string.strip()
    if " " in match_func_string:
        match_func_string = match_func_string.split(" ")[0]
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


def space_string(count):
    s_string = ""
    for index in range(count):
        s_string = s_string + " "
    return s_string


def replace_space(input_string):
    match_string = str(input_string)
    match_string = match_string.replace("\t", " ")
    for index in range(30, 0, -1):
        s_string = space_string(index)
        if s_string in match_string:
            match_string = match_string.replace(s_string, " ")
    return match_string


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
        if " " in match_string:
            match_string = match_string.strip()
            match_string = match_string.split(" ")[0]
    else:
        match_string = match_string.split(")", 1)[-1]
        match_string = match_string.strip()
        if "  " in match_string or "\t" in match_string:
            match_string = replace_space(match_string)
            match_list = match_string.split(" ")
            match_string = match_list[1]
        elif ">" in match_string:
            match_string = match_string.split(">")[-1]
        else:
            match_list = match_string.split(" ")
            match_string = match_list[1]

    match_string = match_string.strip()
    match_string = match_string.replace(";", "")
    match_string = match_string.replace("{", "")
    match_string = match_string.strip()
    return match_string


# parm-mark 执行程序
def obfuscated_code():
    global stuck_list
    global cpp_type_list
    global file_replace_name_dic
    global file_replace_name_dic_keys
    global ignore_type_list
    global file_to_much_call_keys
    global file_to_much_call_dic
    global cpp_class_name_list
    global cpp_class_name_dic
    global oc_system_header_type
    global oc_obscure_file_type
    global oc_func_list
    global oc_property_list
    global oc_header_dic_list
    global oc_func_dic
    global oc_class_dic
    global oc_property_dic
    # top_dir = input("输入项目路径或直接拖入文件夹（例:E:\svn_reposition\ZheJiang）：\n")
    top_dir = test_top_dir

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
    print("正在生成替换列表......")
    class_pattern = re.compile(
        r'(.)*@interface+[\s]*[_a-zA-Z]+([\s]+|;|<|:)')
    oc_func_pattern = re.compile(r'[\s]*(-)[\s]*([(][\s]*(.*)[\s]*[*]?[\s]*[)])[\s]*[A-Za-z_]+(;|[\s]|{|:)')
    oc_property_pattern = re.compile(r'[\s]*@property[\s]*([(].*[)]).*;')
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            file_path = os.path.join(dir_path, s_file)
            print("正在执行：" + file_path)
            if file_type not in oc_system_header_type:
                print("获取OC系统方法跳过文件:" + file_path)
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
                        if not property_string == "":

                            if dir_path not in oc_property_dic.keys():
                                property_list = [{property_string: file_path}]
                                oc_property_dic[dir_path] = property_list
                            else:
                                property_list = oc_property_dic[dir_path]
                                if {property_string: file_path} in property_list:
                                    property_list.append({property_string: file_path})
                                    oc_property_dic[dir_path] = property_list
                            if property_string not in oc_property_list:
                                oc_property_list.append(property_string)
                        else:
                            print("OC_跳过return空字符串")

                    m2 = oc_func_pattern.match(line_val)
                    if m2:
                        m2_list = m2.group()
                        m2_match_string = str(m2_list)
                        func_string = get_oc_func_string(m2_match_string)
                        if func_string not in oc_func_list:
                            oc_func_list.append(func_string)

                        if dir_path not in oc_func_dic.keys():
                            s_func_list = [{func_string:file_path}]
                            oc_func_dic[dir_path] = s_func_list
                        else:
                            s_func_list = oc_func_dic[dir_path]
                            if func_string not in s_func_list:
                                s_func_list.append({func_string:file_path})
                                oc_func_dic[dir_path] = s_func_list

                    m = class_pattern.match(line_val)
                    if m:
                        print(m)
                        g_list = m.group()
                        if isinstance(g_list, str):
                            match_string = str(g_list)
                            print(match_string)
                            # class PluginUtilsIOS
                            print("匹配字符串:%s" % match_string)
                            print(file_path)
                            print(line_val)
                            match_string = get_class_name_with_match_string(match_string)

                            print("Object-C类名%d\n：" % len(cpp_class_name_list))
                            print("Object-C-SKS:" + match_string)
                            print("==========================\n")
                            if dir_path not in oc_class_dic.keys():
                                s_class_list = [{match_string: file_path}]
                                oc_class_dic[dir_path] = s_class_list
                            else:
                                s_class_list = oc_class_dic[dir_path]
                                if {match_string: file_path} not in s_class_list:
                                    s_class_list.append({match_string: file_path})
                                    oc_class_dic[dir_path] = s_class_list
                            if match_string in cpp_class_name_list:
                                continue
                            # 加入类名列表
                            cpp_class_name_list.append(match_string)

    # file_replace_name_dic_keys = file_replace_name_dic.keys()
    print("===========替换列表生成完成===========")
    print("===========替换列表生成完成===========")
    print("===========替换列表生成完成===========")
    print("===========替换列表生成完成===========")
    print("===========替换列表生成完成===========")
    p_write_string = ''
    f_write_string = ''
    c_write_string = ''
    index = 0
    index2 = 0
    index3 = 0
    for value in oc_property_list:
        p_write_string = p_write_string + "\n" + value
        print("property%d: " % index + value)
        index = index + 1
    for value in oc_func_list:
        f_write_string = f_write_string + "\n" + value
        print("oc_func%d: " % index2 + value)
        index2 = index2 + 1
    for value in cpp_class_name_list:
        c_write_string = c_write_string + "\n" + value
        print("oc_class%d: " % index3 + value)
        index3 = index3 + 1

    for key, values in oc_property_dic.items():
        for value in values:
            for s_key, s_value in value.items():
                print("oc_property:" + s_value + "     " + s_key)
    for key, values in oc_func_dic.items():
        for value in values:
            for s_key, s_value in value.items():
                print("oc_func:" + s_value + "     " + s_key)
    for key, values in oc_class_dic.items():
        for value in values:
            for s_key, s_value in value.items():
                print("oc_class:" + s_value + "     " + s_key)

    with open(property_path, encoding="utf-8", mode="w+", errors="ignore") as file_object:
        file_object.write(p_write_string)
    with open(func_path, encoding="utf-8", mode="w+", errors="ignore") as file_object:
        file_object.write(f_write_string)
    with open(class_path, encoding="utf-8", mode="w+", errors="ignore") as file_object:
        file_object.write(c_write_string)


obfuscated_code()
print("遍历OC系统Framework完成")
