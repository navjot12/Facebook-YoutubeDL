from django.conf.urls import patterns, include, url
from django.contrib import admin
from manager.views import MyChatBotView, index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'youtubeDL.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^facebook_auth$', MyChatBotView.as_view()),	#because this is a class based view- so have to do as_view
)