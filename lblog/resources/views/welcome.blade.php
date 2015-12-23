@extends('frame')

@section('exten_css_js')
<script src= "{{ asset('app/js/jquery.js') }}" type="text/javascript" charset="utf-8"></script>
@endsection

@section('page_title')
Come on! Boy!
@endsection

{{-- @include('editor::head') --}}

@section('content')
<div class="editor">
    <textarea id="myEditor" name="content"></textarea>
</div>
@endsection
