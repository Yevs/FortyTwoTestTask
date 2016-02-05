$(document).ready(function() {
    initFormSubmition(function(data) {
        /* updates fields on successfull response
        from submitting the form*/
        
        $('#person-info').show();
        $('#form-container').hide(); 
        for (field in data['person']) {
            if (field != 'avatar') {
                $('#' + field + '_field').text(data['person'][field]);
            } else {
                $('#avatar_field').attr('src', data['person'][field]);
            }
        }
    });
    initFileUploading();
});

$('#edit').click(function() {
    $('#person-info').hide();
    $('#form-container').show(); 
});

$('#cancel').click(function() {
    $('#person-info').show();
    $('#form-container').hide();
});