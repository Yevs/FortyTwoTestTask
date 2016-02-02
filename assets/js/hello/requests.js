var table_len = $('tbody tr').length;  // if there were less than 10 requests on page originally
var last_req_id = -1;  // id of the last processed request
var domain = document.location.origin;  // page url
var focused = document.hasFocus();
var done_last_update = true;  // condition variable. see: process_requests()

/* instead of displaying requests asap
   first put them into the queue and empty it
   as soon as user visits the page*/
var req_queue = []; 

function get_last_request_id() {
    /*
    Returns id of the last request and saves resutl to last_req_id*/

    if (last_req_id == -1) {
        last_req_id = $('#last-req-id')[0].innerHTML;
        return last_req_id;
    } else {
        return last_req_id;
    }
}

function add_req_to_table(req) {
    /*
    Parses requests from req argument and adds them to the table*/

    var time = new Date(Date.parse(req['fields']['datetime'])),
        path = req['fields']['path'],
        method = req['fields']['method'];
    var year = time.getUTCFullYear(),
        month = String('0' + time.getUTCMonth()).slice(-2),
        day = String('0' + time.getUTCDate()).slice(-2),
        hours = String('0' + time.getUTCHours()).slice(-2),
        mins = String('0' + time.getUTCMinutes()).slice(-2);
    var time_str = day+'/'+month+'/'+year+' '+hours+':'+mins;
    $('tbody > tr:first').before('<tr><td>' + time_str + '</td><td>'
                                 + method + '</td><td>' 
                                 + path + '</tr></td>');
}

function empty_req_queue() {
    /*
    Emptys request quests and adds request from it to table
    Only last 10 requests will be added, others deleted.*/

    req_queue.forEach(add_req_to_table);
    table_len += req_queue.length;
    while (table_len > 10) {
        $('tbody tr:last-child').remove();
        table_len--;
    }
    req_queue = [];
}

function process_requests() {
    /*
    Makes get request to server to check for new requests.
    If there are new requests it adds them to request queue.
    Depending if there's user on a page just changes title
    or emptys queue by calling empty_req_queue

    Note: funtion grabs done_last_update condition variable in order to
    prevent situation when the last process_request did not finish
    working while other is being called with the same last request id.
    If this would happen then few table entries would exist for one request*/

    if (done_last_update) {
        done_last_update = false;
        var url = domain + '/api/requests/' + get_last_request_id() + '/';
        $.get(url, function process_data(data) {
            var reqs = JSON.parse(data);
            if (reqs.length > 0) {
                last_req_id = reqs[reqs.length - 1]['pk'];
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