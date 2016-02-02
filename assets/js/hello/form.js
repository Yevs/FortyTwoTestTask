var domain = document.location.origin;  // page domain url

// vars for animating when preventing user to post form 
// when the previous form has not been resolved yet
// See: startAnimation
var animation, animation_slide;   

var button;
var submitted = true;

function startAnimation() {
    /*
    Called when user posts a form.
    Transforms submit button into button with animation:
    Submitting. -> Submitting.. -> Submitting...*/

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
    /*
    Called when user form post has been resolved.
    Stops animation of the submit button*/

    button.addClass('btn-primary');
    clearInterval(animation);
    button.html('Submit');
    button.addClass('btn-primary');
}

function parseErrors(errors) {
    /*
    Given errors as json from server response,
    lists them on the form*/

    var prefix = '#help_';
    for (var field in errors) {
        var msg = errors[field][0];
        $(prefix + field).parent().addClass('has-error')
        $(prefix + field).html(msg);
    }
}

function clearErrors() {
    /*
    Clears errors help boxes.
    Called when user resubmits a form after fail*/

    $('span.help-block').html('');
    $('span.help-block').removeClass('has-error');
}

function initFormSubmition(onSuccess) {
    /*
    Gets a form and assigns an onclick event handler
    to a submit button. Makes sure that form can be
    submitted only once before it gets processed from
    a server by grabbing submitted condition variable.
    A success callback of form submition is given
    by onSuccess argument*/

    button = $('#submit');
    var form = $('#edit-form');
    $('#submit').click(function() {
        if (submitted) {
            
            submitted = false;
            clearErrors();
            var url = domain + '/api/edit/';
            startAnimation();

            form.ajaxSubmit({

                url: url,

                type: 'POST',
                
                dataType: 'json',

                success: function(response) {
                    if (response['status'] == 'error') {
                        parseErrors(response['errors']);
                    } else if (response['status'] == 'ok') {
                        onSuccess();
                    }
                    stopAnimation();
                    submitted = true;
                },

                error: function(data) {
                    stopAnimation();
                    submitted = true;
                }
            });
        }
    });
}

function initFileUploading() {
    /*
    Creates basic event and initiallization
    for a "custom" input[type="file"] control*/

    $(document).on('change', '.btn-file :file', function() {
        var input = $(this),
            numFiles = input.get(0).files ? input.get(0).files.length : 1,
            label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [numFiles, label, input[0].files]);
    });
    
    $('.btn-file :file').on('fileselect', function(e, numFiles, label, files) {
        $('#file-name').html(label);
        if (files && files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#avatar').attr('src', e.target.result);
            }
            reader.readAsDataURL(files[0]);
        }            
    });
}

$(document).ready(function() {
    initFileUploading();
    initFormSubmition(function() {
        window.location = domain;
    });
});