from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('add-student/', views.add_student_view, name='add_student'),
    path('students/', views.student_list_view, name='student_list'),
    path('result/<int:pk>/', views.result_view, name='result_view'),
    path('result/<int:pk>/regenerate/', views.regenerate_result, name='regenerate_result'),
    path('history/', views.prediction_history, name='prediction_history'),
]
