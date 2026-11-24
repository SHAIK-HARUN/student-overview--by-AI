from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('students/', views.view_students, name='view_students'),
    path('predictions/', views.view_predictions, name='view_predictions'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('train/', views.train_model_view, name='train_model'),
    path('charts/', views.admin_charts, name='admin_charts'),
    path('charts/api/', views.chart_data_api, name='chart_data_api'),
    path('detection-ratio/', views.detection_ratio_view, name='detection_ratio'),
]
