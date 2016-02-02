/* A little cheat to give user ability for editing on home page
   rather than on seperate page. Also a workaround to escape extensive
   html markup in js code. Function asks rendered html from server
   by GET on '/edit/' and then swaps current page content with form's
   html in the response. 

   Also by adding custom onSuccess(see form.js) it grab rendered html
   by GET to '/' and get rendered html which then would be swapped with
   form's html.
*/

$('#edit').click(function() {
    var url = domain + '/edit/';
    $.get(url, function(data) {
        var html = $(data);
        var form = html.find('form');
        $('.jumbotron').children().remove();
        $('.jumbotron').append(form);
        initFormSubmition(function() {
            $.get(domain, function(data) {
                var html = $(data);
                $('.jumbotron').children().remove();
                var new_elems = html.find('.jumbotron').children();
                $('.jumbotron').append(new_elems)
            });
        });
        initFileUploading();
    }); 
});