from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('create/', views.create_ranch, name='create_ranch'),
    path('ranch/<int:ranch_id>/', views.ranch_detail, name='ranch_detail'),
    path('ranch/<int:ranch_id>/block/create/', views.create_block, name='create_block'),
    path('ranch/<int:ranch_id>/set/create/', views.create_irrigation_set, name='create_irrigation_set'),
    path('ranch/<int:ranch_id>/schedule/create/', views.create_irrigation_schedule, name='create_irrigation_schedule'),
    path('block/<int:block_id>/history/', views.block_history, name='block_history'),
    path('water-meter-reading/create/', views.create_water_meter_reading, name='create_water_meter_reading'),
    path('ranch/<int:ranch_id>/allocation-status/', views.ranch_allocation_status, name='ranch_allocation_status'),
    path('well/create/<int:ranch_id>/', views.create_well, name='create_well'),
    path('well/<int:ranch_id>/', views.well_list, name='well_list'),
    path('ranch/<int:ranch_id>/report/', views.ranch_report, name='ranch_report'),
]
