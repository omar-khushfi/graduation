from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/',views.Login_View  .as_view(),name="login_view"),
    path('signup/',views.Signup_View.as_view(),name="signup_view"),
    path('logout/',views.logout_view,name="logout_view"),
    path('forgot-password/', views.ForgotPassword.as_view(), name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword.as_view(), name='reset-password'),
   
    
    path('profile/',views.profile,name="profile"),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('edit-languages/', views.edit_languages, name='edit_languages'),
    

   
    
]
