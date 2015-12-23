<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">

@yield('css_file)', "<link rel='stylesheet' href='{{ asset('app/css/style.css') }}' type = 'text/css'>")
@yield('exten_css_js', '')
        <script src= "{{ asset('app/js/funny.js') }}" type="text/javascript" charset="utf-8"></script>

		<title>
@yield('page_title', 'Woodenhouse Blog')
		</title>

    </head>
    <body id = "index">
        <header id="page_header">
            <div id = "logo">
                <h1>Woodman's House! </h1>
@yeild('signin', '天街小雨润如酥，草色遥看近却无')
                <nav>
                    <ul>
                        <li><a href="/">最近发表</a></li>
                        <li><a href="/me">个人简历</a></li>
                        <!-- {% if current_user %} -->
@if (!empty(current_user))
                        <li><a href="/update">New Post</a></li>
                        <!-- <li><a href="/auth/logout?next={{ url_escape(request.uri) }}">Sign Out</a></li> TODO-->
						<li><a href="/auth/logout?next={{'/'}}">Sign Out</a></li> 
                        <!-- {% end %} -->
@endif
                    </ul>
                </nav>
            </div>
        </header>
@yeild('sidebar', "{{'TODO'}}")

@yield('content')
        <footer id = "body_footer">
            <p>联系方式：lipengfei519@hotmail.com</p>
        </footer>
    </body>
</html>
