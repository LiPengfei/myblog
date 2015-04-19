import pymongo
import uuid
import datetime

con = MongoClient(host = "localhost", port = 27017, connect = True)
db  = con.blog

# A一级分类 category {name, sub[], article[]}
# B二级分类 sub_category {name, article[], fathername}
# C日期     archive {year, month article[]]}
# D文章     article {title, content, aside, author, posted_date, updated_date, comments[], next, previous, href, tag []}
# E用户     author {name, email, password}
# F评论人   user {name, email}
# G评论     comment {content, post_time, author}

# A 到 B 是一对多的关系， A 单向关联 B。 B 的删除会影响到 A。
# A 到 D 是一对多的关系， A 单向关联 D。 D 的删除会影响到 A。  D 选择类型的时候也会影响到A。 但是 D不保存类型信息。那为什么D不保存类型信息呢？那么先让A不可以改变类型吧
# B 到 D 是一对多的关系， B 单向关联 D。 D 的删除会影响到B。
# C 到 D 是一对多的关系， C 单向关联 D。 D 删除和修改会影响C。
# E 不可变更 用作管理员内容
# D 到 G 是一对多的关系， D 单向关联 G。 D 删除则G 删除。 G 删除则D 删除

collec_cat = db["category"]
collec_subcat = db["sub_category"]
collec_archive = db["archive"]
collec_article = db["article"]
collec_root = db["root"]
collec_user = db["user"]
collec_comment = db["comment"]

# find
# A -> B, A -> D, B -> D
# C -> D,
# D -> D,
# D can't not -> A, B
# D -> G -> F. can't reverse

# d update
# if D is update C need change
# if D type changed, A, B, need change
# if D's updated_date changed, C changed

# d delete
# a, b, c, d, g changed. a, b, c deleted.
# d's previous's next point to d's next.
# d's next's previous point to d's previous.
# g delete
# f not change because f is import people.

# d add
# A, B, C add

# g add
# f may add if not has, d.comments add

# 暂不考虑删评论

# f delete
# f is bad boy, then delete all g.

# 主要操作是d的 增删改查， G的增删， F的增删

# 我可能的行为 增加一篇文章。
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
    if article.has_key("previous"):
        objson["previous"] = article["previous"]

    result = collec_article.insert_one(objson)

    if article.has_key("cat") :
        if article.has_key("subcat") :
        else :
            add_article_to_cat(result.inserted_id, article["cat"])
    else :
        add_article_to_cat(result.inserted_id, "随笔")

def add_article_to_cat(article_id, catname) :
    result = collec_cat.update_one(
        { "name" : catname },
        {"$push": {"article" : article_id }},
        upsert = True)

    return True

def add_article_to_subcat(article_id, catname, subcatname) :
    result = collec_cat.find_one_and_update(
        {"name" : catname},
        {"$inc" : "sub." + subcatname},
        upsert = True)

    result = collec_subcat.update_one(
        { "name" : subcatname},
        { "$push": {"article" : article_id}},
        upsert = True)

    return True

def add_article_to_list(article_id, previous_id = None) :
    if previous_id != None :
        before = collec_article.find_one_and_update(
            {"_id" : previous_id},
            {"$set" : {"next" : article_id}},
            upsert = True)

        if before.has_key("next") :
            collec_article.find_one_and_update(
                {"_id" : before["next"]},
                {"$set" : {"previous" : article_id}},
                upsert = True)
            collec_article.find_one_and_update(
                {"_id" : article_id},
                {"$set" : {"next" : before["_id"]}},
                upsert = True)
            )


# 删除一篇文章
def delete_article():  # need a mongo id
#   posted_date,  -- auto
#   updated_date, -- none
#   comments[],   -- none

# 修改一篇文章
# def update_article(article_id, ...):  python syntax TODO
    # pass

def update_article_type(cat, subcat):
    pass

def update_article_title(title):
    pass

def update_article_content(conten):
    pass

def update_article_aside(aside):
    pass

def update_article_sort(next_article_id, pre_article_id):
    pass

# 发表一条评论
def add_comment(article_id, author, email, content):
    pass

# 发表一条留言 下个版本再考虑
def add_message(author, email, content):
    pass
