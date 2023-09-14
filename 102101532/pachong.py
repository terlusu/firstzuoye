import re
import requests #发送请求
from bs4 import BeautifulSoup as BS #解析页面
import pandas as pd
import wordcloud#词云图

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ",
           'cookie': 'i-wanna-go-back=-1; buvid4=7CA6C66C-9E53-402E-4FB3-86BB25321B5067810-022042118-m4T90WVXeaj5G26gAjKaYw%3D%3D; CURRENT_BLACKGAP=0; buvid_fp_plain=undefined; LIVE_BUVID=AUTO4116507000856626; is-2022-channel=1; rpdid=|(u)luk)~Ym~0J'
                     'uYY)l~kl~~; DedeUserID=16011705; DedeUserID__ckMd5=105925b70444a4a0; b_ut=5; CURRENT_PID=a927ace0-ca1f-11ed-898a-4300e7154bd6; SESSDATA=06c8f662%2C1696484850%2Cbbd03%2A41; bili_jct=c80387e917cc62713bed4d39c6e2c4d1; buvid3=1E85ECCB-54F1-3AD2-9503-B0A6284BFFC780859infoc; b_nut=1682081080; _uuid=E51737102-73DE-D10ED-517F-D4CB510410EA8481131infoc; nostalgia_conf=-1; hit-new-style-dyn=1; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; CURRENT_QUALITY=120; hit-dyn-v2=1; CURRENT_FNVAL=4048; home_feed_column=5; fingerprint=516ec98d5607f4cd8370d1a8bda66d49; browser_resolution=2512-1292; PVID=1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQ3NzM1NzUsImlhdCI6MTY5NDUxNDM3NSwicGx0IjotMX0.nWzgzRMzHHfBVqGk-u8Ggckhv0IfLFX966Pn5Gzl_IM; bili_ticket_expires=1694773575; sid=77dlgodc; bp_video_offset_16011705=840712188628828185; buvid_fp=edbf7eca4807bba9865f98139494a341; b_lsid=95551010F8_18A8E245B62',
           'oringin': 'https://search.bilibili.com',
           'referer': 'https://search.bilibili.com/all?vt=94428707&keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6%B0%B4%E6%8E%92%E6%B5%B7&from_source=webtop_search&spm_id_from=333.788&search_source=3'}

#输入cookie 爬取视频的网址等等参数

def get_info(vid):
    url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={vid}"#获取视频链接
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    data = response.json()
    info = {}
    info["总弹幕数"] = data["data"]["View"]["stat"]["danmaku"]#获取总弹幕数量
    info["视频数量"] = data["data"]["View"]["videos"]#获取视频数量 要不要无所谓 纯属为了好看
    info["cid"] = [dic["cid"] for dic in data["data"]["View"]["pages"]]
    if info["视频数量"] > 1:
        info["子标题"] = [dic["part"] for dic in data["data"]["View"]["pages"]]#获取视频子标题 也是为了好看
    for k, v in info.items():
        print(k + ":", v)
    return info


def get_danmu(info):
    all_dms = []
    for i, cid in enumerate(info["cid"]):
        url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
        response = requests.get(url)
        response.encoding = "utf-8"
        data = re.findall('<d p="(.*?)">(.*?)</d>', response.text)
        dms = [d[1] for d in data]
        if info["视频数量"] > 1:
            print("cid:", cid, "弹幕数:", len(dms), "子标题:", info["子标题"][i])#输出cid 弹幕总数 视频子标题
        all_dms += dms
    print(f"共获取弹幕{len(all_dms)}条！")#输出获取到的弹幕数量
    return all_dms

def content_sort(danmu_list):#统计弹幕数量
    dan_counts = {}

    for dm in danmu_list:#将所有弹幕遍历一遍
        if dm in dan_counts:
            dan_counts[dm] += 1#如果有相同弹幕 则数量+1
        else:
            dan_counts[dm] = 1#空时 填入弹幕数量1

    px_word_counts = sorted(dan_counts.items(),key=lambda x:x[1],reverse=True)#将弹幕进行排序

    print(" 输出排名前20的弹幕：")

    for i in range(20):
        print("{}:{}".format(px_word_counts[i][0],px_word_counts[i][1]))

    return px_word_counts

def get_cloud(danmu_list):

    text="".join(danmu_list)
    wc = wordcloud.WordCloud(font_path="C:\Windows\Fonts\msyh.ttc",
                             width = 1000,
                             height = 700,
                             background_color='white')#设置云图参数
    wc.generate(text)# 加载词云文本
    wc.to_file("弹幕.png")# 保存词云文件

def get_bv(pages):

    for page in range(pages):#获取每一页视频的bv数据
        page += 1#从第一页开始
        r1 = requests.get(url='https://search.bilibili.com/all?keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6%B0%B4%E6%8E%92%E6%B5%B7&from_source=webtop_search&spm_id_from=333.788&search_source=2&page={}'.format(page), headers=headers)
        r1.encoding = 'utf-8'
        html1 = r1.text
        soup = BS(html1, 'xml')
        video_list = soup.find_all("a", class_="img-anchor")
        for i in range(20):#每一页的视频数量
            b_v = (video_list[i]).get('href')
            bvv = b_v[25:37]
            bv_list.append(bvv)#获取到的bv号进行保存

    return bv_list

if __name__ == "__main__":

    pages = 15#一次爬20个视频 所以一共爬15页
    bv_list = []
    danmu_list = []

    bv_list = get_bv(pages)

    for bv in bv_list:#输入bv号 获取弹幕数据
        vid = bv
        info = get_info(vid)
        danmu = get_danmu(info)
        danmu_list.extend(danmu)

    px_word_counts = content_sort(danmu_list)

    df = pd.DataFrame(px_word_counts)#将获取到的弹幕导入excel
    writer = pd.ExcelWriter('总弹幕.xlsx')
    df.to_excel(writer, sheet_name='b站弹幕')
    writer._save()

    get_cloud(danmu_list)#输出词云





