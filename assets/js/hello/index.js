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
        initFileUploading();
        });
    }); 
});