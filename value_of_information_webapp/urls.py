from django.urls import path
from value_of_information_webapp import views

urlpatterns = [
    path('',views.home, name='home'),
    path('task/<id>', views.task, name='task'),
    path('query/<id>', views.query, name='query'),
    path('submit', views.submit, name='submit'),
    path('csv/<task_id>', views.csv, name='csv'),
]
