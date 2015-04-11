import pymongo

con = MongoClient(host = "localhost", port = 27017, connect = True)
db  = con.blog

# A一级分类 {name, sub[], article[]}
# B二级分类 {name, article[]}
# C日期  {month,  year, article[]]}
# D文章  {title, content, aside, author, posted_date, updated_date, comments[], next, previous, href, tag []}

# A 到 B 是一对多的关系， A 单向关联 B。 B 的删除会影响到 A。
# A 到 D 是一对多的关系， A 单向关联 D。 D 的删除会影响到 A。  D 选择类型的时候也会影响到A。 但是 D不保存类型信息。那为什么D不保存类型信息呢？那么先让A不可以改变类型吧
# B 到 D 是一对多的关系， B 单向关联 D。 D 的删除会影响到B
# C 到 D 是一对多的关系， C 单向关联 D。 D 删除和修改会影响C。

# find
# A -> B, A -> D, B -> D
# C -> D,
# D -> D,
# D can't not -> A, B

# d update
# if D is update C need change
# if D type changed, A, B, need change
# if D's updated_date changed, C changed

# d delete
# a, b, c, d changed. a, b, c deleted. d's previous's next point to d's next. d's next's previous point to d's previous
