import urllib.request
import urllib
import re
import time
import random
import socket
import threading
import redis

r = redis.Redis(host='47.94.20.74', port=6379,db=0,charset='utf-8')#换成自己的IP
# 抓取代理IP
ip_totle = []
for page in range(2, 8):
    url = 'http://www.xicidaili.com/nn/%s' %page#字符串拼接，西刺代理
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}#设置浏览器协议头
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request) #用Request类构建了一个完整的请求，增加了headers等一些信息
    content = response.read().decode('utf-8')
    print('get page', page)#打印出获取哪一页
    pattern = re.compile('<td>(\d.*?)</td>')  # 截取<td>与</td>之间第一个数为数字的内容
    ip_page = re.findall(pattern, str(content))#在content里查找pattern
    ip_totle.extend(ip_page)#将ip_page追加到ip_totle里
    time.sleep(random.choice(range(1, 3)))#推迟运行随机1-3s
# 打印抓取内容
# print('代理IP地址     ', '\t', '端口', '\t', '速度', '\t', '验证时间')
# for i in range(0, len(ip_totle), 4):
#     print(ip_totle[i], '    ', '\t', ip_totle[i + 1], '\t', ip_totle[i + 2], '\t', ip_totle[i + 3])
# 整理代理IP格式
proxys = []
for i in range(0, len(ip_totle), 4):
    proxy_host = ip_totle[i] + ':' + ip_totle[i + 1]#IP和端口
    proxy_temp = proxy_host#加一个http
    proxys.append(proxy_temp)#把proxy_temp追加到proxys

# proxy_ip = open('proxy_ip.txt', 'w')  # 新建一个储存有效IP的文档
lock = threading.Lock()  # 建立一个锁


# 验证代理IP有效性的方法
def test(i):#给一个方法
    socket.setdefaulttimeout(5)  # 设置全局超时时间
    url = "https://www.baidu.com/"  # 打算爬取的网址
    try:
        proxy_support = urllib.request.ProxyHandler({'http':proxys[i]})
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64)")]
        urllib.request.install_opener(opener)
        res = urllib.request.urlopen(url).read()
        lock.acquire()  # 获得锁
        print(proxys[i], 'is OK')
        # proxy_ip.write('%s\n' % str(proxys[i]))  # 写入该代理IP
        lock.release()  # 释放锁
    except Exception as e:
        lock.acquire()
        print(proxys[i], e)
        lock.release()


# 单线程验证
'''for i in range(len(proxys)):
    test(i)'''
# 多线程验证
threads = []
for i in range(len(proxys)):
    thread = threading.Thread(target=test, args=[i])
    threads.append(thread)
    thread.start()
# 阻塞主进程，等待所有子线程结束
for thread in threads:
    thread.join()

# proxy_ip.close()  # 关闭文件

for i in proxys:
    r.sadd("myIPset",i)
    print(i)
r.save()
print(r.scard("myIPset"))
print(r.srandmember("myIPset", 1))

