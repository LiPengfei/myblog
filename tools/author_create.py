#!/usr/env/python
#encoding=utf-8

import argparse
import urllib
import bcrypt
import pymongo

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument("author_name", type=str, help = "the author's name")
    parser.add_argument("author_email", type=str, help = "the author's email")
    parser.add_argument("author_password", type=str, help = "the author's password")

    args = parser.parse_args()

    db = pymongo.MongoClient()["blog"]

    if db["author"].find_one({"name" : args.author_name}) :
        print ("author %s alreay exist", args.author_name)
    else :
        password = bcrypt.hashpw(args.author_password.encode('utf-8'), bcrypt.gensalt())
        db["author"].insert_one(
            {"name" : args.author_name,
             "email" : args.author_email,
             "password" : password
            }
        )
        print ("create author %s success" % (args.author_name))
