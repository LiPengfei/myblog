#!/usr/env/python
#encoding=utf-8

import os
import tornado
import tornado.web
import tornado.options
import tornado.ioloop
import tornado.httpserver

from tornado.options import options, define

define("port", default = 80, help = "run on the given port", type=int)

define("db_host", default = 80, help = "run on the given port", type=int)

# one way.  start with param
# define("db_name", default = 80, help = "run on the given port", type=int)
# define("db_password", default = 80, help = "run on the given port", type=int)
# define("db_user", default = 80, help = "run on the given port", type=int)

# another way. read from file. as bellow comment

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/latest", LatestHandler),
        ]
        settings = dict(
            blog_title = u"Hello World!",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            debug = True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        # tornado.db = mongodb TODO
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

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        pass

class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html")

class LatestHandler(BaseHandler):
    def get(self):
        self.render("latest.html", articles = self.application.latests)

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("blogdemo_user")
        self.redirect(self.get_argument("next", "/"))

if __name__ == "__main__" :
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port);
    tornado.ioloop.IOLoop.instance().start()
