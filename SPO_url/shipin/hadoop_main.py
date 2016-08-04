#!python/bin/python
#  encoding: utf-8
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import sys


# 输入url, 判断是不是 视频
def main():
    for line in sys.stdin:
        line_list = line.strip().split("\t")
        url = line_list[0]
        dict_info = json.loads(line_list[-1])

        if is_shipin(url, dict_info):
            title = dict_info["realtitle"]
            S = title
            P = "视频"
            O = url

            print "%s\t%s\t%s\t%s\t%.4f" % (url, S, P, O, confidence)


def is_shipin(url, dict_info):

    page_type_list = dict_info["page_type"]

    if {"视频播放页"} & set(page_type_list):
        return True
    else:
        return False


if __name__ == '__main__':
    main()
