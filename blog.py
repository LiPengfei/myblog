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
            (r"/article", ArticleHandler),
            (r"/update_article", UpdateHandler),
            (r"/login", LoginHandler),
            (r"/do_login", DoLoginHandler),
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
        tornado.db = pymongo.MongoClient()

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

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        pass

class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html", articles = self.application.latests)

class ArticleHandler(BaseHandler):
    def get(self):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        self.render("article.html", article = self.application.article, signin = signin)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

class DoLoginHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        user_name = self.get_argument("user_name")
        user_password = self.get_argument("user_password")
        self.db.find_one({})

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
