from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('display/', views.display_data, name='display_data'),
    path('summarize/', views.summarize_data, name='summarize_data'),
    path('send-email/', views.send_email_view, name='send_email'),
    path('email-success/', views.send_email_success, name='send_email_success'),
]
