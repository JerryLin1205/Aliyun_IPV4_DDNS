# pip install aliyun-python-sdk-core-v3
# pip install aliyun-python-sdk-domain
# pip install aliyun-python-sdk-alidns
# pip install requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import requests
import json
import time
import urllib.request
import ssl
import sys

# Disable https certification verification
ssl._create_default_https_context = ssl._create_unverified_context     

ipv4_flag = 1  						                # 是否开启ipv4 ddns解析,1为开启，0为关闭
accessKeyId = "xxxxxxx"  		                    # 将accessKeyId改成自己的accessKeyId
accessSecret = "xxxxxx"  	                        # 将accessSecret改成自己的accessSecret
domain = "xxxxx.com"  				                # 你的主域名

def update(RecordId, RR, Type, Value):  		    # 修改域名解析记录
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)

def add(DomainName, RR, Type, Value):  			    # 添加新的域名解析记录
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_RR(RR)  
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)

print("================开始执行程序=================")
print(time.strftime("%Y-%m-%d %H:%M:%S"))
ipAPIList = ["http://ip.42.pl/raw","http://myip.ipip.net/s","http://ident.me/","http://ip.3322.net/",
            "https://api-ipv4.ip.sb/ip","http://api.ipify.org/","http://ip.cip.cc/"]            
client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

for ipAPI in ipAPIList:
    try:
        #ip = urlopen('https://api-ipv4.ip.sb/ip').read()  	# 使用IP.SB的接口获取ipv4地址
        print("开始调用地址 %s" %ipAPI)
        ip = urlopen(ipAPI).read()
        ipv4 = str(ip, encoding='utf-8')
        print("获取到IPv4地址：%s" %ipv4)    
        break
    except (HTTPError, URLError) as e:
        print("当前地址发生异常，尝试下一个地址")
        if ipAPI == len(ipAPIList) - 1:
            print("退出脚本")
            sys.exit(1)
            
def ddns_update(RR):
    print("当前RR值：%s"%(RR))
    if ipv4_flag == 1:
        request = DescribeSubDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        request.set_SubDomain(RR + '.' + domain)

        response = client.do_action_with_exception(request)     # 获取域名解析记录列表
        domain_list = json.loads(response)                      # 将返回的JSON数据转化为Python能识别的

        if domain_list['TotalCount'] == 0:
            add(domain, RR, "A", ipv4)
            print("新建域名解析成功")
        elif domain_list['TotalCount'] == 1:
            if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv4.strip():
                update(domain_list['DomainRecords']['Record'][0]['RecordId'], RR, "A", ipv4)
                print("修改域名解析成功")
            else:  
                print("IPv4地址没变")
        elif domain_list['TotalCount'] > 1:
            from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
            request = DeleteSubDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_DomainName(domain)  
            request.set_RR(RR)
            response = client.do_action_with_exception(request)
            add(domain, RR, "A", ipv4)
            print("修改域名解析成功")

ddns_update("www")
ddns_update("@")

print(time.strftime("%Y-%m-%d %H:%M:%S"))
print("=================程序执行完毕====================")