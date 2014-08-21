from django.conf.urls import patterns, include, url
from users import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_function, name='login'),
    url(r'^logout/$', views.logout_function, name='logout'),
    url(r'^createuser/$', views.createuser, name='createuser'),
    url(r'^deleteuser/$', views.deleteuser, name='delete_user'),
    url(r'^lockuser/$', views.lockuser, name='lock_user'),
    url(r'^unlockuser/$', views.unlockuser, name='unlock_user'),
    url(r'^reset/$', views.resetpasswords, name='reset_passwords'),
    url(r'^manageservices/$', views.manage_services, name='manage_services'),
    url(r'^modifyuser/$', views.modify_user, name='modify_user'),
    # url(r'^opinnayte/', include('opinnayte.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
