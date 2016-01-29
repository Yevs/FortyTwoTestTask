var last_req_id = -1;
var domain = document.location.origin;
var focused = document.hasFocus();
var req_queue = [];

$(window).focus(function() {
    focused = true;
    document.title = 'Requests';
    req_queue.forEach(add_req_to_table);
    req_queue = [];
})
.blur(function() {
    focused = false;
});

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

function process_requests() {
    $.get(domain + '/api/requests/' + get_last_request_id() + '/', 
        function process_data(data) {
            console.log(data);
            var reqs = JSON.parse(data);
            if (reqs.length > 0) {
                last_req_id = reqs[0]['id'];
            }
            req_queue.push.apply(req_queue, reqs);
            if (!focused) {
                if (req_queue.length > 0) {
                    document.title = '(' + req_queue.length + ') Requests';
                }
            }
    });
}

setInterval(process_requests, 300);