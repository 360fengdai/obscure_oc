# coding: utf-8
import os
import re
import random
import chardet
import hashlib
import sys
from datetime import datetime

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

obscure_class_dic_path = os.path.join(run_output_path, 'OCClassObscure.txt')
dir_path = sys.path[0]
class_path = os.path.join(dir_path, "file/OC_Class.txt")
file_category_names = []
system_class_list = []
with open(class_path, encoding="utf-8", mode="r", errors="ignore") as file_object:
    system_class_list = file_object.readlines()
temp_special_import_list = []
min_length = 8
category_super_class_list = []
top_dir = ''
'''忽略文件，例如.a的头文件'''
ignore_file_path_list = []
'''不忽略的特殊文件'''
no_ignore_files = ['GCTCordovaConfig/Assets/config.xml']
'''需要忽略的类名
LKSDK引用：GCDAsyncSocket、MSWeakTimer、YTKRequest、YTKNetworkAgent、YTKRequest、MJRefreshNormalHeader、SDWebImageManager、JSONKeyMapper、
MJRefreshBackNormalFooter、MQQNetworkInfo
MQQNetworkInfo被引用:（GCTAccount、GCTVODPlayer+GCTStatistics、GCTAVPlayer+Statistic、GCTConnectionViewModel）
例：LKSDK是原生开发的，但是引入项目中已经是.framework形式，framework在查询类名和替换类名时都会被过滤掉，其中引用的类在外部被搜索到并替换，
就会导致LKSDK内部引用此类时找不到，所以这种结构本身就不大合理，.framework内部应该是一个完整的封闭系统

编码解码的类不能混淆，为了兼容已经保存到本地的数据，有这些：'AFHTTPSessionManager', 'AFURLSessionManager', 'AFSecurityPolicy',
                          'AFURLRequestSerialization', 'AFURLResponseSerialization', 'RACArraySequence',
                          'RACEmptySequence', 'RACSequence', 'RACTuple', 'RACUnarySequence', 'MPEngineInfo',
                          'GCTShuziAccountModel', 'GCTTravelPermissionModel', 'GCTVideoFoodDisplayCountModel',
                          'GCTVideoFoodPlayTimeModel'

'''
ignore_class_name_list = ['AppDelegate', 'AFHTTPBodyPart', 'MQQHotspotWiFi', 'MQQWiFi', 'GCTEvent', 'Private',
                          'JSONModel', 'TarsObject', 'GCTLoginEvent', 'GCTLogoutEvent', 'GCDAsyncSocket', 'MSWeakTimer',
                          'YTKRequest', 'YTKNetworkAgent', 'YTKRequest', 'MJRefreshNormalHeader', 'SDWebImageManager',
                          'JSONKeyMapper', 'MJRefreshBackNormalFooter', 'Reachability', 'MQQNetworkInfo',
                          'LBSAddressInfo', 'LBSLocationManager', 'SDWebImageDownloader', 'MBProgressHUD',
                          'AFHTTPSessionManager', 'AFURLSessionManager', 'AFSecurityPolicy',
                          'AFURLRequestSerialization', 'AFURLResponseSerialization', 'RACArraySequence',
                          'RACEmptySequence', 'RACSequence', 'RACTuple', 'RACUnarySequence', 'MPEngineInfo',
                          'GCTShuziAccountModel', 'GCTTravelPermissionModel', 'GCTVideoFoodDisplayCountModel',
                          'GCTVideoFoodPlayTimeModel']

'''需要忽略的文件名'''
ignore_file_list = ['RUIKit', 'R']
'''需要过滤的类名前缀 Theme里边用了某些自己的静态库，静态库中引用了某些GCTTheme开头的类'''
ignore_class_pre_list = ['GCTTheme']
'''去除\n'''
# ignore_dir_list = ['Pods']
'''
CNCore的类在其他类的Framework中大量饮用
ChasingGameSDK.framework引用了大量的第三方库，因ChasingGameSDK已经是编译完的状态，导致其他源码引入的第三方库都不能做混淆
'''
ignore_dir_list = ['.framework', '/Protobuf', '/AFNetworking', '/FMDB', '/Nimbus', '/CNCore', '/mopub-ios-sdk',
                   '/GCTTinyApp', '/ZFPlayer', '/KTVHTTPCache', '/MBProgressHUD', '/Headers/Private',
                   '/Headers/Public', '/React-Core', '/React']

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
oc_obscure_file_type = [".pch", ".h", ".m", ".hpp", ".cpp", ".mm", ".cc", ".c", ".inl", ".frag", ".vert", '.storyboard']


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
    global modification_list
    match_string = local_match_string.strip()
    match_list = []
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
    for value in ignore_file_path_list:
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
    top_dir = ''
    if run_input_path:
        top_dir = run_input_path
    else:
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
        r'(.)*@interface[\s]+[_a-zA-Z]+[\s]*[:][\s]*[_a-zA-Z]+[\s]*')
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_in_ignore_dir_list(dir_path):
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
    temp = []
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        if is_in_ignore_dir_list(dir_path):
            # print("过滤特殊文件夹，例如Pods、framework")
            continue
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
            if file_name in ignore_file_list:
                continue
            if is_ignore_path(file_path):
                # print("遍历类名：跳过静态库对应的头文件")
                continue
            if is_ignore_file(s_file):
                # print("跳过忽略文件：" + file_path)
                continue
            print("正在扫描文件:" + file_path)
            # if is_category_file(file_name):
            #     print("跳过类别："+file_name)
            #     continue
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
                    if '@interface' not in line_val:
                        ''' 此行没有@interface直接跳过 '''
                        continue
                    line_val = line_val.replace('\n', '')
                    m = class_pattern.match(line_val)
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
                                print("扫描到Object-C类名：%d\n：" % len(oc_class_name_list))
                                if not is_ignore_class_name_pre(match_string):
                                    oc_class_name_list.append(match_string)

    print("===========替换列表生成完成===========")
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
    temp_w_list = ['{\n']
    for key1, value1 in oc_class_name_dic.items():
        string1 = " \"%s\":\"%s\",\n" % (key1, value1)
        temp_w_list.append(string1)
    del_temp = temp_w_list[-1]
    del_temp = del_temp.replace(',', '')
    temp_w_list[-1] = del_temp
    temp_w_list.append('}')
    with open(obscure_class_dic_path, encoding="utf-8", mode="w+", errors="ignore") as file_object:
        file_object.write(''.join(temp_w_list))
    # print('遍历：' + top_dir)
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        # 查找时过滤，替换时不过滤
        # if is_in_ignore_dir_list(dir_path):
        #     print("过滤特殊文件夹，例如Pods、framework")
        #     continue
        # if '/Pods' in dir_path:
        #     continue
        # if is_ignore_pod(dir_path):
        #     continue
        for s_file in files:
            if s_file == 'GCTUIKit.h':
                print('1')
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
                    # print('不是混淆文件类型' + s_file)
                    continue

            print("正在处理...:" + file_path)
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            if s_file == 'AppDelegate+WiFi.m':
                encode_type = 'utf-8'
            obscure_oc_class_name(file_path, encode_type)
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        # if '/Pods' in dir_path:
        #     continue
        for s_file in files:
            file_path = os.path.join(dir_path, s_file)
            file_name, file_type = os.path.splitext(s_file)
            if file_name in oc_class_name_list:
                obscure_file_name = oc_class_name_dic[file_name]
                new_path = os.path.join(dir_path, obscure_file_name + file_type)
                # os.rename(file_path, new_path)
    # pbxproj_path = ''
    # for dir_path, sub_paths, files in os.walk(top_dir, False):
    #     if '/Pods' in dir_path:
    #         continue
    #     stop = False
    #     for s_file in files:
    #         if s_file == 'project.pbxproj':
    #             stop = True
    #             pbxproj_path = os.path.join(dir_path, s_file)
    #             break
    #     if stop:
    #         break
    # pbxproj_content = ''
    # f = open(file_path, 'rb')
    # data = f.read()
    # encode_type = chardet.detect(data)["encoding"]
    # f.close()
    # with open(pbxproj_path, mode='r', encoding=encode_type) as file_object:
    #     pbxproj_content = file_object.read()
    # for key1, value1 in oc_class_name_dic.items():
    #     pbxproj_content = pbxproj_content.replace(' %s.' % key1, ' %s.' % value1)
    # with open(pbxproj_path, mode='w', encoding=encode_type) as file_object:
    #     file_object.write(pbxproj_content)


def obscure_oc_class_name(file_path, encode_type):
    global oc_class_name_dic
    global oc_class_name_list
    # print(file_path)
    w_file_content = ''
    with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
        w_file_content = file_object.read()
    start_md5 = get_string_md5(w_file_content)
    file_name, file_type = os.path.splitext(file_path)
    random_class_string = ''
    old_v = ''

    def change(match_value):
        # global old_v
        # global random_class_string
        # global w_file_content
        # print('change: %s %s' % (old_v, random_class_string))
        line = str(match_value.group())
        tuple_temp = match_value.span()
        j = 1
        char_pre = w_file_content[tuple_temp[0] - j]
        char_suf = w_file_content[tuple_temp[1]]
        char_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
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
        if "#import" in temp_str or "#include" in temp_str or "URLForResource" in temp_str:
            return line
        return line.replace(old_v, random_class_string)

    for i, val in enumerate(oc_class_name_list):
        if val in w_file_content:
            random_class_string = oc_class_name_dic[val]
            old_v = val
            # count_s = 7
            # com_string = r"(.|\s){%d}%s(.|\s){%d}" % (count_s, val, count_s)
            com_string = r"%s" % old_v
            t_list = re.sub(com_string, change, w_file_content)
            w_file_content = ''.join(t_list)

    end_md5 = get_string_md5(w_file_content)
    if not start_md5 == end_md5:
        with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
            file_object.write(w_file_content)
    # print("处理完成: " + file_path)


def replace(left, right, string, val, random_class_string):
    object_string = "%s%s%s" % (left, val, right)
    change_string = "%s%s%s" % (left, random_class_string, right)
    string = string.replace(object_string, change_string)
    return string


obfuscated_code()
print("混淆Object-C类名完成")
end_time1 = datetime.now()
print("脚本oc_class_path运行时间：%s" % str((end_time1 - start_time).seconds))
