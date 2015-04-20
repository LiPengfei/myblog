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
            (r"/article/(\w+)", ArticleHandler),
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
        res = self.db["category"].find()
        category = {}
        for v in res :
            category[v["_id"]] = v
        res = self.db["sub_category"].find()
        subcategory = {}
        for v in res:
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

        category = self.db["category"].find_one({"name" : fathername}) #TODO
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

class DoLoginHandler(BaseHandler):
    def get(self):
        if self.current_user :
            self.redirect(self.get_argument("next", "/"))
            return

        self.render("login.html", tip = self.application.strings["loginfo"])

    def post(self):
        user_name = self.get_argument("user_name", "")
        user_password = self.get_argument("user_password", "")
        doc = self.db["author"].find_one({"name" : user_name, "password" : user_password})
        if doc == None :
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
        article_id = self.get_argument("article_id", None)
        if article_id :
            article = self.db["article"].find_one({"_id": bson.ObjectId(article_id)})
            self.render("update_article.html", article = article, sidebar = self.sidebar)

        else:
            self.render("update_article.html", article = None, sidebar = self.sidebar)

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("new_article_href", None):
            self.new_article()
        else:
            self.update_article()

    def new_article(self):
        now = datetime.datetime.now()
        objson = {
            "updated_date" : now,
        }

        objson["title"] = self.get_argument("article_title")
        objson["aside"] = self.get_argument("article_aside")
        objson["href"] = self.get_argument("new_article_href")
        objson["markdown"] = self.get_argument("article_content")
        objson["author"] = self.current_user
        objson["content"] = markdown.markdown(objson["markdown"])
        this_article = self.db["article"].insert_one(objson)

        cat_name = self.get_argument("cat_new", None)
        subcat_name = self.get_argument("subcat_new", None)
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

        self.redirect("/article/%s" %(objson["href"]))

    def update_article(self):
        now = datetime.datetime.now()
        objson = {
            "posted_date" : now,
        }

        objson["title"] = self.get_argument("article_title")
        objson["aside"] = self.get_argument("article_aside")
        objson["href"] =  self.get_argument("article_href")
        objson["markdown"] = self.get_argument("article_content")
        objson["author"] = self.current_user
        objson["content"] = markdown.markdown(objson["markdown"])
        this_article = self.db["article"].find_one_and_replace({"href" : objson["href"]}, objson)
        self.redirect("/article/%s" %(objson["href"]))

    def add_article_to_cat(self, article_id, catname):
        result = self.db["category"].update_one(
            { "name" : catname },
            {"$push": {"article" : article_id }},
            upsert = True)

    def add_article_to_subcat(self, article_id, catname, subcatname):
        category = self.db["category"].find_one_and_update(
            {"name" : catname},
            {"$push" : {"article" : article_id} },
            upsert = True,
            return_document=pymongo.collection.ReturnDocument.AFTER
        )
        subcatory = self.db["sub_category"].find(
            {"_id" : {"$in" : category.get("sub", [])}, "name" : subcatname},
        )

        assert(subcatory.count() <= 1)

        if subcatory.count() != 0 :
            self.db["sub_category"].find_one_and_update(
                {"_id" : subcatory[0]["_id"]},
                {"$push", {"article" : article_id}}
            )
        else :
            subcatory = self.db["sub_category"].insert_one(
                {"name" : subcatname, "article" : [article_id]}
            )
            self.db["category"].find_one_and_update(
                {"name" : catname},
                {"$push" : {"sub" : subcatory.inserted_id} },
            )

class CommentHandler(BaseHandler):
    def post(self):
        article_id_string = self.get_argument("article_id", None)
        if article_id_string == None:
            raise tornado.web.HTTPError(404)

        article_id = bson.ObjectId(article_id_string)
        name = self.get_argument("name", "")
        email = self.get_argument("email", "")
        comment = self.get_argument("comment", "")

        db_user = None
        user_doc = self.db["user"].find_one(
            {"name" : name, "email" : email})
        if not db_user :
            user_doc = self.db["user"].insert_one({"name" : name, "email" : email})
            db_user = user_doc.inserted_id
        else:
            db_user = user_doc["_id"]

        now = datetime.datetime.now()
        db_comment = self.db["comment"].insert_one(
            {"content" : comment,
             "author" : db_user,
             "posted_date" : now})
        db_article = self.db["article"].find_one_and_update(
            {"_id" : article_id},
            {"$push" : {"comment" : db_comment.inserted_id}})

        self.redirect("/article/%s" % (db_article["href"]))


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
