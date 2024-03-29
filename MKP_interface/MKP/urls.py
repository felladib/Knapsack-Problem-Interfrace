from django.urls import path
from . import views  # Importez le module de vues de votre application

urlpatterns = [
    path(r'',views.home),
    path('Home/', views.home, name='homepage'),  # Utilisez views.home pour référencer la vue
    path('simulation/', views.simulation, name='simulationpage'),

    path('delete_sac/<int:sac_id>/', views.delete_sac, name='delete_sac'),
    path('delete_obj/<int:obj_id>/', views.delete_obj, name='delete_obj'),
    
    
     path('add_sac/', views.add_sac, name='add_sac'),
     path('add_obj/', views.add_obj, name='add_obj'),
     path('run_algorithm/', views.run, name='run'),
     
     
]