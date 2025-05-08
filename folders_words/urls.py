from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views


app_name = 'folders_words'
urlpatterns = [
  
    path('',views.folders.as_view(),name="folders"),
    path('folder/<int:pk>/',views.folder.as_view(),name="folder"),
    path('folder/<int:pk>/add_word/',views.AddWordView.as_view(),name="add_word"),
    path('folder/<int:pk>/edit_word/<int:id>',views.edit_word.as_view(),name="edit_word"),
    path('delete_word/<int:pk>/<int:word_id>/', views.delete_word, name='delete_word'),
    path('delete_selected_words/', views.delete_selected_words, name='delete_selected_words'),
    path('generate_pdf/<int:folder_id>/', views.generate_pdf, name='generate_pdf'),

]
