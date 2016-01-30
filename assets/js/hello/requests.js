var table_len = $('tbody tr').length; // if there were less than 10 requests on page originally
var last_req_id = -1;
var domain = document.location.origin;
var focused = document.hasFocus();
var req_queue = [];
var done_last_update = true; // in case request will take more than a second

function get_last_request_id() {
    if (last_req_id == -1) {
        last_req_id = $('#last-req-id')[0].innerHTML;
        return last_req_id;
    } else {
        return last_req_id;
    }
}

function add_req_to_table(req) {
    var time = req['datetime'],
        path = req['path'],
        method = req['method'];
    $('tbody > tr:first').before('<tr><td>' + time + '</td><td>'
                                 + method + '</td><td>' 
                                 + path + '</tr></td>');
}

function empty_req_queue() {
    req_queue.forEach(add_req_to_table);
    table_len += req_queue.length;
    while (table_len > 10) {
        $('tbody tr:last-child').remove();
        table_len--;
    }
    req_queue = [];
}

function process_requests() {
    if (done_last_update) {
        done_last_update = false;
        var url = domain + '/api/requests/' + get_last_request_id() + '/';
        $.get(url, function process_data(data) {
            var reqs = JSON.parse(data);
            if (reqs.length > 0) {
                last_req_id = reqs[reqs.length - 1]['id'];
            }
            req_queue.push.apply(req_queue, reqs);
            if (!focused) {
                if (req_queue.length > 0) {
                    document.title = '(' + req_queue.length + ') Requests';
                }
            } else {
                empty_req_queue();
            }
            done_last_update = true;
        })
        .fail(function() {
            done_last_update = true;
        })
    }
}

$(window).focus(function() {
    focused = true;
    document.title = 'Requests';
    empty_req_queue();
})
.blur(function() {
    focused = false;
});



process_requests();
setInterval(process_requests, 1000);