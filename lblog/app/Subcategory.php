<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Category;
use App\Article;

class Subcategory extends Model
{
    protected $table = 'subcategories';

    protected $guraded =['id'];

    public function articles(){
        return $this->hasMany(Article::class, 'categoryId');
    }

    public function subcategories(){
        return $this->hasMany(Subcategory::class, 'parentId');
    }
}
