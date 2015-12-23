<?php

namespace App;
use App\Archive;
use App\Subcategory;
use App\Category;
use App\Author;
use App\Comments;

use Illuminate\Database\Eloquent\Model;

class Article extends Model
{
    protected $guarded = ['id'];

    /*
     * 如果外键是 xxx_id, 就可以不用传第二个参数，可惜我不是这么设计数据库的
     * 下次需要注意，用 xxx_id 最小化编码
     */
    public function author() {
        return $this->belongsTo(Author::class, 'ownerId' /*, 'id'*/);
    }

    public function archive() {
        return $this->belongsTo(Archive::class, 'archiveId' /*, 'id'*/);
    }

    public function category() {
        return $this->belongsTo(Category::class, 'categoryId' /*, 'id'*/);
    }

    public function subcategory() {
        return $this->belongsTo(Subcategory::class, 'subcategoryId' /*, 'id'*/);
    }

    public function comments() {
        return $this->hasMany(Comments::class, 'articleId');
    }
}
