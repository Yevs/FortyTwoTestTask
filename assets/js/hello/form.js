var domain = document.location.origin;
var animation, animation_slide;
var button;
var submitted = true;

function startAnimation() {
    button.removeClass('btn-primary');
    animation_slide = 0;
    animation = setInterval(function() {
        var new_text = 'Submitting' + Array(animation_slide+1).join('.');
        animation_slide += 1;
        animation_slide %= 3;
        button.html(new_text);
    }, 600);
}

function stopAnimation() {
    button.addClass('btn-primary');
    clearInterval(animation);
    button.html('Submit');
    button.addClass('btn-primary');
}

function parseErrors(errors) {
    var prefix = '#help_';
    for (var field in errors) {
        var msg = errors[field][0];
        $(prefix + field).parent().addClass('has-error')
        $(prefix + field).html(msg);
    }
}

function clearErrors() {
    $('span.help-block').html('');
    $('span.help-block').removeClass('has-error');
}

$(document).ready(function() {
    button = $('#submit');
    var form = $('#edit-form');
    $('#submit').click(function() {
        if (submitted) {
            submitted = false;
            clearErrors();
            var jsoned_form = {}
            form.serializeArray().forEach(function(field) {
                jsoned_form[field['name']] = field['value']
            });
            var url = domain + '/api/edit/';
            startAnimation();
            $.post(url, jsoned_form, function(data) {
                response = JSON.parse(data);
                if (response['status'] == 'error') {
                    parseErrors(response['errors']);
                }
                stopAnimation();
                submitted = true;
            }).fail(function(data) {
                console.log(data);
                stopAnimation();
                submitted = true;
            });
        }
    });
});