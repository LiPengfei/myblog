<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Comment;

class User extends Model
{
    protected $guarded = ['id'];

    public function comments(){
        return $this->hasMany(Comment::class, 'ownerId');
    }
}
