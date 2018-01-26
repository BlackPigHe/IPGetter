import socket
import urllib
import threading
import redis
import urllib.request

import time

r = redis.Redis(host='47.94.20.74', port=6379,db=0,charset='utf-8')#换成自己的IP

t1=time.time()
lock = threading.Lock()


b=0

# 验证代理IP有效性的方法
#使用多线程的方法来验证ip的有效性，可以将ip分成CPU线程数多出10倍就好，以20为例吧

for i in range(10):

    for j in range(int(r.scard('myIPset')/10)):
        singleIP=r.spop('myIPset',count=1) #获取每个的成员
        #print(singleIP)
        r.sadd("myIPset"+str(i),singleIP)
    r.save()

threads=[]


def test(setName):#给一个方法
    ie = r.sscan(setName, count=r.scard(setName))

    socket.setdefaulttimeout(5)  # 设置全局超时时间
    url = "https://www.baidu.com/"  # 打算爬取的网址
    for i in ie[1]:
        # print(str(i).split("'")[1])
        try:
            proxy_support = urllib.request.ProxyHandler({'http': str(i).split("'")[1] })
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64)")]
            urllib.request.install_opener(opener)
            res = urllib.request.urlopen(url).read()
            # lock.acquire()  # 获得锁
            # print(i, 'is OK')
            r.sadd('newIPset',i)
            # lock.release()  # 释放锁
        except Exception as e:
            #lock.acquire()
            print(i, e)
            r.srem('myIPset',i)
            #lock.release()

if __name__ == '__main__':

    for i in  range(10):
        t=threading.Thread(target=test,args={'myIPset'+str(i),})

        t.start();
        # print(i)

print(r.scard('myIPset'))
print(r.scard('myIPset1'))
r.save()
print(r.scard('newIPset'))
t2=time.time()

print(t2-t1)