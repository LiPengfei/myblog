#!/usr/env/python
#encoding=utf-8

import pymongo
import uuid
import datetime
import bson

con = pymongo.MongoClient(host = "localhost", port = 27017, connect = True)
db  = con.blog
collec_cat = db["category"]
collec_subcat = db["sub_category"]
collec_archive = db["archive"]
collec_article = db["article"]
collec_root = db["root"]
collec_user = db["user"]
collec_comment = db["comment"]

def add_article(**article):
    now = datetime.datetime.now()
    objson = {
        "posted_date" : now,
        "comments" : [],
    }

    objson["tilte"] = article.get("title", "无题")
    objson["content"] = article.get("content", "无内容")
    objson["author"] = article.get("author", "李鹏飞")
    objson["href"] = article.get("href", "rand" + str(uuid.uuid1()))
    objson["tag"]  = article.get("tag", [])
    objson["aside"] = article.get("asise", "")
    this_article = collec_article.insert_one(objson)

    if article.has_key("previous_id") :
        add_article_to_list(this_article.inserted_id, article["previous_id"])

    if article.has_key("cat_name") :
        if article.has_key("subcat_name") :
            add_article_to_subcat(this_article.inserted_id, article["cat_name"], article["subcat_name"])
        else :
            add_article_to_cat(this_article.inserted_id, article["cat_name"])
    else :
        add_article_to_cat(this_article.inserted_id, "随笔")

    collec_archive.update_one(
        {"year" : now.year, "month": now.month},
        {"$push" : {"article" : this_article.inserted_id}},
        upsert = True)

def add_article_to_cat(article_id, catname) :
    result = collec_cat.update_one(
        { "name" : catname },
        {"$push": {"article" : article_id }},
        upsert = True)

    return True

def add_article_to_subcat(article_id, catname, subcatname) :
    result = collec_cat.find_one_and_update(
        {"name" : catname},
        {"$inc" : {"sub." + subcatname : 1}},
        upsert = True)

    result = collec_subcat.update_one(
        { "name" : subcatname},
        { "$push": {"article" : article_id}},
        upsert = True)

    return True

def add_article_to_list(article_id, previous_id) :
    pre_before = collec_article.find_one_and_update(
        {"_id" : previous_id},
        {"$set" : {"next" : article_id}},
        upsert = True)

    if pre_before.has_key("next") :
        pre_next = collec_article.find_one_and_update(
            {"_id" : pre_before["next"]},
            {"$set" : {"previous" : article_id}},
            upsert = True)
        collec_article.find_one_and_update(
            {"_id" : article_id},
            {"$set" : {"next" : pre_next["_id"], "previous" : pre_before["_id"]}},
            upsert = True)

def delete_article(article_id) :
    article = collec_article.find_one({"_id" : article_id})

    # 在JavaScript 中 ObjectId("aaaaaa..") == ObjectId("aaaaaa..") 始终为 false
    # 解决方法把objectid转成字符串比较
    js_str = "function() {function func(item, array) { for (var it in array) { if (item == array[it]) return true; } return false;}; return func('%s', %s)};" % (str(article_id), "this['article']")
    res = collec_archive.find().where(js_str)
    for doc in res :
        collec_archive.delete_one({"_id" : doc["_id"]})

    res = collec_subcat.find().where(js_str)
    for doc in res :
        collec_subcat.delete_one({"_id" : doc["_id"]})

    res = collec_cat.find().where(js_str)
    for doc in res :
        collec_cat.delete_one({"_id" : doc["_id"]})

    if article.has_key("previous") :
        if article.has_key("next") : # previous next
            res = collec_article.find_one_and_update({"_id" : article["previous"]}, {"$set" : {"next" : article["next"]}})
            res = collec_article.find_one_and_update({"_id" : article["next"]}, {"$set" : {"previous" : article["previous"]}})
        else : #previous no next
            res = collec_article.find_one_and_update({"_id" : article["previous"]}, {"$unset" : {"next" : 1}})
    else :
        if article.has_key("next") : # no previos next
            res = collec_article.find_one_and_update({"_id" : article["next"]}, {"$unset" : {"previous" : 1}})
        # no previous no next do nothing

    collec_article.delete_one({"_id" : article_id})
    # 留言不删除

def update_article(**updated_article):
    now = datetime.datetime.now()
    updated_article = {
        "updated_date" : now,
    }

    article = collec_article.find_one_and_update({"_id" : updated_article["_id"]}, updated_article)
    # 暂不提供改变顺序，因为是双向链表，太麻烦

delete_article(bson.objectid.ObjectId("552b8fac13fe2165f9578a6e"))
# if __name__ == "__main__" :
    # article = dict(
    #     title = "How Many Shoule We Put You Down For ?",
    #     content = """<p>Sit asperiores illo doloremque ducimus iure. Obcaecati corporis saepe itaque et vitae iste impedit aspernatur. Veniam dicta voluptatum ipsa doloremque unde quibusdam? Neque perspiciatis beatae magnam ipsam doloremque dolor repellendus.</p>
    #     <p>Dolor labore dolorem possimus saepe aperiam ducimus? At corporis iste minima voluptates ducimus. Deserunt consequuntur officiis veritatis eius aut dolorem! Error atque voluptatibus fuga sit praesentium. Esse modi porro eos?</p>""",
    #     author =  "李鹏飞",
    #     href = "/TODO",
    #     tag = ["c/c++", "python"],
    #     aside = '<p>&quot;Never give someone a chance to say no when selling your product.&quot; </p>',
    #     cat_name = "测试",
    # )
    # add_article(**article)

    # article = dict(
    #     title = "How Many Shoule We Put You Down For 2 ?",
    #     content = """<p>Sit asperiores illo doloremque ducimus iure. Obcaecati corporis saepe itaque et vitae iste impedit aspernatur. Veniam dicta voluptatum ipsa doloremque unde quibusdam? Neque perspiciatis beatae magnam ipsam doloremque dolor repellendus.</p>
    #     <p>Dolor labore dolorem possimus saepe aperiam ducimus? At corporis iste minima voluptates ducimus. Deserunt consequuntur officiis veritatis eius aut dolorem! Error atque voluptatibus fuga sit praesentium. Esse modi porro eos?</p>""",
    #     author =  "李鹏飞",
    #     href = "/TODO",
    #     tag = ["c/c++", "python"],
    #     aside = '<p>&quot;Never give someone a chance to say no when selling your product.&quot; </p>',
    #     cat_name = "测试",
    #     subcat_name = "测试二级",
    # )
    # add_article(**article)
