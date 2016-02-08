var last_req_id = -1;  // id of the last processed request
var domain = document.location.origin;  // page url
var focused = document.hasFocus();
var done_last_update = true;  // condition variable. see: process_requests()
var min_prior = 0;  // minimum possible priority
var max_prior;  // maximum possible priority
var selected_prior_min, selected_prior_max;  // currently selected prioritites
var order = 'time';  // currently selected ordering
var unseen_amount = 0;  // amount of unsees requests (for page title)
var select_control; 
var slider;
var authenticated;
var req_queue = [];

/*
Way this code works:
When document is ready request queue is initalized out of table data.

Then process_requests starts polling server for new requests based on 
options which user selected. New requests are being added to the queue
and it is being sorted and sliced. After this table rerenders.

When user changes some options completely new request queue is build
(see on_requests_reponse).*/


$(window).focus(function() {
    focused = true;
    document.title = 'Requests';
})
.blur(function() {
    focused = false;
});


function process_requests() {
    /*
    Makes get request to server to check for new requests.
    If there are new requests it adds them to request queue,
    sorts the queue, slices it and rerenders the table.

    Depending if there's user on a page it may changes title.

    Note: function grabs done_last_update condition variable in order to
    prevent situation when the last process_request did not finish
    working while other is being called with the same last request id.
    If this would happen then few table entries would exist for one request*/

    if (done_last_update) {
        done_last_update = false;
        var url = build_url(get_last_request_id(), build_options());
        $.get(url, function process_data(data) {
            var json_reqs = JSON.parse(data);
            if (json_reqs.length > 0) {
                last_req_id = get_max_id(json_reqs);
                update_queue(json_reqs.map(create_request));
                render_table(req_queue);
            }
            update_title(json_reqs.length);
            done_last_update = true;
        })
        .fail(function() {
            done_last_update = true;
        })
    }
}


function update_title(additional_amount) {
    /*
    Adds additional amount of requests to unseen amount
    and changes title if user is not on page*/

    unseen_amount += additional_amount;
    if (!focused) {
        if (unseen_amount > 0) {
            document.title = '(' + unseen_amount + ') Requests';
        }
    } else {
        unseen_amount = 0;
    }
}


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


function get_max_id(json_reqs) {
    /*
    Gets maximum id of requests returned from the server as json*/

    return Math.max.apply(Math, json_reqs.map(function(obj) { 
        return obj.pk;
    }));
}


function update_queue(reqs) {
    /*
    Upates request queue with new requests*/

    req_queue.push.apply(req_queue, reqs);
    req_queue.sort(compare);
    req_queue = req_queue.slice(req_queue.length-10);
}


function compare(reqA, reqB) {
    /*
    Compare function for sorting request queue depening on ordering*/

    if (order == 'time') {
        if (reqA.time < reqB.time) {
            return -1;
        } else if (reqA.time > reqB.time) {
            return 1;
        } else if (reqA.priority < reqB.priority) {
            return -1
        } else if (reqA.priority > reqB.priority) {
            return 1;
        } else {
            return 0;
        }
    } else {
        if (reqA.priority < reqB.priority) {
            return -1;
        } else if (reqA.priority > reqB.priority) {
            return 1;
        } else if (reqA.time < reqB.time) {
            return -1;
        } else if (reqA.time > reqB.time) {
            return 1;
        } else {
            return 0;
        }
    }
}


function get_initial_queue() {
    /*
    Transforms server rendered table into request queue*/

    return $('tbody').children().map(function(_, tr) {
        data = $(tr).children().map(function(_, td) {
            return td.innerHTML;
        });
        return {
            'time': new Date(Date.parse(data[0])),
            'method': data[1],
            'path': data[2],
            'priority': parseInt(data[3])
        };
    });
}


function build_url(last_id, options) {
    /*
    Depending on options builds url. If last_id is not null then
    goes for /api/requests/last_id?... else 
    goes for /api/requests/?...*/

    var url = domain + '/api/requests'
    if (last_id) {
        url += '/' + last_id;
    }
    url += '?';
    for (option in options) {
        url += option + '=' + options[option] + '&';
    }
    return url;
}


function build_options() {
    /*
    Creates options object depending on what user selected on page*/

    return {
        'order': order,
        'lower': selected_prior_min,
        'upper': selected_prior_max
    };
}


function create_request(json_req) {
    /*
    Creates convenient request object out of json request object returned 
    from backend*/

    return {
        'id': json_req['pk'],
        'path': json_req['fields']['path'],
        'method': json_req['fields']['method'],
        'priority': parseInt(json_req['fields']['priority']),
        'time': new Date(Date.parse(json_req['fields']['datetime']))
    };
}


function _add_req_to_table(req) {
    /*
    Adds request to the table*/

    append = '<tr><td>' + build_time_string(req.time) + '</td><td>'
             + req.method + '</td><td>' 
             + req.path + '</td><td>'
             + req.priority + '</td>';
    if (authenticated) {
        append += '<td><a href="/requests/edit/' +
                  req.id + '/">Edit</a></td>'
    }
    append += '</tr>'
    if ($('tbody').children().length > 0) {
        $('tbody > tr:first').before(append);
    } else {
        $('tbody').append(append);
    }
}


function build_time_string(time) {
    /*
    Given Date object return string in format 'day/month/year hours:minutes'*/

    var year = time.getUTCFullYear(),
        month = String('0' + time.getUTCMonth()).slice(-2),
        day = String('0' + time.getUTCDate()).slice(-2),
        hours = String('0' + time.getUTCHours()).slice(-2),
        mins = String('0' + time.getUTCMinutes()).slice(-2);
    return day+'/'+month+'/'+year+' '+hours+':'+mins;
}


function render_table(queue) {
    /*
    Renders table out of a given request queue*/

    $('tbody tr').remove();
    queue.forEach(_add_req_to_table);
}


function on_requests_reponse(data) {
    /*
    Callback for event that fires when user changes some controls*/

    var requests = JSON.parse(data);
    if (requests.length > 0) {
        last_req_id = get_max_id(requests);
    }
    requests = requests.slice(requests.length-10);
    req_queue = requests.map(create_request);
    render_table(req_queue.reverse());
    unseen_amount = 0;
}


function init_variables() {
    /*
    Sets variables when page is loaded*/

    max_prior = parseInt($('#max-prior').text());
    authenticated = $('#authenticated').text() == 'True';
    selected_prior_max = max_prior;
    selected_prior_min = min_prior;
    $('#slider').slider({
        'min': min_prior,
        'max': max_prior,
        'step': 1,
        'value': [selected_prior_min, selected_prior_max]
    });
    slider = $('#slider').slider();
    select_control = $('#order-select');
    req_queue = get_initial_queue();
}


$(document).ready(function () {
    
    init_variables();

    slider.on('slideStop', function(e) {
        selected_prior_min = slider.data('slider').getValue()[0];
        selected_prior_max = slider.data('slider').getValue()[1];
        var url = build_url(null, build_options())
        $.get(url, on_requests_reponse);
    });

    select_control.on('change', function(e) {
        order = select_control.val();
        var url = build_url(null, build_options())
        $.get(url, on_requests_reponse);
    });

    process_requests();
    setInterval(process_requests, 1000);
});