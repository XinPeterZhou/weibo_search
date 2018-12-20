# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 10:53:53 2018
微博信息爬虫
@author: baili
"""
import urllib.request
import json
import pandas as pd
from bs4 import BeautifulSoup

#设置代理IP
proxy_addr="122.241.72.191:808"

#定义页面打开函数
def use_proxy(url,proxy_addr):
    req=urllib.request.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy=urllib.request.ProxyHandler({'http':proxy_addr})
    opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data=urllib.request.urlopen(req).read().decode('utf-8','ignore')
    return data

def clean_text(content):
    
    soup = BeautifulSoup(content,"lxml") 
    return soup.get_text().strip()
    
if __name__=="__main__":
                
    #在这里输入要搜索的关键词 
    keywords=['樟木','竹海']

    
    for key in keywords:
        #建立输出文本的框架
        df=pd.DataFrame(columns=('姓名','大V认证','时间','来自','正文','全文','地址',
                             '点赞','评论','转发','图片','转发内容'))       
        for page in range(0,10):
            url='https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D'+urllib.request.quote(key)+'&page_type=searchall&page='+str(page+1)
            print(url)
            print('*'*40)
            #微博返回的json首页和其余的结构不一样
            data=use_proxy(url,proxy_addr)
            if page==0:
                content = json.loads(data)['data']['cards'][-1]['card_group']
            else:
                content = json.loads(data)['data']['cards'][0]['card_group']
            for item in range(0, len(content)):
                #print('*'*20+'第'+str(item)+'条'+'*'*20)
                df.loc[page*10+item,'姓名']=content[item]['mblog']['user']['screen_name']
                df.loc[page*10+item,'时间']=content[item]['mblog']['created_at']
                df.loc[page*10+item,'来自']=content[item]['mblog']['source']
                df.loc[page*10+item,'正文']=clean_text(content[item]['mblog']['text'])
                try:
                    df.loc[page*10+item,'全文']=clean_text(content[item]['mblog']['longText']['longTextContent'])
                except:
                    df.loc[page*10+item,'全文']='同上'
                try:
                    df.loc[page*10+item,'地址']=content[item]['scheme']
                except:
                    df.loc[page*10+item,'地址']='未获取'
                df.loc[page*10+item,'点赞']=content[item]['mblog']['attitudes_count']
                df.loc[page*10+item,'评论']=content[item]['mblog']['comments_count']
                df.loc[page*10+item,'转发']=content[item]['mblog']['reposts_count']
                try:
                    df.loc[page*10+item,'图片']=len(content[item]['mblog']['pics'])
                except:
                    df.loc[page*10+item,'图片']=0
                if content[item]['mblog']['user']['verified']:
                    df.loc[page*10+item,'大V认证']=content[item]['mblog']['user']['verified_reason']
                else:
                    df.loc[page*10+item,'大V认证']=''
                try:
                    df.loc[page*10+item,'转发内容']=clean_text(content[item]['mblog']['retweeted_status']['text'])
                except:
                    df.loc[page*10+item,'转发内容']='无'     
        df.to_excel('weibo_search_'+key+'.xls')