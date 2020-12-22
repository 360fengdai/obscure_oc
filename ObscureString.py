# coding: utf-8
import os
import re
import random
import chardet
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

'''
使用说明：
1、混淆字符串的文件类型范围为：['.m', '.cpp']
2、只会搜索OC方法和C函数内的字符串，OC字符串@"xxx", C字符串"xxx"
3、宏定义的字符串请写原字符串至方法内，否则不会混淆
4、定义在方法或函数外的字符串，如需混淆，也需要手动移动字符串到方法内，在执行混淆脚本
5、多次执行不会重复混淆
6、静态变量字符串不支持混淆，当前行开头是static|constexpr|const时跳过混淆
7、NSString方法外部字符串不会混淆，判断逻辑为NSString是当前行开头且不在方法内

'''

def get_random_number_0_10():
    return random.randint(0, 10)


def get_random_string(length=8):
    seed = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for j in range(length):
        sa.append(random.choice(seed))
        salt = ''.join(sa)
    return salt


def get_random_object_name():
    return get_random_string(20 + get_random_number_0_10())


keys = [0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF, 0xEA, 0xEB, 0xEC, 0xED, 0xED]
file_type_list = ['.m', '.cpp']
out_put_path = os.path.join(run_output_path, 'ObscureString.txt')
out_put_error_path = os.path.join(run_output_path, 'ObscureStringError.txt')
out_put_no_change_str_path = os.path.join(run_output_path, 'ObscureStringNoChangeStr.txt')
out_put_static_str_path = os.path.join(run_output_path, 'ObscureStringStatic.txt')
ignore_file_name_list = ['RCTSRWebSocket.m', 'MPStreamAdPlacer.m', 'mtaf_appender.cpp', 'json.cpp',
                         'EXLocationRequester.m', 'RCTEventDispatcher.m', 'R.h', 'R.m']
test_path = '/Users/chongliu/Desktop/ObscureStringTest.txt'


def get_random_number_0_10():
    return random.randint(0, 10)


def get_random_string(length=8):
    seed = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for j in range(length):
        sa.append(random.choice(seed))
        salt = ''.join(sa)
    return salt


def get_random_object_name():
    return get_random_string(20 + get_random_number_0_10())


def first_line(real_str, func_name):
    return "\n///%s\nstatic inline __attribute__((always_inline)) NSString *%s() {\n" % (real_str, func_name)


def first_line_c_str(real_str, func_name):
    return "\n///%s\nstatic inline __attribute__((always_inline)) char *%s() {\n" % (real_str, func_name)


def second_line(key_name, c_key):
    return "\tstatic char %s = (char) %s;\n" % (key_name, c_key)


def third_line(encrypted_str_name, c_length, encrypt_content):
    return "\tstatic char %s[%d] = %s;\n" % (encrypted_str_name, c_length, encrypt_content)


def fourth_line(decrypted_str_name, c_length):
    return "\tint i; char %s[%d];\n" % (decrypted_str_name, c_length + 1)


def fourth_line_c_str(decrypted_str_name, c_length):
    return "\tint i; static char %s[%d];\n" % (decrypted_str_name, c_length + 1)


def fifth_line(c_length, decrypted_str_name, encrypted_str_name, key_name):
    return "\tfor(i=0; i<%d; i++) {\n\t\t%s[i] = %s[i] ^ (char) ((%s + i) %% 256);\n\t}\n\t%s [%d] = \'\\0\';\n" % (
        c_length, decrypted_str_name, encrypted_str_name, key_name, decrypted_str_name, c_length)


def fifth_line_c_string(c_length, decrypted_str_name, encrypted_str_name, key_name, first_content):
    # c_number = (first_content + 1) % 128
    return "\tfor(i=0; i<%d; i++) {\n\
            %s[i] = %s[i] ^ (char) ((%s + i) %% 256);\n\t}\n\t%s [%d] = \'\\0\';\n" % (
        c_length, decrypted_str_name, encrypted_str_name, key_name, decrypted_str_name, c_length)
    # return "\tfor(i=0; i<%d; i++) {\n\t\t%s[i] = %s[i] ^ (char) ((%s + i) %% 256);\n\t}\n" % (
    #     c_length, decrypted_str_name, encrypted_str_name, key_name)


def sixth_line(decrypted_str_name):
    return "\treturn [NSString stringWithCString:%s encoding:NSUTF8StringEncoding];\n}\n" % decrypted_str_name


def sixth_line_c_str(decrypted_str_name):
    return "\treturn (char *) %s;\n}\n" % decrypted_str_name


def obscure_func_str(real_str, func_name, key_name, key, encrypted_str_name, length, encrypted_content,
                     decrypted_str_name):
    return first_line(real_str, func_name) + second_line(key_name, hex(key)) + third_line(encrypted_str_name, length,
                                                                                          ''.join(
                                                                                              encrypted_content)) + fourth_line(
        decrypted_str_name, length) + fifth_line(length, decrypted_str_name, encrypted_str_name,
                                                 key_name) + sixth_line(decrypted_str_name)


def obscure_func_c_str(real_str, func_name, key_name, key, encrypted_str_name, length, encrypted_content,
                       decrypted_str_name,
                       content):
    return first_line_c_str(real_str, func_name) + second_line(key_name, hex(key)) + third_line(encrypted_str_name,
                                                                                                length,
                                                                                                ''.join(
                                                                                                    encrypted_content)) \
           + fourth_line_c_str(
        decrypted_str_name, length) + fifth_line_c_string(length, decrypted_str_name, encrypted_str_name,
                                                          key_name, content[0]) + sixth_line_c_str(
        decrypted_str_name)


def obscure_with_str(object_str, is_c_str=0):
    encrypted = ['{']
    d_length = len(object_str)
    d_key = keys[get_random_number_0_10()]
    d_content = []
    for i in range(0, d_length):
        c = ord(object_str[i])
        r = ((d_key + i) % 256) ^ c
        d_content.append(r)
        if i == d_length - 1:
            encrypted.append("(char) %s" % hex(r))
            encrypted.append("}")
        else:
            encrypted.append("(char) %s," % hex(r))
    d_func_name = get_random_object_name()
    d_key_name = get_random_object_name()
    d_encrypted_str_name = get_random_object_name()
    d_decrypted_str_name = get_random_object_name()
    w_string = ''
    if is_c_str == 0:
        w_string = obscure_func_str(real_str=object_str,
                                    func_name=d_func_name,
                                    key_name=d_key_name,
                                    key=d_key,
                                    encrypted_str_name=d_encrypted_str_name,
                                    length=d_length,
                                    encrypted_content=encrypted,
                                    decrypted_str_name=d_decrypted_str_name)
    else:
        w_string = obscure_func_c_str(real_str=object_str,
                                      func_name=d_func_name,
                                      key_name=d_key_name,
                                      key=d_key,
                                      encrypted_str_name=d_encrypted_str_name,
                                      length=d_length,
                                      encrypted_content=encrypted,
                                      decrypted_str_name=d_decrypted_str_name,
                                      content=d_content)

    return w_string, '%s()' % d_func_name


# print(obscure_with_str("PUSBZ-L6IA3-6O63J-YGV44-PHOWS-2XFA4", False)[0])
# print(obscure_with_str("430B62115DB5E9726F193792D78E0BD1", str_type=1))
# print(obscure_with_str("0123456789qwertyuiopasdfghjklzxcvbnm", str_type=1))


def obscure_start():
    top_dir = ''
    if run_input_path:
        top_dir = run_input_path
    else:
        top_dir = input("输入项目路径或直接拖入文件夹（例:E:\svn_reposition\ZheJiang）：\n")
    # top_dir = '/Users/chongliu/Desktop/5'
    top_dir = top_dir.strip()
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

    obscure_out_put_list = []
    obscure_out_put_error_list = []
    out_put_no_change_str_list = ['C方法替换时匹配到OC字符串:\n']
    out_put_static_str_list = ['静态字符串:\n']
    current_content = ''
    func_list = []
    need_write_list = []
    need_change_dic = {}
    changed_oc_str = []
    changed_c_str = []
    current_file_path = ''
    test_func_list = []
    test_func_ex_list = []

    def search_func(match_value):

        line = str(match_value.group())
        func_item = [line]
        tuple_temp = match_value.span()
        # char_pre = current_content[tuple_temp[0] - 1]
        char_index = tuple_temp[1]
        count = 1
        c_length = len(current_content)
        while count > 0:
            if char_index >= c_length - 1:
                # print('错误方法：%d, %s' % (char_index, line))
                obscure_out_put_error_list.append('错误方法：%d, %s' % (char_index, line))
                break
            char_suf = current_content[char_index]
            if char_suf == '{':
                count = count + 1
            elif char_suf == '}':
                count = count - 1
            char_index = char_index + 1
            func_item.append(char_suf)
        # print('方法:')
        # print(''.join(func_item))
        func_list.append(''.join(func_item))
        return line

    def change_create(match_value):
        tuple_temp = match_value.span()
        line = str(match_value.group())
        j = 1
        temp_c_line = []
        char_pre = ''
        c_current_func_str = ''.join(func_list)
        while char_pre != '\n':
            char_pre = c_current_func_str[tuple_temp[0] - j]
            temp_c_line.insert(0, char_pre)
            j = j + 1
            if tuple_temp[0] - j < 0:
                char_pre = '\n'

        temp_c_str = ''.join(temp_c_line)
        if re.match(r'[\s]*(static|constexpr|const)[\s]+.*', temp_c_str):
            # print("OC静态字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        if re.match(r'[\s]*(NSString)[\s]+.*', temp_c_str) and temp_c_str not in ''.join(func_list):
            # print("NSString方法外部字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        line = line.strip("@")
        line = line.strip("\"")
        if line in changed_oc_str:
            return line
        changed_oc_str.append(line)
        obscure_tuple = obscure_with_str(line, False)
        test_func_list.append(obscure_tuple[0])
        test_func_ex_list.append("\tprintf(\"\\nKey  :  %s\");\n" % line)
        test_func_ex_list.append("\tprintf(\"\\nValue:  %%s\", %s.UTF8String);\n" % (obscure_tuple[1]))
        obscure_out_put_list.append("\t\"%s\": \"%s\",\n" % (line, obscure_tuple[1]))
        print("需要混淆的OC字符串：%s, 混淆方法：%s" % (line, obscure_tuple[1]))
        if len(need_write_list) == 0:
            need_write_list.insert(0, '#import <Foundation/Foundation.h>\n')
        need_write_list.append(obscure_tuple[0])
        need_change_dic[line] = obscure_tuple[1]
        return line

    def change_create_c(match_value):
        line = str(match_value.group())
        tuple_temp = match_value.span()
        char_pre = ''
        c_current_func_str = ''.join(func_list)
        if tuple_temp[0] - 1 < len(c_current_func_str):
            char_pre = c_current_func_str[tuple_temp[0] - 1]
        if char_pre == "@":
            # print("C方法匹配到OC字符串:%s" % line)
            return line
        j = 2
        temp_c_line = [char_pre]
        while char_pre != '\n':
            char_pre = c_current_func_str[tuple_temp[0] - j]
            temp_c_line.append(char_pre)
            j = j + 1
            if tuple_temp[0] - j < 0:
                char_pre = '\n'
        temp_c_str = ''.join(temp_c_line)
        if re.match(r'[\s]*(static|constexpr|const)[\s]+.*', temp_c_str):
            # print("OC静态字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        if re.match(r'[\s]*(NSString)[\s]+.*', temp_c_str) and temp_c_str not in ''.join(func_list):
            # print("NSString方法外部字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        line = line.strip("\"")
        if line in changed_c_str:
            return line
        changed_c_str.append(line)
        obscure_tuple = obscure_with_str(line, True)
        test_func_list.append(obscure_tuple[0])
        test_func_ex_list.append("\tprintf(\"\\nKey  :  %s\");\n" % line)
        test_func_ex_list.append("\tprintf(\"\\nValue:  %%s\", %s);\n" % (obscure_tuple[1]))
        obscure_out_put_list.append("\t\"%s\": \"%s\",\n" % (line, obscure_tuple[1]))
        print("需要混淆的C字符串：%s, 混淆方法:%s" % (line, obscure_tuple[1]))
        need_write_list.append(obscure_tuple[0])
        need_change_dic[line] = obscure_tuple[1]
        return line

    def change_str_c(match_value):
        line = str(match_value.group())
        tuple_temp = match_value.span()
        char_pre = current_content[tuple_temp[0] - 1]
        temp_c_line = []
        j = 2
        if char_pre == "@" or char_pre == "\\" or char_pre == "\"":
            # print("C方法替换时匹配到错误字符串:%s" % line)
            out_put_no_change_str_list.append("%s:%s" % (line, current_file_path))
            return line
        while char_pre != '\n':
            char_pre = current_content[tuple_temp[0] - j]
            temp_c_line.insert(0, char_pre)
            j = j + 1
            if tuple_temp[0] - j < 0:
                char_pre = '\n'

        temp_c_str = ''.join(temp_c_line)
        if re.match(r'[\s]*(static|constexpr|const)[\s]+.*', temp_c_str) or re.match(r'[\s]*(#|//).*',
                                                                                     temp_c_str):
            # print("C替换时检测到静态字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        if re.match(r'[\s]*(NSString)[\s]+.*', temp_c_str) and temp_c_str not in ''.join(func_list):
            # print("NSString方法外部字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        c_line = line.strip("\"")
        if c_line in need_change_dic.keys():
            return need_change_dic[c_line]
        return line

    def change_str(match_value):
        line = str(match_value.group())
        tuple_temp = match_value.span()
        char_pre = current_content[tuple_temp[0] - 1]
        temp_c_line = []
        j = 2
        if char_pre == "@" or char_pre == "\\" or char_pre == "\"":
            # print("OC替换时匹配到错误字符串:%s" % line)
            out_put_no_change_str_list.append("%s:%s" % (line, current_file_path))
            return line
        while char_pre != '\n':
            char_pre = current_content[tuple_temp[0] - j]
            temp_c_line.insert(0, char_pre)
            j = j + 1
            if tuple_temp[0] - j < 0:
                char_pre = '\n'

        temp_c_str = ''.join(temp_c_line)
        if re.match(r'[\s]*(static|constexpr|const)[\s]+.*', temp_c_str) or re.match(r'[\s]*(#|//).*',
                                                                                     temp_c_str):
            # print("OC替换时检测到静态字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        if re.match(r'[\s]*(NSString)[\s]+.*', temp_c_str) and temp_c_str not in ''.join(func_list):
            # print("NSString方法外部字符串无法加固：%s" % temp_c_str)
            out_put_static_str_list.append(temp_c_str)
            return line
        c_line = line.strip("@")
        c_line = c_line.strip("\"")
        if c_line in need_change_dic.keys():
            return need_change_dic[c_line]
        return line

    def change_str_with(str_patton, c_content, c_func_list, c_need_write_list, t_change_create, c_change_str):
        # print(".")
        oc_func_pattern = re.compile(
            r"[\s]?(\-|\+)[\s]*([(][\s]*(.*)[\s]*[*]?[\s]*[)])[\s]*[A-Za-z_]+([\s]|.)*?{")
        c_func_pattern = re.compile(
            r"[\s]*(static)*[\s]*(void|int|bool|char|float|double|wchar_t)[\s]+[A-Za-z_]+[\w]+[\s]*\(.*\)([\s]|[\w])*?{")
        c_oc_func_pattern = re.compile(r"[\s]*(BOOL|NS|UI|CG)[\w*]*[\s]+[A-Za-z_]+[\w]+[\s]*\(.*\)([\s]|[\w])*?{")
        re.sub(oc_func_pattern, search_func, c_content)
        re.sub(c_func_pattern, search_func, c_content)
        re.sub(c_oc_func_pattern, search_func, c_content)
        re.sub(str_patton, t_change_create, ''.join(c_func_list))
        w_content_list_temp = re.sub(str_patton, c_change_str, c_content)
        current_w_list_temp = []
        current_w_list_temp.extend(c_need_write_list)
        current_w_list_temp.extend(w_content_list_temp)
        current_w_str_temp = ''.join(current_w_list_temp)
        return current_w_str_temp
    print("开始扫描...")
    for dir_path, sub_paths, files in os.walk(top_dir, False):
        for s_file in files:
            if s_file in ignore_file_name_list:
                continue
            file_path = os.path.join(dir_path, s_file)
            current_file_path = file_path
            file_name, file_type = os.path.splitext(s_file)
            if file_type not in file_type_list:
                continue
            print("正在处理...:%s" % file_path)
            # print("file_path: %s" % file_path)
            func_list = []
            need_write_list = []
            need_change_dic = {}
            current_content = ''
            f = open(file_path, 'rb')
            data = f.read()
            encode_type = chardet.detect(data)["encoding"]
            f.close()
            if s_file == 'AppDelegate+WiFi.m':
                encode_type = 'utf-8'
            with open(file_path, mode='r', encoding=encode_type, errors='ignore') as file_object:
                current_content = file_object.read()

            patton_str = r"@\"[a-zA-Z0-9_.-]+\""
            current_content = change_str_with(patton_str, current_content, func_list, need_write_list, change_create,
                                              change_str)
            '''
                两步加固独立，上一步加固oc字符串，生成的current_content就是替换完成后的结果
                先加密oc字符串，已经处理完@开头的oc字符串，剩余匹配到的是都c字符串
            '''
            func_list = []
            need_write_list = []
            need_change_dic = {}
            c_patton_str = r"\"[a-zA-Z0-9_.-]+\""
            current_content = change_str_with(c_patton_str, current_content, func_list, need_write_list,
                                              change_create_c, change_str_c)
            # func_list = []
            # need_write_list = []
            # c_func_pattern = r"[\s]*(void|int|bool|char|float|double|wchar_t)[\s]+[A-Za-z_]+[\w]*\(.*\)[\s]*{"
            # re.sub(oc_func_pattern, search_func, current_content)
            # re.sub(c_func_pattern, search_func, current_content)
            # re.sub(c_patton_str, change_create_c, ''.join(func_list))
            # w_content_list = re.sub(c_patton_str, change_str, current_content)
            # current_w_list = []
            # current_w_list.extend(need_write_list)
            # current_w_list.extend(w_content_list)
            # current_w_str = ''.join(current_w_list)
            with open(file_path, mode='w', encoding=encode_type, errors='ignore') as file_object:
                file_object.write(current_content)
            # print('1')
            # re.search(patton_str, current_content)
            # res = re.findall(patton_str, current_content)
            # print(res)

    w_test_list = []
    w_test_list.extend(test_func_ex_list)
    w_test_list.extend(test_func_list)
    # w_test = ''.join(w_test_list)
    print_str = ''.join(test_func_ex_list)
    func_str = ''.join(test_func_list)
    w_appdelegate_text = "#import \"AppDelegate.h\"\n%s\n@implementation AppDelegate\n- (BOOL)application:" \
                         "(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions " \
                         "{\n%s\nreturn YES;\n}\n@end" % (func_str, print_str)
    if len(obscure_out_put_list) == 0:
        return
    obscure_out_put_list = sorted(obscure_out_put_list, key=lambda x: len(str(x).split(':')[0]))
    obscure_out_put_list[-1] = obscure_out_put_list[-1].replace(",", "")
    obscure_out_put_list.insert(0, '{\n')
    obscure_out_put_list.append('}\n')
    with open(out_put_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
        file_object.write(''.join(obscure_out_put_list))
    with open(out_put_error_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
        file_object.write(''.join(obscure_out_put_error_list))
    with open(out_put_no_change_str_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
        file_object.write(''.join(out_put_no_change_str_list))
    with open(out_put_static_str_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
        file_object.write(''.join(out_put_static_str_list))
    with open(test_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
        file_object.write(w_appdelegate_text)


obscure_start()
print("字符串混淆执行结束")
end_time1 = datetime.now()
print("脚本oc_class_path运行时间：%s" % str((end_time1 - start_time).seconds))

# with open(file_path, mode='w', encoding='utf-8', errors='ignore') as file_object:
#     file_object.write(w_string)

# print("%s" % hex(141))

# for
