# coding=utf-8
import hashlib
import inspect
import re
import time,os,json,sys,uuid,urllib,math,psutil,random,decimal
import traceback

reload(sys)
sys.setdefaultencoding('utf8')
from const import *

import oss2,requests

def load_header_string(header_string):
    arr = header_string.split('\n')
    headers = {}
    for v in arr:
        search = re.search(r'^[\s\n]*?((?!\:)\S+?)\:[\s]*?(\S*?)$', v)
        if(search):
            headers[search.group(1)] = search.group(2)
    return headers

def hex_str(str):
    hexs=''
    for v in str.decode():
        hexs += '\\u'+v.encode('hex')
    return hexs

def aliyun_upload_url_file(url):

    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    auth = oss2.Auth('id', 'mm')
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    search = re.search( r'(\.(png|jpg|jpeg|gif)(?!.*\.(png|jpg|jpeg|gif))).*', url, re.I)
    suffix = '.jpg'
    if search:
        suffix = search.group(1)
    filename = datetime('%Y%m%d') +'/'+ hashlib.md5(tuuid()).hexdigest() + suffix
    bucket_name = '-oss'
    region = 'http://oss-cn-shenzhen.aliyuncs.com'
    bucket = oss2.Bucket(auth, region, bucket_name)
    input = requests.get(url, verify=False)
    result = bucket.put_object(filename, input)
    if result.status != 200:
        raise Exception('上传失败')
    return 'https://-oss.oss-cn-shenzhen.aliyuncs.com/'+ filename

def datetime(format='%Y-%m-%d %H:%M:%S'):
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    return time.strftime(format, time_local)

def tuuid(return_num=False):
    #时刻变化
    id = str(decimal.Decimal(time.time())).replace('.', '')[1:25]
    if return_num:
        return id;
    return radix(id, 36, 10)

def radix(number, to=62, fro=10):
    #先转换成10进制
    number = dec_from(number, fro)
    #再转换成目标进制
    number = dec_to(number, to)
    return number

def dec_to(num, to = 62):
    if to == 10 or to > 62 or to < 2:
        return num
    dict = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if to > 36:
        dict = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
    ret = ''
    num = int(num)
    while num > 0:
        ret = dict[num % to] + ret
        num = num / to
    return ret

def dec_from(num, fro = 62):
    if fro == 10 or fro > 62 or fro < 2:
        return num
    num = str(num)
    dict = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if fro > 36:
        dict = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
    len = len(num)
    dec = 0
    for i in range(0, len):
        pos = dict.find(num[i]);
        if pos >= fro:
            continue; #如果出现非法字符，会忽略掉。比如16进制中出现w、x、y、z等
    dec = math.pow(fro, len - i - 1) * pos + dec
    return dec

for i in range(0,10):
    tuuid()

def mkfile(filename, content):
    paths = filename.split('/')
    path = ''
    for i in range(len(paths) - 1):
        path += paths[i] + '/'
        if os.path.exists(path) is False:
            os.makedirs(path)
    with open(filename, 'a') as f:
        f.write(content)

def log(name, *args):
    info_list = []
    for i in range(len(args)):
        info_list.append(str(args[i]))
    log_info = {
        'info': info_list,
        'time': datetime()
    }
    mkfile(Const.LOG_PATH +'/'+ name + '/' + datetime('%Y-%m-%d') +'.log', json.dumps(log_info, indent=4, ensure_ascii=False))
    print '--------{} log--------'.format(name)
    print json.dumps(info_list).decode("unicode-escape")
    print '--------{} log-end--------'.format(name)
    return (name,) + args

def err_log(*args):
    ex_type, ex_msg, ex_tb = sys.exc_info()
    caller = traceback.extract_stack()[-2:-1][0]
    log_name = caller[0][caller[0].rfind('/')+1:] + str(caller[1])
    ex_f_tb = ()
    for v in traceback.format_tb(ex_tb):
        ex_f_tb = ex_f_tb + (v.strip().replace('\n', ''),)
    info = (log_name,) + ex_f_tb + (str(ex_type), str(ex_msg)) + args
    log(*info)
    return info

def save_img(img_url, path='/tel/'):
    path = Const.DATA_PATH + path
    if not os.path.exists(path):
        os.makedirs(path)
    suffix = os.path.splitext(img_url)[1]
    if not suffix:
        suffix = '.jpg'
    filename = '{}/{}{}'.format(path, uuid.uuid1(), suffix)
    urllib.urlretrieve(img_url, filename=filename)
    return filename

def pr(str):
    print '----------------------------------------------------------------{}'.format(inspect.stack()[1][3])
    print '[{}]'.format(str)
    print '----------------------------------------------------------------{}-end'.format(inspect.stack()[1][3])