#!python/bin/python
# encoding: utf-8
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
import sys, hashlib


# 输入url, 判断是不是 音频页
def main():

    for line in sys.stdin:
        line_list = line.strip().split("\t")
        url = line_list[0]
        dict_info = json.loads(line_list[-1])

        if is_shipin(url, dict_info):
            title = dict_info["realtitle"]
            S = title
            P = "音频"
            O = url

            print "%s\t%s\t%s\t%s" % (url, S, P, O)


def is_shipin(url, dict_info):

    soup = BeautifulSoup(dict_info["html"], "html.parser")

    # 基于meta的识别
    content = get_meta_content(soup)
    if "音乐" not in content and "播放器" not in content and "电台" not in content:
        return False

    # 判断页面是否有播放元素
    if len(soup.find_all("a", attrs={"title": "播放"})) > 0:
        return True

    return False


def get_meta_content(soup):
    content = ""
    for meta in soup.find_all("meta"):
        if "content" in meta.attrs:
            content += meta["content"] + "\t"
    return content.strip()






if __name__ == '__main__':
    main()