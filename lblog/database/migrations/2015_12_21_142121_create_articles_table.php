<?php

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateArticlesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('articles', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->string('title', 64)->nullAble(false);
            $table->string('markdown', 10240)->nullAble(false);
            $table->string('content', 10240)->nullAble(false);
            $table->string('aside', 512);
            $table->bigInteger('ownerId')->unsigned();
            $table->bigInteger('categoryId')->unsigned();
            $table->bigInteger('subcategoryId')->unsigned();
            $table->bigInteger('archiveId')->unsigned();
            $table->foreign('ownerId')->references('id')->on('authors');
            $table->foreign('categoryId')->references('id')->on('categories');
            $table->foreign('subcategoryId')->references('id')->on('subcategories');
            $table->foreign('archiveId')->references('id')->on('archives');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::drop('articles');
    }
}
