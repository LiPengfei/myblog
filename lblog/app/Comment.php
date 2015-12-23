<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\User;
use App\Article;

class Comment extends Model
{
    protected $guarded = ['id'];

    public function user() {
        return $this->belongsTo(User::class, 'ownerId');
    }

    public function article() {
        return $this->belongsTo(Article::class, 'articleId');
    }
}
