# encoding: utf-8
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
import json
from PageInfo import PageInfo
from bs4 import BeautifulSoup

class PageClassify:
    def __init__(self, url, dict_info, soup):
        """prepared:输入为预先解析的页面信息，如页面类型，title，格式： url \t pageinfo(json)
           crawl_pack:需要抓取页面，返回和prepared相同格式 
        """
        self.url = url
        self.soup = soup
        self.page_flag, self.page_info = self.get_pageinfo(url, dict_info)


    def get_pageinfo(self, url, dict_info):
        # json_info : url, page_type, title, realtitle, content, cont_html, kv_dict, article
        page_info = self.trans_code(url, dict_info)
        return 1, page_info


    def trans_code(self, url, json_info):
        page_info = {
            'url'       : url,
            'page_type' : [],
            'title'     : json_info['title'].encode('utf8'),
            'realtitle' : json_info['realtitle'].encode('utf8'),
            'content'   : json_info['content'].encode('utf8'),
            'cont_html' : json_info['cont_html'].encode('utf8'),
            'kv_dict'   : {},
            # 'title_ner'   : json_info['title_ner'],
            # 'article'   : json_info['article'].encode('utf8')
        }

        #
        if "title_ner" in json_info:
            page_info["title_ner"] = json_info['title_ner']
        else:
            page_info["title_ner"] = []


        for item in json_info['page_type']:
            page_info['page_type'].append(item.encode('utf8'))
        for item in json_info['kv_dict']:
            key = item.encode('utf8')
            value = []
            for v_item in json_info['kv_dict'][item]:
                value.append(v_item.encode('utf8'))
            page_info['kv_dict'][key] = value
        return page_info
    
    def classify_evaluating(self):
        """评测"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0

        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''
        
        page_info['domain'] = '评测'
        page_info['s'] = self.get_evaluating_s()

        if '文章内容页' not in page_info['page_type'] and '商品详情页' not in page_info['page_type']:
            return 0, ''

        if page_info['realtitle'].find('测评') != -1 or page_info['realtitle'].find('评测') != -1:
            page_info['confidence'] = 1
            return 1, page_info

        valid_count = 0
        key_words = ['评测', '测评', '参数', '做工', '设计', '性价比', '优点', '缺点']
        for item in key_words:
            if page_info['content'].find(item) != -1:
                valid_count += 1
        if valid_count >= 4:
            confidence = valid_count * 0.15
            if confidence > 1:
                confidence = 1
            page_info['confidence'] = confidence
            return 1, page_info
        else:
            return 0, ''

    # 测评
    def get_evaluating_s(self):
        ner_list = self.page_info["title_ner"]
        title = unicode(self.page_info['realtitle'], errors="ignore")

        if ner_list == []:
            return title

        key_word_list = [u"测评", u"评测", u"上手评测", u"上手测评"]
        before_idx_list = [title.find(key_word) + len(key_word) for key_word in key_word_list if key_word in title]
        if before_idx_list == []:
            before_idx = len(title)
        else:
            before_idx = min(before_idx_list)

        entity_name = None
        for ner in ner_list:
            offset = ner["offset"]
            etype = ner["etype"]

            if offset < before_idx:
                entity_name = ner["name"]

        if entity_name:
            return entity_name

        # 如果title中关键字 "测评", "评测", 且不能识别其中的实体的时候, 使用策略去识别
        key_word_idx = -1
        for key_word in key_word_list:
            if title.find(key_word) != -1:
                key_word_idx = title.find(key_word)

        if key_word_idx != -1:
            # 从关键字往前扫描, 遇到标点空格停止
            i = key_word_idx - 1
            while i >= 0:
                if title[i] in u" ，。！；？":
                    break
                i -= 1
            title = title[i + 1: key_word_idx]

        return title


    def classify_introduction(self):
        """简介"""

        # 如果是百科页面, 直接return 1
        baike_res, page_info_ = self.classify_baike()
        if baike_res == 1:
            page_info_['domain'] = '简介'
            return 1, page_info_

        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '简介'
        page_info['s'] = self.get_introduction_s()
        title_count = 0
        cont_count  = 0
        confidence = 0

        title = None
        if self.soup != None and self.soup.title != None:
            title = self.soup.title.string

        title_words = ['简介', '介绍', "about"]
        for item in title_words:
            if page_info['realtitle'].lower().find(item) != -1:
                title_count += 1
            if title != None and item in title.lower():
                title_count += 1

        if title_count > 0:
            confidence = 0.6

        cont_words = ['简介', '介绍', '剧情']
        for item in cont_words:
            if page_info['content'].find(item) != -1:
                cont_count += 1

        valid_count = cont_count*1
        if valid_count >= 2:
            confidence += valid_count * 0.1
            if confidence > 1:
                confidence = 1

        if confidence > 0.5:
            page_info['confidence'] = confidence
            return 1, page_info
        else:
            return 0, ''

    # 简介
    def get_introduction_s(self):
        ner_list = self.page_info["title_ner"]
        title = unicode(self.page_info['realtitle'], errors="ignore")

        S = None

        key_word_list = [u"简介", u"介绍", u"故事简介", u"介绍大全"]

        if ner_list != []:
            before_idx_list = [title.find(key_word) + len(key_word) for key_word in key_word_list if key_word in title]
            if before_idx_list == []:
                before_idx = len(title)
            else:
                before_idx = min(before_idx_list)

            entity_name = None
            for ner in ner_list:
                offset = ner["offset"]
                etype = ner["etype"]

                if offset < before_idx:
                    entity_name = ner["name"]

            if entity_name:
                S = entity_name

        if S is None:

            # 如果title中存在关键字, 且不能识别其中的实体的时候, 使用策略去识别
            key_word_idx = -1
            for key_word in key_word_list:
                if title.find(key_word) != -1:
                    key_word_idx = title.find(key_word)

            if key_word_idx != -1:
                # 从关键字往前扫描, 遇到标点空格停止
                i = key_word_idx - 1
                while i >= 0:
                    if title[i] in " ，。！；？":
                        break
                    i -= 1
                title = title[i + 1: key_word_idx]

            S = title

        if S.endswith("）"):
            if "（" in S:
                S = S[:S.rfind("（")]
        if S.endswith(")"):
            if "(" in S:
                S = S[:S.rfind("(")]

        # 如果有 【南妹皇后】, 《斗破苍穹》 取中间的
        if "《" in S and "》" in S:
            start = S.find("《")
            end = S.find("》")
            if start < end:
                S = S[start + 1: end]

        if "【" in S and "】" in S:
            start = S.find("【")
            end = S.find("】")
            if start < end:
                S = S[start + 1: end]


        if S.strip() == u"":
            return "~"
        return S


    def classify_news(self):
        """新闻"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '新闻'
        if '新闻内容页' in page_info['page_type']:
            page_info['confidence'] = 1
            return 1, page_info
        else:
            return 0, ''

    def classify_personalprofile(self):
        """个人资料"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '个人资料'
        page_info['s'] = self.get_personalprofile_s()
        confidence  = 0
        kv_count    = 0
        cont_count  = 0

        # 使用beautiful soup 获取 title tag 内容
        title = None
        if self.soup != None and self.soup.title != None:
            title = self.soup.title.string

        if title != None and ('个人资料' in title or '明星资料' in title):
            confidence = 0.6

        if '个人资料' in page_info['realtitle'] or '明星资料' in page_info['realtitle']:
            confidence = 0.6

        kv_words = ['姓名', '生日', '出生日期', '出生地', '民族', '身高', '体重', '爱好', '职业']
        for item in kv_words:
            if item in page_info['kv_dict']:
                kv_count += 1

        cont_words = ['个人经历', '个人简介', '个人资料', '主要作品', '基本信息', '人物评价']
        for item in cont_words:
            if page_info['content'].find(item) != -1:
                cont_count += 1

        valid_count = kv_count*1 + cont_count*2
        if valid_count >= 4:
            confidence += 0.15 * valid_count
            if confidence > 1:
                confidence = 1

        if confidence > 0.5:
            page_info['confidence'] = confidence
            return 1, page_info
        else:
            return 0, ''


    def get_personalprofile_s(self):
        ner_list = self.page_info["title_ner"]
        title = unicode(self.page_info['realtitle'], errors="ignore")

        if ner_list == []:
            return title

        key_word = u"个人资料"
        # 离关键字最近的那个实体, 人物
        renwu_etype_list = [
            "1000", "1001",
            "1002", "1003",
            "1004", "1005",
            "1006", "1007",
            "1008", "1009",
            "1010", "1011",
            "1012"
        ]

        if key_word in title:
            before_idx = title.find(key_word) + len(key_word)
        else:
            before_idx = len(title)

        entity_name = None
        for ner in ner_list:
            offset = ner["offset"]
            etype = ner["etype"]

            if offset < before_idx and etype in renwu_etype_list:
                entity_name = ner["name"]

        if entity_name:
            return entity_name

        return title

    def classify_baike(self):
        """百科"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '百科'
        self.get_baike_s(page_info) # s
        page_info['confidence'] = 1

        if page_info['url'][:7] == 'http://':
            url = page_info['url'][7:]
        else:
            url = page_info['url']

        main_site = url.split('/')[0]
        if main_site == 'baike.sogou.com':
            if url[16] == 'v':
                return 1, page_info
            else:
                return 0, ''
        else:
            valid_set = {
                'baike.baidu.com/item',
                'baike.baidu.com/view',
                'baike.baidu.com/subview',
                'baike.baidu.com/album',
                'wapbaike.baidu.com/item',
                'wapbaike.baidu.com/view',
                'wapbaike.baidu.com/subview',
                'm.baike.so.com/doc',
                'baike.so.com/doc',
                'www.baike.com/wiki',

            }
            url_subdomain = '/'.join(url.split('/')[:2])
            if url_subdomain in valid_set:
                return 1, page_info
            else:
                return 0, ''


    def get_baike_s(self, page_info):
        # 使用title作为s
        title = page_info['realtitle']
        s = title
        page_info['s'] = s




    def classify_weibo(self):
        """微博"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '微博'
        self.get_weibo_s(page_info)
        page_info['confidence'] = 1
        if page_info['url'][:8] == 'https://':
            url = page_info['url'][8:]
        elif page_info['url'][:7] == 'http://':
            url = page_info['url'][7:]
        else:
            url = page_info['url']

        main_site = url.split('/')[0]
        if main_site == 'weibo.com':
            if url[9:12] == '/u/':
                return 1, page_info
            domains = url.strip("/").split('/')
            if len(domains) == 2:
                return 1, page_info
            else:
                return 0, ''
        elif main_site == 'www.weibo.com':
            if url[13:16] == '/u/':
                return 1, page_info
            elif url[13:16] == '/p/':
                tag = url.split('?')[0].split('/')[-1]
                if tag == 'home':
                    return 1, page_info
                else:
                    return 0, ''
            domains = url.strip("/").split('/')
            if len(domains) == 2:
                return 1, page_info
            else:
                return 0, ''
        elif main_site == 'tw.weibo.com':
            if url[12:15] == '/u/':
                return 1, page_info
            elif url[12:15] == '/p/':
                tag = url.split('?')[0].split('/')[-1]
                if tag == 'home':
                    return 1, page_info
                else:
                    return 0, ''
            domains = url.strip("/").split('/')
            if len(domains) == 2:
                return 1, page_info
            else:
                return 0, ''

        elif main_site == 'e.weibo.com':
            if url[11:14] == '/u/':
                return 1, page_info
            elif url[11:14] == '/p/':
                tag = url.split('?')[0].split('/')[-1]
                if tag == 'home':
                    return 1, page_info
                else:
                    return 0, ''
            domains = url.strip("/").split('/')
            if len(domains) == 2:
                return 1, page_info
            else:
                return 0, ''
        elif main_site == 't.qq.com':
            if url[8:13] == '/p/t/':
                return 0, ''
            domains = url.strip("/").split('/')
            if len(domains) == 2:
                return 1, page_info
            else:
                return 0, ''
        else:
            return 0, ''

    def get_weibo_s(self, page_info):
        # 使用title作为s
        title = page_info['realtitle']
        s = title
        page_info['s'] = s

    def classify_commidity(self):
        """商品"""
        page_flag, page_info = self.page_flag, self.page_info
        page_info['domain'], page_info['s'], page_info['confidence'] = "", "~", 0
        if page_flag == -1:
            return -1, ''
        elif page_flag == -2:
            return -2, ''

        page_info['domain'] = '商品'
        self.get_commidity_s(page_info)
        page_info['confidence'] = 1
        if '商品详情页' in page_info['page_type']:
            return 1, page_info
        else:
            return 0, ''


    def get_commidity_s(self, page_info):
        # 使用title作为s
        title = page_info['realtitle']
        s = unicode(title.strip(), errors="ignore")

        # 1. 如果是(), 【 】开头的, 去掉
        if s.startswith(u"("):
            if u")" in s:
                s = s[s.find(u")")+1:]
        if s.startswith(u"（"):
            if u"）" in s:
                s = s[s.find(u"）")+1:]
        if s.startswith(u"【"):
            if u"】" in s:
                s = s[s.find(u"】")+1:]

        #2. 如果结尾是(),判断里面字的个数,如果 >= 10, 去掉
        if s.endswith(u"）"):
            if u"（" in s:
                start = s.rfind(u"（")
                # 判断括号里面字的个数
                end = len(s) - 1
                num_words = end - start - 1
                if num_words >= 10:
                    s = s[:s.rfind(u"（")]

        page_info['s'] = s


    def test_precision_recall(self, test_dict):
        """准招计算"""
        func_dict = {
            'baike'  : self.classify_baike,
            'weibo'  : self.classify_weibo,
            'news'   : self.classify_news,
            'ceping' : self.classify_evaluating,
            'goods'  : self.classify_commidity,
            'personinfo' : self.classify_personalprofile,
            'abstract'   : self.classify_introduction
        }

        for domain in test_dict:
            print '# ' + domain + ' ---------'

            precision = ''
            recall    = ''

            def get_pr(pr):
                total = 0
                valid = 0

                for item in test_dict[domain][pr]:
                    url = item['url']
                    tag = item['tag']
                    func = func_dict[domain]
                    pre, page_info = func(url)
                    print pr + '\t' + url + '\t' + str(tag) + '\t' + str(pre)
                    if pre == -1 or pre == -2:
                        continue
                    total += 1
                    if pre == tag:
                        valid += 1
                if total == 0:
                    return '0%'
                return str(round((valid/total),4)*100) + '%'

            precision = get_pr('precision')
            recall    = get_pr('recall')
            print 'precision : ' + precision
            print 'recall : ' + recall

    def predict(self):
        """页面类型预测"""
        extractions = [
            self.classify_evaluating,
            self.classify_introduction,
            # self.classify_news,
            self.classify_personalprofile,
            self.classify_baike,
            self.classify_weibo,
            self.classify_commidity
        ]

        # go go go!
        for do_extraction in extractions:
            res, page_info = do_extraction()

            if res == 1:

                # print \
                #     page_info['url'], type(page_info['url']),  \
                #     page_info['s'], type(page_info['s']), \
                #     page_info['domain'], type(page_info['domain']), \
                #     page_info['url'], type(page_info['url']),\
                #     page_info['confidence'], type(page_info['confidence'])

                print u"%s\t%s\t%s\t%s\t%.4f" % (
                    page_info['url'],
                    page_info['s'],
                    page_info['domain'],
                    page_info['url'],
                    page_info['confidence']
                )



        

