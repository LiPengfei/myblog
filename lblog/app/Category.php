<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Article;

class Category extends Model
{
    protected $table = 'categories';

    protected $guarded = ['id'];

    public function articles() {
        return $this->hasMany(Article::class, 'categoryId');
    }
}
