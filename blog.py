#!/usr/bin/env python
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
import concurrent.futures
import bcrypt
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from tornado.options import options, define
define("port", default = 80, help = "run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/article/(.+)", ArticleHandler),
            (r"/category/(.+)", CategoryHandler),
            (r"/subcategory/([^/.]+)/([^/.]+)", SubCategoryHandler),
            (r"/archive/(\d+)", ArchiveHandler),
            (r"/update", UpdateHandler),
            (r"/comment", CommentHandler),
            (r"/auth/login", DoLoginHandler),
            (r"/auth/logout", DoLogoutHandler),
            (r"/me", MeHandler),
            (r"/editme", EditMeHandler),
            (r".*", BaseHandler),   # for 404 error
        ]

        settings = dict(
            blog_title = "Hello World!",
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

        setting_file = file("setting.json")
        self.setting = json.load(setting_file)

        self.executor = concurrent.futures.ThreadPoolExecutor(2)

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

    def sendmail(self, subject, content):
        smtp = smtplib.SMTP()
        smtp.connect(self.setting["smtp_info"]["smtpserver"])
        smtp.starttls()
        smtp.login(self.setting["smtp_info"]["username"],
                  self.setting["smtp_info"]["password"])

        msg = MIMEMultipart()
        msg["From"] = self.setting["smtp_info"]["username"]
        msg["To"] = self.setting["smtp_info"]["target"]
        msg["Subject"] = subject
        txt = MIMEText(content)
        msg.attach(txt)

        smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        smtp.quit()

    def getsignins(self):
        return self.setting["signins"][random.randint(0, len(self.setting["signins"]) - 1)]

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def sidebar(self):
        return self.application.getside_bar_info()

    @property
    def executor(self):
        return self.application.executor

    def get_current_user(self): # for authenticated decoreactor
        return self.get_secure_cookie("blog_owner")

    def get(self):
        self.write_error(404)

    def write_error(self, status_code, **kwargs): # for unhandled exception
            if status_code == 404:
                self.render('404_500.html', title = "404啦，您访问的网页不存在。。")
            elif status_code == 500:
                self.render('404_500.html', title = "500啦，我们出了一个错误。。")
            else:
                self.write('error:' + str(status_code))

class DoLoginHandler(BaseHandler):
    def get(self):
        if self.current_user :
            self.redirect(self.get_argument("next", "/"))
            return
        self.render("login.html", tip = self.application.setting["auth_info"]["loginfo"])

    def post(self):
        author_name = self.get_argument("author_name", "")
        author_password = self.get_argument("author_password", "")

        author = self.db["author"].find_one({"name" : author_name})
        if author == None :
            self.render("login.html", tip = self.application.setting["auth_info"]["errorauth"])
        else :
            hashed_password = bcrypt.hashpw(author_password.encode("utf-8"), author["password"].encode("utf-8"))
            if hashed_password == author["password"] :
                self.set_secure_cookie("blog_owner", author_name)
                self.redirect(self.get_argument("next", "/"))
            else :
                self.render("login.html", tip = self.application.setting["auth_info"]["errorauth"])

class DoLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("blog_owner")
        self.redirect(self.get_argument("next", "/"))

class HomeHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        articles = yield self.get_data()
        self.render("home.html", articles = articles, sidebar = self.sidebar)

    @tornado.gen.coroutine
    def get_data(self):
        return self.db["article"].find().sort(
            [("updated_date", pymongo.DESCENDING),("posted_date", pymongo.DESCENDING)]).limit(20)

class CategoryHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, url_input):
        signin = self.application.getsignins()

        articles = yield self.get_data(url_input)
        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )

    @tornado.gen.coroutine
    def get_data(self, url_input):
        category = self.db["category"].find_one({"name" : url_input})

        if category.has_key("article") :
            articles = self.db["article"].find(
                {"_id" : {"$in" : category["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )
            return articles
        return None

class SubCategoryHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, fathername, name):
        signin = self.application.getsignins()

        articles = yield self.get_data(fathername, name)

        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )

    @tornado.gen.coroutine
    def get_data(self, fathername, name):
        category = self.db["category"].find_one({"name" : fathername})

        if (not category.has_key("sub")):
            return None

        subcategory = self.db["subcategory"].find_one(
            {"name":name, "_id" : {"$in" : category["sub"]}}
        )

        if subcategory.has_key("article") :
            articles = self.db["article"].find(
                {"_id" : {"$in" : subcategory["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )
            return articles
        return None

class ArchiveHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, archiveinfo):
        signin = self.application.getsignins()

        articles = yield self.get_data(archiveinfo)

        self.render (
            "home.html",
            articles = articles,
            signin = signin,
            sidebar = self.sidebar
        )

    @tornado.gen.coroutine
    def get_data(self, archiveinfo):
        year = int(archiveinfo[:4])
        month = int(archiveinfo[4:])

        archive = self.db["archive"].find_one({"year" : year, "month" : month})

        if archive.has_key("article") :
            articles = self.db["article"].find(
                {"_id" : {"$in" : archive["article"]}}).sort(
                [("updated_date", pymongo.DESCENDING),
                 ("posted_date", pymongo.DESCENDING)]
            )
            return articles
        return None

class ArticleHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, url_input):
        signin = self.application.getsignins()

        article, previous_article, next_article = yield self.executor.submit(self.get_data, url_input)

        self.render (
            "article.html",
            article = article,
            signin = signin,
            sidebar = self.sidebar,
            previous_article = previous_article,
            next_article = next_article
        )

    def get_data(self, url_input):
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
                    next_article = dict (
                        href = articles[article_index - 1]["href"],
                        title = articles[article_index - 1]["title"]
                    )
                if (article_index + 1) < article_nums :
                    previous_article = dict (
                        href = articles[article_index + 1]["href"],
                        title = articles[article_index + 1]["title"]
                    )
            article_index = article_index + 1
        return article, previous_article, next_article

class MeHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        signin = self.application.getsignins()

        article = yield self.get_data()
        if article:
            self.render("me.html", article = article, signin = signin)
        else:
            if self.current_user :
                self.render("editme.html", article = None)
            else:
                raise tornado.web.HTTPError(404)

    @tornado.gen.coroutine
    def get_data(self):
        return self.db["me"].find_one()

class EditMeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        article = self.db["me"].find_one()
        self.render("editme.html", article = article)

    @tornado.web.authenticated
    def post(self):
        article = {}
        article["title"] = self.get_argument("article_title")
        article["markdown"] = self.get_argument("article_content")
        article["content"] = markdown.markdown(article["markdown"])
        this_article = self.db["me"].find_one_and_replace({}, article, upsert = True)

        self.executor.submit(self.application.sendmail,
                             article["title"],
                             article["markdown"].encode("utf-8"))

        self.redirect("/me")

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
            "updated_date" : now,
        }

        article["href"] = "%d/%d/%d/%s" % (now.year, now.month, now.day, self.get_argument("article_newhref"))
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

        self.executor.submit(self.application.sendmail,
                             article["href"],
                             article["markdown"].encode("utf-8"))

        self.redirect("/article/%s" %(article["href"]))

    def update_article(self):
        now = datetime.datetime.now()

        this_article = self.db["article"].find_one_and_update(
            {"href" : self.get_argument("article_href")},
            {"$set" : {
                    "title" : self.get_argument("article_title"),
                    "aside" : self.get_argument("article_aside"),
                    "content" : markdown.markdown(self.get_argument("article_content")),
                    "markdown" : self.get_argument("article_content"),
                    "updated_date" : now
                }
            },
            return_document=pymongo.collection.ReturnDocument.AFTER
        )

        self.executor.submit(self.application.sendmail,
                             this_article["href"],
                             this_article["markdown"].encode("utf-8"))

        self.redirect("/article/%s" %(this_article["href"]))

    def add_article_to_cat(self, article_id, catname):
        self.db["category"].update_one(
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

        comment_name = self.get_argument("comment_verify")
        if comment_name != "8":
            self.redirect("/article/%s" % (article_href))
            return

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
        summary_letter_nums = 800
        first_less_letter = article["markdown"].find("<")
        if first_less_letter < summary_letter_nums and first_less_letter != -1 :
            summary_letter_nums = first_less_letter

        content = markdown.markdown(article["markdown"][:summary_letter_nums])
        return self.render_string("modules/art_summary.html", article = article, content=content)

class CommentModule(tornado.web.UIModule):
    def render(self, comment, floor):
        comment = self.handler.db["comment"].find_one({"_id" : comment})
        comment_author = self.handler.db["user"].find_one({"_id" : comment["author"]})
        comment["author"] = comment_author
        return self.render_string("modules/comment.html", comment = comment, floor = floor)

if __name__ == "__main__" :
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port);
    tornado.ioloop.IOLoop.instance().start()
