#!/usr/env/python
#encoding=utf-8

import os
import tornado
import tornado.web
import tornado.options
import tornado.ioloop
import tornado.httpserver
import random
import pymongo
import bson

from tornado.options import options, define

define("port", default = 80, help = "run on the given port", type=int)

# one way.  start with param
# define("db_name", default = 80, help = "run on the given port", type=int)
# define("db_password", default = 80, help = "run on the given port", type=int)
# define("db_user", default = 80, help = "run on the given port", type=int)

# another way. read from file. as bellow comment

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/article/(\w+)", ArticleHandler),
            (r"/category/([^/.]+)", CategoryHandler),
            (r"/category/([^/.]+)/([^/.]+)", SubCategoryHandler),
            (r"/archive/(\d+)", ArchiveHandler),
            (r"/update_article", UpdateHandler),
            (r"/login", LoginHandler),
            (r"/auth/login", DoLoginHandler),
        ]

        settings = dict(
            blog_title = u"Hello World!",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            ui_modules = {
                "art_summary" : ArtSummaryModule,
                "comment"    : CommentModule,
            }, # 没有全部都做成ui module。因为不用ui module 功能也实现了。这里这么做只是为了尝试一下 ui module。其效率和效果如何，不知道。
            debug = True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = pymongo.MongoClient()["blog"]

        # 先做硬编码 TODO
        self.latests = [
            dict(
                title = "How Many Shoule We Put You Down For ?",
                posted_date = "October 1st, 2010 at 2:39PM",
                aside = '<p>&quot;Never give someone a chance to say no when selling your product.&quot; </p>',
                content = """<p>Sit asperiores illo doloremque ducimus iure. Obcaecati corporis saepe itaque et vitae iste impedit aspernatur. Veniam dicta voluptatum ipsa doloremque unde quibusdam? Neque perspiciatis beatae magnam ipsam doloremque dolor repellendus.</p>
                <p>Dolor labore dolorem possimus saepe aperiam ducimus? At corporis iste minima voluptates ducimus. Deserunt consequuntur officiis veritatis eius aut dolorem! Error atque voluptatibus fuga sit praesentium. Esse modi porro eos?</p>""",
                comments = 25,
                href = "/TODO",
                author  = "李鹏飞",
            ),
            dict(
                title = "How Many Shoule We Put You Down For 2?",
                posted_date = "October 1st, 2010 at 2:39PM",
                updated_date = "October 1st, 2010 at 3:39PM",
                content = """<p>Adipisicing corporis tempora atque debitis animi dolores. Placeat ut ut exercitationem asperiores consectetur. Laudantium inventore reprehenderit iusto sit sit iure itaque tenetur sed mollitia. Consequuntur non incidunt cumque blanditiis odio.</p>
                <p>Elit vero iusto quaerat blanditiis recusandae natus omnis impedit. Nobis quos mollitia inventore eveniet quo iste laboriosam at. Beatae facilis alias autem unde eveniet nam. Inventore architecto suscipit dolorum voluptate!</p>""",
                comments = 10,
                href = "/TODO",
                author  = "李鹏飞",
            ),
        ]
        self.article = dict(
                title = "How Many Shoule We Put You Down For ?",
                posted_date = "October 1st, 2010 at 2:39PM",
                content = """<p>Sit asperiores illo doloremque ducimus iure. Obcaecati corporis saepe itaque et vitae iste impedit aspernatur. Veniam dicta voluptatum ipsa doloremque unde quibusdam? Neque perspiciatis beatae magnam ipsam doloremque dolor repellendus.</p>
                <p>Dolor labore dolorem possimus saepe aperiam ducimus? At corporis iste minima voluptates ducimus. Deserunt consequuntur officiis veritatis eius aut dolorem! Error atque voluptatibus fuga sit praesentium. Esse modi porro eos?</p>""",
                author  = "李鹏飞",
                previous = dict(
                    title = "实在是不行",
                    href = "aaaa",
                ),
                next = dict(
                    title = "实在还是不行",
                    href = "aaaa",
                ),
                comments = [
                    dict(
                        author = "lipengfei",
                        posted_date = "October 1st, 2010 at 2:39PM",
                        content = "<h1>这个是很牛逼的</h1>",
                    ),
                    dict(
                        author = "lipengfei",
                        posted_date = "October 1st, 2010 at 2:39PM",
                        content = "<h>这个是很牛逼的</h>",
                    ),
                    dict(
                        author = "lipengfei",
                        posted_date = "October 1st, 2010 at 2:39PM",
                        content = "<h>这个是很牛逼的</h>",
                    ),
                ],
            )
        self.signins = [
            "天街小雨润如酥，草色遥看近却无",
            "最是一年春好处， 绝胜烟柳满皇都",
            "孤舟蓑笠翁，独钓寒江雪",
            "我住长江头，君住长江尾，日日思君不见君，共饮长江水",
            "会挽雕弓如满月，西北望，射天狼"
        ]
        self.strings = {
            "loginfo" : "请输入用户名和密码",
            "errorauth" : "用户名或者密码错误",
        }

    def getside_bar_info(self):
        res = self.db["category"].find()
        category = {}
        for v in res :
            category[v["_id"]] = v
        res = self.db["sub_category"].find()
        subcategory = {}
        for v in res :
            subcategory[v["_id"]] = v
        res = self.db["archive"].find()
        archive = {}
        for v in res :
            archive[v["_id"]] = v

        return {
            "category" : category,
            "subcategory" : subcategory,
            "archive" : archive,
        }

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    @property
    def sidebar(self):
        return self.application.getside_bar_info()

    def get_current_user(self):
        pass

class HomeHandler(BaseHandler):
    def get(self):
        articles = self.db["article"].find().sort(
            [("updated_date", pymongo.DESCENDING),("posted_date", pymongo.DESCENDING)]).limit(20)
        self.render("home.html", articles = articles, sidebar = self.sidebar)

class ArticleHandler(BaseHandler):
    def get(self, url_input):
        print(url_input)
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        # 这里为了让地址栏看着不那么渣, 没有用id做key。href实际上可以说起了主键的作用了。人为起的名字做键肯定会有问题，所以，再插入的时候要多做一些检查操作，如果重复了就伪随机一个，加上后缀，当前的总文章数做后缀
        article = self.db["article"].find_one({"href" : url_input})

        self.render (
            "article.html",
            article = article,
            signin = signin,
            sidebar = self.sidebar
        )

class CategoryHandler(BaseHandler):
    def get(self, url_input):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        category = self.db["category"].find_one({"name" : url_input})

        if category.has_key("article") :
            articles_cursor = self.db["article"].find(
                {"_id" : {"$in" : category["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )

        articles = []
        for article in articles_cursor :
            articles.append(article)

        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )

class SubCategoryHandler(BaseHandler):
    def get(self, fathername, name):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        category = self.db["category"].find_one({"name" : fathername})
        assert(category["sub"])
        subcategory = self.db["sub_category"].find_one(
            {"name":name, "_id" : {"$in" : category["sub"]}}
        )

        if subcategory.has_key("article") :
            articles_cursor = self.db["article"].find(
                {"_id" : {"$in" : subcategory["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )

        articles = []
        for article in articles_cursor :
            articles.append(article)

        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )

class ArchiveHandler(BaseHandler):
    def get(self, archiveinfo):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]

        year = int(archiveinfo[:4])
        month = int(archiveinfo[4:])

        archive = self.db["archive"].find_one({"year" : year, "month" : month})

        if archive.has_key("article") :
            articles_cursor = self.db["article"].find(
                {"_id" : {"$in" : archive["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )

        articles = []
        for article in articles_cursor :
            articles.append(article)

        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )


class LoginHandler(BaseHandler):
    def get(self):
        tip = self.get_argument("tip", "loginfo")
        self.render("login.html", tip = self.application.strings[tip])

class DoLoginHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        user_name = self.get_argument("user_name")
        user_password = self.get_argument("user_password")
        doc = self.db["author"].find_one({"name" : user_name, "password" : user_password})
        if doc == None :
            self.redirect("/login?tip=errorauth")
        else :
            self.redirect("/")

class UpdateHandler(BaseHandler):
    def get(self):
        self.render("update_article.html", article = self.application.article)

class ArtSummaryModule(tornado.web.UIModule):
    def render(self, article):
        return self.render_string("modules/art_summary.html", article = article)

class CommentModule(tornado.web.UIModule):
    def render(self, comment):
        return self.render_string("modules/comment.html", comment = comment)

if __name__ == "__main__" :
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port);
    tornado.ioloop.IOLoop.instance().start()
