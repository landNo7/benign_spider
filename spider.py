import os
import re
import wget
import requests
import subprocess
from lxml import etree
from requests.adapters import HTTPAdapter


header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,\
    */*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
}

header1 = {
    'Referer': 'https://dl.pconline.com.cn/download/2692033.html'	,
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
}


class GetUrl(object):
    def __init__(self):
        self.dir_path = 'install_exe/'
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        self.get_token_head = "https://dlc2.pconline.com.cn/dltoken/"
        self.get_token_end = "_genLink.js"
        self.url_head = "https:"
        self.dowload_url = []
        self.url_list = []
        self.xpath_menu = '//*[@id="Jsort"]/div[2]/ul/li/dl/dt/a/@href'
        self.xpath_dowload = '//*[@id="Jwrap"]/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div/div/div[1]/p/a/@href'
        self.xpath_next_page = '//*[@id="Jwrap"]/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/a/@href'
        self.xpath_temp_exe_link = '//*[@id="local_0"]/a[1]/@tempurl'
        self.page = requests.session()
        self.page.mount('https://', HTTPAdapter(max_retries=3))
    def get_url(self, url, status):

        self.page.headers = header
        p = self.page.get(url, timeout=20)
        print(url + " https status: %s" % p.status_code)
        html = etree.HTML(p.text)
        p.close()
        if 0 == status:
            urls = html.xpath(self.xpath_menu)
            urls = urls[0:-1]
            for _url in urls:
                self.get_url(self.url_head + str(_url), status=1)
            # self.get_exe_url()
        elif 1 == status:
            urls = html.xpath(self.xpath_dowload)
            self.dowload_url += urls
            pages = html.xpath(self.xpath_next_page)
            pages = pages[0:-2]
            for next_page in pages:
                self.get_url(self.url_head + str(next_page), status=2)
        else:
            urls = html.xpath(self.xpath_dowload)
            self.dowload_url += urls

    def get_exe_url(self):
        self.page.headers = header
        for url in self.dowload_url:
            # print(url)
            url, exe_id = self.get_link(url)
            url = self.url_head + url
            p = self.page.get(url, timeout=20)
            print(url + " exe https status: %s" % p.status_code)
            if 200 == int(p.status_code):
                html = etree.HTML(p.text)
                p.close()
                exe_url = html.xpath(self.xpath_temp_exe_link)[0]
                token = self.get_token(url, exe_id)
                exe_end = str(exe_url).split('/')[-1]
                token = token + '/' + exe_end
                exe_url = self.url_head + str(exe_url).replace(exe_end,token)
                # print(exe_url)
                if exe_url.endswith(".exe") or exe_url.endswith(".zip"):
                    # outfname = self.dir_path + '/' + exe_id + '.' + exe_url.split('.')[-1]
                    self.url_list.append(str(exe_url))
                    cmd = 'wget -P %s %s' % (self.dir_path, exe_url)
                    subprocess.call(cmd, shell=True)
                    # wget.download(exe_url,out=outfname)
            else:
                p.close()
                continue
    
    def get_link(self,url):
        url_end = '-1'
        url_end1 = '&linkPage=1'
        tempurl = str(url).split('/')
        if 7 == len(tempurl):
            end = url_end1 + '.' + tempurl[-1].split('.')[-1]
            exe_id = re.findall(r"\d+",tempurl[-1])[0]
            url = str(url).replace('.html',end)
        elif 5 == len(tempurl):
            end = url_end + '.' + tempurl[-1].split('.')[-1]
            exe_id = tempurl[-1].split('.')[0]
            url = str(url).replace('.html',end)
        else:
            print("no found" + url)
            return None, 0
        return url, exe_id

    def get_token(self, url, exe_id):
        header1['Referer'] = url
        self.page.headers = header1
        token_url = self.get_token_head + str(exe_id) + self.get_token_end
        p = self.page.get(token_url, timeout=20)
        token = str(p.text).split('\'')[1]
        p.close()
        return str(token)

    # 获取分类url列表
    def get_list(self):
        return self.url_list

    # 去重
    def rd_list(self):
        temp = list(set(self.url_list))
        temp.sort(key=self.url_list.index)
        self.url_list = temp


if __name__ == '__main__':
    url = 'https://dl.pconline.com.cn/'
    G = GetUrl()
    G.get_url(url, status=0)
    G.get_exe_url()
    List = G.get_list()
    print(len(List))
    G.rd_list()
    List = G.get_list()
    print(len(List))
    with open('urls.txt', 'a+') as aw:
        for url in List:
            aw.write(url+'\n')
    # url = 'https://dl.pconline.com.cn/'
    # url1 = 'https://dl.pconline.com.cn/sort/12.html'
    # url2 = '//dl.pconline.com.cn/download/2692033.html'
    # url3 = '//dl.pconline.com.cn/html_2/1/97/id=45518&pn=0.html'
    # token_url = 'https://dlc2.pconline.com.cn/dltoken/2692033_genLink.js'
    # page = requests.session()
    # page.headers = header

    # G = GetUrl()
    # url2, exe_id = G.get_link(url3)
    # print(url2, exe_id)
    # url2 = G.url_head + url2
    # p = page.get(url=url2)
    # print(p.status_code)
    # p.close()
    # html = etree.HTML(p.text)

    # xpath = '//*[@id="local_0"]/a[1]/@tempurl'
    # tempurl = html.xpath(xpath)
    # exe_url = str(tempurl[0])
    # token = G.get_token(url2, exe_id)
    # print(token)
    # exe_end = str(exe_url).split('/')[-1]
    # token = token + '/' + exe_end
    # exe_url = G.url_head + str(exe_url).replace(exe_end,token)
    # print(exe_url.endswith(".exe"))