#!/usr/bin/env python
#encoding=utf-8

import argparse
import urllib
import sys
import pymongo

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("href", type = str,  help = "article's href")

    args = parser.parse_args()
    db = pymongo.MongoClient()["blog"]

    article = db["article"].find_one_and_delete({"href" : args.href})

    if article :
        # delete comment
        if article.has_key("comment") :
            comment_cursor = db["comment"].find({"_id" : {"$in" : article["comment"]}})
            for comment in comment_cursor:
                db["comment"].delete_one({"_id" : comment["_id"]})

        # check if delete subcategory
        subcategory = db["subcategory"].find_one_and_update(
            {"article" : article["_id"]},
            {"$pull" : {"article" : article["_id"]}},
            return_document=pymongo.collection.ReturnDocument.AFTER
        )
        if subcategory and len(subcategory["article"]) == 0:
            db["subcategory"].delete_one({"_id" : subcategory["_id"]})
            db["category"].find_one_and_update(
                {"sub" : subcategory["_id"]},
                {"$pull" : {"sub" : subcategory["_id"]}},
            )

        # check if delete category
        category = db["category"].find_one_and_update(
            {"article" : article["_id"]},
            {"$pull" : {"article" : article["_id"]}},
            return_document=pymongo.collection.ReturnDocument.AFTER
        )

        if category and len(category["article"]) == 0 :
            assert(len(category["sub"]) == 0)
            db["category"].delete_one({"_id": category["_id"]})

        # check if delete archive
        archive = db["archive"].find_one_and_update(
            {"article" : article["_id"]},
            {"$pull" : {"article" : article["_id"]}},
            return_document=pymongo.collection.ReturnDocument.AFTER
        )

        if archive and len(archive["article"]) == 0 :
            db["archive"].delete_one({"_id": archive["_id"]})

        print ("article with href %s delete success" % (args.href))
    else :
        print ("article with href %s is not exist" % (args.href))
