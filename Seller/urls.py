from django.urls import path
from .views import *

urlpatterns = [
    path('LogIn/',LogIn,name='LogIn'),
    path('SignUp/',SignUp,name='SignUp'),
    path('LogOut/',LogOut,name='LogOut'),
    path('seller_index/',seller_index,name='seller_index'),
]
