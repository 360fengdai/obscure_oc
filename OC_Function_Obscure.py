# coding: utf-8
import os
import re
import random
import chardet
import hashlib
import sys
from datetime import datetime

'''
    oc方法混淆脚本使用说明： 总则：脚本是帮你做事，不是求你做事，所以要主动适配脚本 
    1、init/set/wr_/is开头的方法不混淆 
    2、过滤的路径可在脚本中改ignore_file_path_list对象。【'.framework', '/Protobuf', '/AFNetworking', '/FMDB', '/Headers/Private', 
        '/Headers/Public']】
    3、没有混淆C方法，只混淆了Object-C的方法 
    4、方法名字长度需要大于等于16，过小的方法名不值得做混淆
    
'''

temp_list = sys.argv

print("参数列表:")
print(temp_list)

run_output_path = ''
run_input_path = ''
if len(temp_list) == 3:
    run_input_path = temp_list[1]
    run_output_path = temp_list[2]

start_time = datetime.now()

if not run_output_path:
    temp_list_output = sys.argv[0].split('/')
    user_name = ''
    for i in range(0, len(temp_list_output)):
        value = temp_list_output[i]
        if value == 'Users':
            user_name = temp_list_output[i + 1]
            run_output_path = '/Users/%s/Desktop/ObscureOutput' % user_name

if not os.path.exists(run_output_path):
    os.mkdir(run_output_path)
system_func_list = []
system_class_list = []
system_property_list = []
obscure_class_dic_path = os.path.join(run_output_path, 'OCFunctionObscure.txt')
obscure_class_dic_path2 = os.path.join(run_output_path, 'OCFunctionObscure2.txt')
dir_path = sys.path[0]
func_path = os.path.join(dir_path, "file/OC_Function.txt")
property_path = os.path.join(dir_path, "file/OC_property.txt")
class_path = os.path.join(dir_path, "file/OC_Class.txt")

with open(property_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_property_list = file_object.readlines()
for v in system_property_list:
    index = system_property_list.index(v)
    if v.endswith('\n'):
        v = v.replace('\n', '')
    system_property_list[index] = v
with open(func_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_func_list = file_object.readlines()
for v in system_func_list:
    index = system_func_list.index(v)
    if v.endswith('\n'):
        v = v.replace('\n', '')
    system_func_list[index] = v
with open(class_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_class_list = file_object.readlines()
for v in system_class_list:
    index = system_class_list.index(v)
    if v.endswith('\n'):
        v = v.replace('\n', '')
    system_class_list[index] = v

ignore_file_list = ['RUIKit', 'R']
ignore_file_path_list = ['.framework', '/Protobuf', '/AFNetworking', '/FMDB', '/Headers/Private', '/Headers/Public',
                         '/React-Core', '/React']
cpp_type_list = [".cpp", ".h", ".hpp"]
cpp_type_with_header = [".h", ".cpp", ".inl", ".hpp", ".m", ".mm", ".c", ".cc", ".frag", ".vert"]
change_file_type_list = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]
# key:file_name  value:replace_name
file_replace_name_dic = {}
file_replace_name_dic_keys = []
file_to_much_call_dic = {}
file_to_much_call_keys = []
prefix_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
               "V", "W", "X", "Y", "Z"]
oc_file_type = [".h", ".m", ".mm"]
oc_obscure_file_type = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert"]
'''
    需要混淆的Pods库
'''
pod_need_list = ['GCTAccount', 'GCTAdvert', 'GCTAPM', 'GCTAudio', 'GCTCinema', 'GCTCitiesAndStations', 'GCTConfig',
                 'GCTCordovaConfig', 'GCTCordovaPlugins', 'GCTCoupon', 'GCTDataPersisten', 'GCTEventBus', 'GCTEvents',
                 'GCTFaceCheck', 'GCTFeed', 'GCTHome', 'GCTHTTPServer', 'GCTIDAuth', 'GCTIOSUtils', 'GCTLocation',
                 'GCTLogger', 'GCTLottie', 'GCTMapKitV2', 'GCTMediaPlayer', 'GCTMine', 'GCTNotificationCenter', 'GCTPay'
                 'GCTPromotionCenter', 'GCTPushKit', 'GCTQQ', 'GCTQRCode', 'GCTQuickLogin', 'GCTReact', 'GCTReservation',
                 'GCTResourceKit', 'GCTRiskDetective', 'GCTRouter', 'GCTSharedTravel', 'GCTShareKit', 'GCTShuziAccount',
                 'GCTShuziProxy', 'GCTStatistic', 'GCTTheme', 'GCTTinyApp', 'GCTToday', 'GCTTravel', 'GCTUIKit',
                 'GCTUser', 'GCTVideo', 'GCTWebView', 'GCTWiFiConnect', 'GCTWiFiSDK', 'GCTYouZanDebugKit',
                 'GCTYouZanKit', 'GCTZipArchive', 'GDTMobSDK', 'GKPageScrollView', 'NextGCT', 'react_module_bridge']

'''
    过滤方法场景
    1、静态库的头文件中有这个方法，其他地方的代码也定义了这个方法，自动过滤静态库后，仍然匹配到其他地方的这个方法，静态库头文件方法调用处
       替换时被替换
    2、
'''
oc_func_list = []
ignore_func_list = ['pauseTrackPlay', 'resumeTrackPlay', 'constants', 'afterDelay', 'continue', 'addUIBlock',
                    'startObserving', 'stopObserving', 'hasValue', 'constantsToExport', 'sendEventWithName',
                    'apiName##ServerAPI', 'recordViewControllerOnReady', 'recordWithViewController',
                    'recordViewController', 'extraModulesForBridge', 'formattingCityName', 'cityFromCityName',
                    'loginFromViewController', 'currentAccessWirelessNetwork', 'convertWithTravelModel',
                    'createNavigationController', 'replaceAnimationView', 'travelModelWithTravelID']
oc_property_list = []
oc_func_dic = {}
'''
block的get方法待处理
'''

ignore_sys_func_start_list = ['wr_', 'set', 'XMTrackPlay', 'is', 'init', 'didSelect', 'sizeFor', 'perform',
                              'format', 'display', 'draw', 'mj_', 'GCTSwizzling_']
# ignore_sys_func_start_list = ['numberOfRowsInsection', 'showAnimated', 'pickerColumnView', 'isEnabled',
#                               'removeSignalForKeyPath',
#                               'addSignalForkeyPath', 'cellIdentifier', 'makeSubViews', 'cellClassName',
#                               'stopRefreshAnimation',
#                               'accountID', 'continue', 'homeDatas', 'toAddTravel',
#                               'currentViewController', 'wifiSloganImageView', 'shareAction', 'initQuickLoginSDKs',
#                               'handleOpenURL',
#                               'processData', 'afterDelay', 'tabbarselectedcolor', 'wr_', 'set'
#                               ]

# ignore_sys_func_start_list = []

temp_func_math_dic = {}


def is_ignore_pod(file_path):
    pod_dir = '/Pods/'
    if pod_dir in file_path:
        for v in pod_need_list:
            c_pod_dir = pod_dir + v
            if c_pod_dir in file_path:
                return False
        return True
    else:
        return False


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
    match_string = local_match_string.strip()
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
    match_func_string = match_list[1]
    if ":" in match_string:
        match_temp_list = match_func_string.split(":")
        match_func_string = match_temp_list[0]
    match_func_string = match_func_string.strip()
    if " " in match_func_string:
        match_func_string = match_func_string.split(" ")[0]
    match_func_string = match_func_string.strip()
    match_func_string = match_func_string.replace(";", "")
    match_func_string = match_func_string.replace("{", "")
    match_func_string = match_func_string.strip()
    return match_func_string


def is_ignore_func_start_function(match_string):
    match_string = str(match_string)
    for ignore_start in ignore_sys_func_start_list:
        if match_string.startswith(ignore_start):
            return True

    return False


def get_string_md5(match_string):
    md5obj = hashlib.md5()
    md5obj.update(match_string.encode("utf8"))
    _hash = md5obj.hexdigest()
    return str(_hash).upper()


def get_oc_property_string(match_string):
    match_string = str(match_string)
    match_string = match_string.strip()
    if '^' in match_string:
        # print('block')
        match_string = match_string.split('^')[-1]
        match_string = match_string.split(')')[0]
    else:
        if "*" in match_string:
            match_list = match_string.split("*")
            match_string = match_list[-1]
        else:
            match_list = match_string.split(" ")
            match_string = match_list[-1]
        match_string = match_string.strip()
        if " " in match_string:
            match_string = match_string.split(" ")[0]
        match_string = match_string.replace(";", "")
        match_string = match_string.replace("{", "")
        match_string = match_string.strip()
    return match_string


# parm-mark 执行程序
def obfuscated_code():
    global oc_func_dic
    ignore_set_list = []
    top_dir = ''
    if run_input_path:
        top_dir = run_input_path
    else:
        top_dir = input("输入项目路径或直接拖入文件夹（例:E:\svn_reposition\ZheJiang）：\n")
    # top_dir = '/Users/chongliu/Desktop/5'
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
    print("正在扫描......")
    oc_func_pattern = re.compile(r'(\-|\+)[\s]*([(][\s]*(.*)[\s]*[*]?[\s]*[)])[\s]*[A-Za-z_]+([\s]|.)*?({|;)')
    oc_property_pattern = re.compile(r'[\s]*@property[\s]*([(].*[)]).*;')
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_ignore_path(dir_path):
            # print("过滤特殊文件夹，例如Pods、framework")
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
    # for value in ignore_file_list:
        # print('ignore_file_list：' + value)
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        '''
                    只混淆指定的库
                '''
        if is_ignore_pod(dir_path):
            continue
        for s_file in files:
            file_name, file_type = os.path.splitext(s_file)
            file_path = os.path.join(dir_path, s_file)

            if file_type not in oc_file_type:
                continue
            is_ignore = is_ignore_path(file_path)
            if is_ignore:
                # print("遍历类名：跳过静态库对应的头文件")
                continue
            print("正在扫描文件:" + file_path)
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            if s_file == 'AppDelegate+WiFi.m':
                encode_type = 'utf-8'
            # 获取结构体、类名列表
            with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
                file_content = file_object.readlines()
                for line_val in file_content:
                    func_match = oc_func_pattern.match(line_val)
                    property_match = oc_property_pattern.match(line_val)
                    if property_match:
                        property_match_list = property_match.group()
                        property_match_string = str(property_match_list)
                        property_string = get_oc_property_string(property_match_string)
                        if property_string not in oc_property_list and property_string and len(property_string) >= 1:
                            oc_property_list.append(property_string)
                    if func_match:
                        func_list = func_match.group()
                        func_match_string = str(func_list)
                        func_string = get_oc_func_string(func_match_string)
                        j1 = '(' not in func_string
                        j2 = ')' not in func_string
                        j3 = '^' not in func_string
                        j4 = func_string not in system_func_list
                        j5 = func_string not in system_class_list
                        j6 = func_string not in system_property_list
                        j7 = func_string not in oc_func_list
                        j8 = len(str(func_string)) >= 16
                        j9 = is_ignore_func_start_function(func_string)
                        j10 = func_string not in ignore_func_list
                        j12 = func_string.startswith("set")
                        if j12:
                            if len(func_string) < 4:
                                continue
                            char_up = func_string[3]
                            char_up = str(char_up).lower()
                            end_char = func_string[4:]
                            ignore_model = char_up + ''.join(end_char)
                            if ignore_model not in ignore_set_list:
                                ignore_set_list.append(ignore_model)

                        if j1 and j2 and j3 and j4 and j5 and j6 and j7 and j8 and not j9 and j10:
                            print("扫描到方法名:" + func_string)
                            oc_func_list.append(func_string)
                            temp_func_math_dic[func_string] = func_match_string + '分割' + file_path

    print("===========替换列表生成完成===========")
    del_func_list2 = []
    '''
        过滤set、get方法和指定过滤的方法
    '''
    temp_v_p_list = []
    temp_v_p_list.extend(ignore_set_list)
    for v_p in oc_property_list:
        temp_v_p_list.append(v_p)
        first_char = v_p[0]
        end_char_list = v_p[1:]
        first_char = str(first_char).upper()
        temp_v_p_list.append("set%s%s" % (first_char, ''.join(end_char_list)))

    for i in range(len(oc_func_list) - 1, -1, -1):
        s_val = oc_func_list[i]
        s_val = str(s_val)
        if s_val in temp_v_p_list:
            del_func_list2.append(s_val)
    # print(del_func_list2)
    for del_func_value in del_func_list2:
        index_set = oc_func_list.index(del_func_value)
        del oc_func_list[index_set]
    test_index2 = 0
    for oc_func_value in oc_func_list:
        test_index2 = test_index2 + 1
        random_string2 = get_random_string(get_random_number_5_10()) + get_random_string(
            get_random_number_5_10()) + get_random_string(get_random_number_5_10())
        if oc_func_value.startswith('initWith'):
            random_string2 = 'initWith' + random_string2
        elif oc_func_value.startswith('init'):
            random_string2 = 'init' + random_string2
        oc_func_dic[oc_func_value] = random_string2

    temp_keys = sorted(oc_func_dic.keys())
    temp_dic = {}
    for value_key in temp_keys:
        temp_dic[value_key] = oc_func_dic[value_key]
    oc_func_dic = temp_dic
    temp_w_list = ["{\n"]
    for key1, value1 in oc_func_dic.items():
        string1 = "\t\"%s\": \"%s\",\n" % (key1, value1)
        temp_w_list.append(string1)
    temp_w_list[-1] = str(temp_w_list[-1]).replace(",", "")
    temp_w_list.append("}")
    with open(obscure_class_dic_path, encoding="utf-8", mode="w", errors="ignore") as file_object:
        file_object.write(''.join(temp_w_list))
    temp_w_list2 = ["{\n"]
    for key2, value2 in temp_func_math_dic.items():
        string2 = "\t\"%s\": \"%s\",\n" % (key2, value2)
        temp_w_list2.append(string2)
    temp_w_list2[-1] = str(temp_w_list2[-1]).replace(",", "")
    temp_w_list2.append("}")
    with open(obscure_class_dic_path2, encoding="utf-8", mode="w", errors="ignore") as file_object:
        file_object.write(''.join(temp_w_list2))
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            if s_file == "sqlite3.c":
                continue
            file_path = os.path.join(dir_path, s_file)
            is_ignore = is_ignore_path(file_path)
            if is_ignore:
                # print("遍历类名：跳过静态库对应的头文件")
                continue
            if ".framework" in str(file_path):
                continue
            file_name, file_type = os.path.splitext(s_file)
            if file_name in ignore_file_list:
                continue
            if file_type not in oc_obscure_file_type:
                continue
            print("正在处理...:" + file_path)
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            if s_file == 'AppDelegate+WiFi.m':
                encode_type = 'utf-8'
            obscure_oc_func_name(file_path, encode_type)


def obscure_oc_func_name(file_path, encode_type):
    w_file_content = ''
    with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
        w_file_content = file_object.read()
    start_md5 = get_string_md5(w_file_content)
    random_class_string = ''
    old_v = ''
    is_change = False
    is_change = False

    def change(match_value):
        global is_change
        is_change = False
        line = str(match_value.group())
        tuple_temp = match_value.span()
        j = 1
        char_pre = w_file_content[tuple_temp[0] - j]
        char_suf = w_file_content[tuple_temp[1]]
        char_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/_'
        if char_pre in char_list or char_suf in char_list:
            return line
        temp_c_line = []
        while char_pre != '\n':
            char_pre = w_file_content[tuple_temp[0] - j]
            temp_c_line.insert(0, char_pre)
            j = j + 1
            if tuple_temp[0] - j < 0:
                char_pre = '\n'
        temp_str = ''.join(temp_c_line)
        if "#import" in temp_str:
            return line
        # print('change: %s %s' % (old_v, random_class_string))
        return line.replace(old_v, random_class_string)

    for i, val in enumerate(oc_func_list):
        if val in w_file_content:
            random_class_string = oc_func_dic[val]
            old_v = val
            com_string = r"%s" % old_v
            t_list = re.sub(com_string, change, w_file_content)
            w_file_content = ''.join(t_list)
    end_md5 = get_string_md5(w_file_content)
    if not start_md5 == end_md5:
        with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
            file_object.write(w_file_content)
    # print("处理完成: " + file_path)


obfuscated_code()
print("混淆Object-C方法名完成")
end_time1 = datetime.now()
print("脚本oc_class_path运行时间：%s" % str((end_time1 - start_time).seconds))
