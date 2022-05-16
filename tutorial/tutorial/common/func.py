# coding=utf-8
import inspect
import time,os,json,sys,uuid,urllib
import traceback

reload(sys)
sys.setdefaultencoding('utf8')
from const import *

def datetime(format='%Y-%m-%d %H:%M:%S'):
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    return time.strftime(format, time_local)

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