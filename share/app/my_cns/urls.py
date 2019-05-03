from django.urls import path, include

from . import views

app_name = 'my_cns'

urlpatterns = [
    path('', views.LoginView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('topics_list/', views.TopicsListView.as_view(), name='topics_list'),
    path('topics_list/<int:page>/', views.get_topics, name='topics_list_page'),
    path('topic_detail/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('download/', views.GetDownloadFileView.as_view(), name='download'),
]
