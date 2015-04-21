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
import datetime
import markdown
from tornado.options import options, define
define("port", default = 80, help = "run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/article/(.+)", ArticleHandler),
            (r"/category/([^/.]+)", CategoryHandler),
            (r"/category/([^/.]+)/([^/.]+)", SubCategoryHandler),
            (r"/archive/(\d+)", ArchiveHandler),
            (r"/update", UpdateHandler),
            (r"/comment", CommentHandler),
            (r"/auth/login", DoLoginHandler),
            (r"/auth/logout", DoLogoutHandler),
        ]

        settings = dict(
            blog_title = u"Hello World!",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            xsrf_cookies = True,
            login_url = "/auth/login", # for authenticated decoreactor
            ui_modules = {
                "art_summary" : ArtSummaryModule,
                "comment"    : CommentModule,
            }, # 没有全部都做成ui module。因为不用ui module 功能也实现了。这里这么做只是为了尝试一下 ui module。其效率和效果如何，不知道。
            debug = True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = pymongo.MongoClient()["blog"]

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
        sidebar = dict(
            category = [],
            subcategory = {},
            archive = [],
        )

        sidebar["category"] = self.db["category"].find()

        subcategorys = self.db["subcategory"].find()
        for subcategory in subcategorys:
            sidebar["subcategory"][subcategory["_id"]] = subcategory

        sidebar["archive"] = self.db["archive"].find()
        return sidebar

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def sidebar(self):
        return self.application.getside_bar_info()

    def get_current_user(self): # for authenticated decoreactor
        return self.get_secure_cookie("blog_owner")

class HomeHandler(BaseHandler):
    def get(self):

        articles = self.db["article"].find().sort(
            [("updated_date", pymongo.DESCENDING),("posted_date", pymongo.DESCENDING)]).limit(20)

        self.render("home.html", articles = articles, sidebar = self.sidebar)

class ArticleHandler(BaseHandler):
    def get(self, url_input):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        articles = self.db["article"].find().sort(
            [("posted_date", pymongo.DESCENDING)])

        article = None
        previous_article = None
        next_article = None
        article_index = 0
        article_nums = articles.count()

        while article_index != article_nums :
            if articles[article_index]["href"] == url_input:
                article = articles[article_index]
                if article_index != 0 :
                    previous_article = dict (
                        href = articles[article_index - 1]["href"],
                        title = articles[article_index - 1]["title"]
                    )
                if article_index != article_nums - 1 :
                    next_article = dict (
                        href = articles[article_index + 1]["href"],
                        title = articles[article_index + 1]["title"]
                    )
            article_index = article_index + 1

        self.render (
            "article.html",
            article = article,
            signin = signin,
            sidebar = self.sidebar,
            previous_article = previous_article,
            next_article = next_article
        )

class CategoryHandler(BaseHandler):
    def get(self, url_input):
        signin = self.application.signins[random.randint(0, len(self.application.signins) - 1)]
        category = self.db["category"].find_one({"name" : url_input})

        if category.has_key("article") :
            articles = self.db["article"].find(
                {"_id" : {"$in" : category["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )

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
        subcategory = self.db["subcategory"].find_one(
            {"name":name, "_id" : {"$in" : category["sub"]}}
        )

        if subcategory.has_key("article") :
            articles = self.db["article"].find(
                {"_id" : {"$in" : subcategory["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )

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

class DoLoginHandler(BaseHandler):
    def get(self):
        if self.current_user :
            self.redirect(self.get_argument("next", "/"))
            return

        self.render("login.html", tip = self.application.strings["loginfo"])

    def post(self):
        user_name = self.get_argument("author_name", "")
        user_password = self.get_argument("author_password", "")
        author = self.db["author"].find_one({"name" : user_name, "password" : user_password})
        if author == None :
            self.render("login.html", tip = self.application.strings["errorauth"])
        else :
            self.set_secure_cookie("blog_owner", user_name)
            self.redirect(self.get_argument("next", "/"))

class DoLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("blog_owner")
        self.redirect(self.get_argument("next", "/"))

class UpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        article_href = self.get_argument("article_href", None)
        if article_href :
            article = self.db["article"].find_one({"href": article_href})
            self.render("update_article.html", article = article, sidebar = self.sidebar, is_old_article = True)
        else:
            self.render("update_article.html", article = None, sidebar = self.sidebar, is_old_article = False)

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("article_newhref", None):
            self.new_article()
        else:
            self.update_article()

    def new_article(self):
        now = datetime.datetime.now()
        article = {
            "posted_date" : now,
        }

        article["href"] = "%d/%d/%s" % (now.year, now.month, self.get_argument("article_newhref"))
        article["title"] = self.get_argument("article_title")
        article["aside"] = self.get_argument("article_aside")
        article["markdown"] = self.get_argument("article_content")
        article["author"] = self.current_user
        article["content"] = markdown.markdown(article["markdown"])

        if self.db["article"].find_one({"href" : article["href"]}) :
            self.render("update_article.html", article = article, sidebar = self.sidebar, is_old_article = False)
            return 

        this_article = self.db["article"].insert_one(article)

        cat_name = self.get_argument("article_cat", None)
        subcat_name = self.get_argument("article_subcat", None)
        if cat_name :
            if subcat_name :
                self.add_article_to_subcat(this_article.inserted_id, cat_name, subcat_name)
            else :
                self.add_article_to_cat(this_article.inserted_id, cat_name)
        else :
            self.add_article_to_cat(this_article.inserted_id, "随笔")

        self.db["archive"].update_one(
            {"year" : now.year, "month": now.month},
            {"$push" : {"article" : this_article.inserted_id}},
            upsert = True)

        self.redirect("/article/%s" %(article["href"]))

    def update_article(self):
        now = datetime.datetime.now()
        article = {
            "updated_date" : now,
        }

        article["title"] = self.get_argument("article_title")
        article["aside"] = self.get_argument("article_aside")
        article["href"] =  self.get_argument("article_href")
        article["markdown"] = self.get_argument("article_content")
        article["author"] = self.current_user
        article["content"] = markdown.markdown(article["markdown"])
        this_article = self.db["article"].find_one_and_replace({"href" : article["href"]}, article)
        self.redirect("/article/%s" %(article["href"]))

    def add_article_to_cat(self, article_id, catname):
        result = self.db["category"].update_one(
            {"name" : catname},
            {"$push": {"article" : article_id }},
            upsert = True)

    def add_article_to_subcat(self, article_id, catname, subcatname):
        category = self.db["category"].find_one_and_update(
            {"name" : catname},
            {"$push" : {"article" : article_id} },
            upsert = True,
            return_document=pymongo.collection.ReturnDocument.AFTER
        )
        subcatory = self.db["subcategory"].find(
            {"_id" : {"$in" : category.get("sub", [])}, "name" : subcatname},
        )

        assert(subcatory.count() <= 1)

        if subcatory.count() != 0 :
            self.db["subcategory"].find_one_and_update(
                {"_id" : subcatory[0]["_id"]},
                {"$push" : {"article" : article_id}}
            )
        else :
            subcatory = self.db["subcategory"].insert_one(
                {"name" : subcatname, "article" : [article_id]}
            )
            self.db["category"].find_one_and_update(
                {"name" : catname},
                {"$push" : {"sub" : subcatory.inserted_id} },
            )

class CommentHandler(BaseHandler):
    def post(self):
        article_href = self.get_argument("article_href", None)
        if article_href == None:
            raise tornado.web.HTTPError(404)

        comment_name = self.get_argument("comment_name", "")
        comment_email = self.get_argument("comment_email", "")
        comment_content = self.get_argument("comment_content", "")

        user_id = None

        user = self.db["user"].find_one(
            {"name" : comment_name, "email" : comment_email})
        if not user :
            user = self.db["user"].insert_one({"name" : comment_name, "email" : comment_email})
            user_id = user.inserted_id
        else:
            user_id = user["_id"]

        now = datetime.datetime.now()
        comment = self.db["comment"].insert_one(
            {"content" : comment_content,
             "author" : user_id,
             "posted_date" : now})

        article = self.db["article"].find_one_and_update(
            {"href" : article_href},
            {"$push" : {"comment" : comment.inserted_id}})

        self.redirect("/article/%s" % (article_href))


class ArtSummaryModule(tornado.web.UIModule):
    def render(self, article):
        return self.render_string("modules/art_summary.html", article = article)

class CommentModule(tornado.web.UIModule):
    def render(self, comment):
        comment = self.handler.db["comment"].find_one({"_id" : comment})
        comment_author = self.handler.db["user"].find_one({"_id" : comment["author"]})
        comment["author"] = comment_author
        return self.render_string("modules/comment.html", comment = comment)

if __name__ == "__main__" :
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port);
    tornado.ioloop.IOLoop.instance().start()
