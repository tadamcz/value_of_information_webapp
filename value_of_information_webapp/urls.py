from django.urls import path
import views

urlpatterns = [
    path('',views.home, name='home'),
    path('get_result/<task_id>', views.get_result)
]
