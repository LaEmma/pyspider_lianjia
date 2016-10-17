# -*- coding: utf-8 -*-
from pyspider.libs.base_handler import *
from pyspider.Database import DBSQLite
import re
import os

INIT_DATABASE = [
    'create table if not exists ershoufangonsale( \
        region varchar(50), \
        layout varchar(50), \
        area varchar(50), \
        direction varchar(50), \
        houseInfo varchar(50), \
        floor varchar(100), \
        totalPrice varchar(50))', 
    'create table if not exists ershoufangsold( \
        region varchar(50), \
        layout varchar(50), \
        area varchar(50), \
        houseInfo varchar(50), \
        dealDate varchar(100), \
        totalPrice varchar(50),\
        floor varchar(50), \
        unitPrice varchar(50))',
    'create table if not exists zufangonsale( \
        url varchar(100), \
        title varchar(100), \
        price varchar(20), \
        area varchar(50), \
        layout varchar(50), \
        floor varchar(50), \
        direction varchar(50), \
        subway varchar(50), \
        region varchar(50), \
        location varchar(50), \
        dealdate varchar(50))',
    'create table if not exists zufangsold( \
        title varchar(100), \
        address varchar(100), \
        floor varchar(100), \
        area varchar(50), \
        price varchar(50), \
        dealDate varchar(100), \
        viewUrl varchar(100), \
        pic_url varchar(100))',
]

class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v1',
    }

    def __init__(self):
        self.ldb = DBSQLite(os.path.join(os.getcwd(),'lianjia.sqlite3'))
        for s in INIT_DATABASE:
            self.ldb.ExecNoQuery(s, ())
        self.ldb.commit()

        self.base_url = 'http://bj.lianjia.com/zufang/'
        self.total_items  = 0
        self.number_per_page = 30
        
    @every(minutes = 24 * 60)
    def on_start(self):
        self.crawl(self.base_url, callback = self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        #called in the beginning to get total number
        for each in response.doc('HTML>BODY>DIV.wrapper>DIV.main-box>DIV.con-box>DIV.list-head>H2>SPAN').items():
            self.total_items = 200#each.text()
        self.list_page(response)
            
    def list_page(self, response):
        for each in response.doc('a[href*="zufang"]').items():
            if re.match(self.base_url+'([0-9]|[A-Z]+)', each.attr.href, re.U):
                #self.crawl(each.attr.href, callback=self.detail_page)
                self.crawl(each.attr.href, fetch_type='js', js_script="""
                   function() {
                         setTimeout(window.scrollTo(0,document.body.scrollHeight), 1000);
                   }""", callback=self.phantomjs_parser)
        
        #next page
        m = re.search('&quot;curPage&quot;:(\d+)', str(response.doc('DIV.page-box')), re.U)
        if m:
            #print m.group(0)
            page_num = int(m.group(0)[len('&quot;curPage&quot;:'):])
        
            if self.number_per_page * page_num < 100: #100 should be replaced by total items
                page_num += 1
                #for each in response.doc('DIV.page-box').items():
                url = self.base_url + 'pg' + str(page_num) + '/'
                self.crawl(url, callback=self.list_page)
    '''
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "price": response.doc('HTML>BODY>DIV.content-wrapper>DIV.overview>DIV.content>DIV.price >SPAN.total').text(),
            "roominfo": [tuple(each.text().split(u'：')) for each in response.doc('HTML>BODY>DIV.content-wrapper>DIV.overview>DIV.content>DIV.zf-room >P').items()],
        }
    '''
    @config(priority=2)
    def phantomjs_parser(self, response):
        soldList = []
        if response.doc('DIV#resblockDeal>DIV.dealList>DIV.list>DIV.row').items():
            soldList = [{
                'viewUrl': each('DIV.house>DIV.desc>DIV.frame>A').attr.href,
                'pic_url': each('DIV.house>A IMG').attr.src,
                'title': each('DIV.house>DIV.desc>DIV.frame>A').text(),
                'address': each('DIV.house>DIV.desc>A').text(),
                'floor': each('DIV.house>DIV.desc>DIV.floor').text(),
                'area': each('DIV.area').text(),
                'transDate': each('DIV.date').text(),
                'price': each('DIV.price').text(),

            } for each in response.doc('DIV#resblockDeal>DIV.dealList>DIV.list>DIV').items()]
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "price": response.doc('HTML>BODY>DIV.content-wrapper>DIV.overview>DIV.content>DIV.price >SPAN.total').text(),
            "roominfo": [tuple(each.text().split(u'：')) for each in response.doc('HTML>BODY>DIV.content-wrapper>DIV.overview>DIV.content>DIV.zf-room >P').items()],
            "soldList": soldList,
        }

    def on_result(self, result):
        if not result:
            return
        #write to zufangonsale
        res = []
        sql = "insert into zufangonsale values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        res = [result['url'], result['title'], result['price']]
        for subitem in result['roominfo']:
                #print 'subitem'+subitem
            if isinstance(subitem[1], basestring): 
                res.append(subitem[1]) 
        self.ldb.ExecQuery(sql, tuple(res))
        #write to zufangonsold
        # print result['soldList']
        res = []
        sql = "insert into zufangsold values(?, ?, ?, ?, ?, ?, ?, ?)"
        for subitem in result['soldList']:
            # print subitem
            res = [subitem['title'], subitem['address'], subitem['floor'], subitem['area'], subitem['price'], subitem['transDate'], subitem['viewUrl'], subitem['pic_url']]
            self.ldb.ExecQuery(sql, tuple(res))
