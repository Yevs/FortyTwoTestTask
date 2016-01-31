from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'hello.views.home', name='hello'),
    url(r'^requests/$', 'hello.views.requests', name='requests'),
    url(r'^api/requests/(?P<req_id>[0-9]+)/$',
        'hello.views.get_requests', name='get_requests'),
    url(r'^edit/$', 'hello.views.edit', name='edit'),
)
