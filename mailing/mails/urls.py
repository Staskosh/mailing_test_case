from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_templates/', views.get_templates, name='get_templates'),
    url(r'^get_contacts/', views.get_contacts, name='get_contacts'),
    url(r'^mailing-list/$', views.show_mailing_list, name='show_mailing_list'),
    url(r'^mailing-list/(?P<mailing_id>\d+)/$', views.show_mailing_details, name='show_mailing_details'),
    url(r'^send_mails/', views.send_mails, name='send_mails'),
    url(r'^check_email_status/', views.check_email_status, name='check_email_status'),
    url(r'^tracking/(?P<email_token>[0-9a-fA-F-]+)/$', views.track_email_open, name='track_email_open'),
]
