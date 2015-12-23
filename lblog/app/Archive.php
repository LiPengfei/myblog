<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Article;

class Archive extends Model
{
    protected $fillable = ['month', 'year'];

    public function articles() {
        return $this->hasMany(Article::class, 'ownerId' /*, 'id'*/);
    }
}
