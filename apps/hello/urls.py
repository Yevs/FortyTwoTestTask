from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'hello.views.home', name='home'),
    url(r'^requests/$', 'hello.views.requests', name='requests'),
    url(r'^api/requests/(?P<req_id>[0-9]+)/$',
        'hello.views.get_requests', name='get_requests'),
    url(r'^api/edit/$', 'hello.views.edit_api', name='update'),
    url(r'^edit/$', 'hello.views.edit', name='edit'),
    url(r'^login/$', 'hello.views.login', name='login'),
    url(r'^logout/$', 'hello.views.logout', name='logout'),
)
