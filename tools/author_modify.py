#!/usr/bin/env python
#encoding=utf-8

import argparse
import urllib
import pymongo
import bcrypt

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(usage = "%(prog)s is used to modify an author(name, email, password) or delete an author\n%(prog)s [-d | -mn] [-d | -me] [-d | -mp] author_name")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--delete", action = "store_true")

    parser.add_argument("-mn", "--modify_name", type = str, help = "name changed to ")
    parser.add_argument("-me", "--modify_email", type = str,  help = "email changed to ")
    parser.add_argument("-mp", "--modify_password", type = str,  help = "password changed to ")

    parser.add_argument("author_name", type=str, help = "the author's you want to change")

    args = parser.parse_args()

    db = pymongo.MongoClient()["blog"]

    if args.delete :
        if db["author"].find_one_and_delete({"name" : args.author_name}) :
            print ("delete author %s success" % (args.author_name))
        else :
            print ("author %s not exist" % (args.author_name))

    else :
        author = db["author"].find_one({"name" : args.author_name})
        flag = False
        if args.modify_name :
            flag = True
            author["name"] = args.modify_name
        if args.modify_email :
            flag = True
            author["email"] = args.modify_email
        if args.modify_password :
            flag = True
            author["password"] = bcrypt.hashpw(args.modify_password.encode('utf-8'), bcrypt.gensalt())

        if flag :
            db["author"].find_one_and_replace({"name" : args.author_name}, author)
            print ("modify author %s success" % (args.author_name))
        else :
            print(parser.print_help())
