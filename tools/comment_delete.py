#!/usr/bin/env python
#encoding=utf-8

import argparse
import urllib
import pymongo

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("href", type = str, help = "article href")
    parser.add_argument("floor", type = int,  help = "the floor you want to delete")
    args = parser.parse_args()

    db = pymongo.MongoClient()["blog"]

    article = db["article"].find_one({"href" : args.href})
    if article :
        if (article["comment"] and len(article["comment"]) > args.floor) :
            comment_id = article["comment"][args.floor]
            db["article"].find_one_and_update(
                {"href" : args.href},
                {"$pull" :{"comment" : comment_id}}
            )
            db["comment"].find_one_and_delete({"_id" : comment_id})
            print("article %s delete floor %d success" %(args.href, args.floor))
        else:
            print("article %s has no floor %d" %(args.href, args.floor))
    else :
        print("article with href %s not exist" %(args.href))
