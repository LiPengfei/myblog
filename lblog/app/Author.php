<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Article;

class Author extends Model
{
     /* the database table used by the model, default is lower(classname)s (authors) */
    protected $table = 'authors';

     /* the attribute can't be assign */
    protected $guarded = ['id'];

    /* the arrtibute excluded from the model's json form */
    protected $hidden = ['password'];

    public function articles() {
        return $this->hasMany(Article::class, 'ownerId');
    }
}
