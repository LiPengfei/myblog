#!/bin/bash

php artisan make:migration create_categories_table --create=categories
php artisan make:migration create_subcategories_table --create=subcategories
php artisan make:migration create_archives_table --create=archives
php artisan make:migration create_articles_table --create=articles
php artisan make:migration create_authors_table --create=authors
php artisan make:migration create_users_table --create=users
php artisan make:migration create_comments_table --create=comments

# php artisan migrate

php artisan make:model Category
php artisan make:model Subcategory
php artisan make:model Archive
php artisan make:model Article
php artisan make:model Author
php artisan make:model User
php artisan make:model Comment
