import pymongo

con = MongoClient(host = "localhost", port = 27017, connect = True)
db  = con.blog

# A一级分类 {name, sub[], article[]}
# B二级分类 {name, article[]}
# C日期     {month,  year, article[]]}
# D文章     {title, content, aside, author, posted_date, updated_date, comments[], next, previous, href, tag []}
# E用户     {name, email, password}
# F评论人   {name, email}
# G评论     {content, post_time, author}

# A 到 B 是一对多的关系， A 单向关联 B。 B 的删除会影响到 A。
# A 到 D 是一对多的关系， A 单向关联 D。 D 的删除会影响到 A。  D 选择类型的时候也会影响到A。 但是 D不保存类型信息。那为什么D不保存类型信息呢？那么先让A不可以改变类型吧
# B 到 D 是一对多的关系， B 单向关联 D。 D 的删除会影响到B。
# C 到 D 是一对多的关系， C 单向关联 D。 D 删除和修改会影响C。
# E 不可变更 用作管理员内容
# D 到 G 是一对多的关系， D 单向关联 G。 D 删除则G 删除。 G 删除则D 删除


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

def add_article(title, content, aside, author, next_article, pre_article, href, tag, cat, subcat):
#   posted_date,  -- auto
#   updated_date, -- none
#   comments[],   -- none
    pass

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
