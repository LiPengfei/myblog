@extents('farme')

@section('exten_css_js')
<script src= "{{ asset('app/js/jquery.js') }}" type="text/javascript" charset="utf-8"></script>
@stop

@section('page_title')
Come on! Boy!
@stop

@include('editor::head')

@section('content')
<div class="editor">
    <textarea id="myEditor" name="content"></textarea>
</div>
@stop
