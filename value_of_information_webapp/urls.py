from django.urls import path
import views

urlpatterns = [
    path('',views.home, name='home'),
    path('get_result/<query_uid>', views.get_result)
]
