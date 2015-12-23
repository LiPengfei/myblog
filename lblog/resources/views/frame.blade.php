<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        @section('css_file')
        <link rel='stylesheet' href='{{ asset('app/css/style.css') }}' type = 'text/css'>
        @show

        @yield('exten_css_js')

        <script src= "{{ asset('app/js/funny.js') }}" type="text/javascript" charset="utf-8"></script>

		<title> @section('page_title') Woodenhouse Blog @show </title>

    </head>
    <body id = "index">
        <header id="page_header">
            <div id = "logo">
                <h1>Woodman's House! </h1>
@section('signin')天街小雨润如酥，草色遥看近却无 @show
                <nav>
                    <ul>
                        <li><a href="/">最近发表</a></li>
                        <li><a href="/me">个人简历</a></li>
@if (!empty($current_user))
                        <li><a href="/update">New Post</a></li>
						<li><a href="/auth/logout?next={{'/'}}">Sign Out</a></li> 
@endif
                    </ul>
                </nav>
            </div>
        </header>
@section('sidebar') TODO @show

@yield('content')
        <footer id = "body_footer">
            <p>联系方式：lipengfei519@hotmail.com</p>
        </footer>
    </body>
</html>
