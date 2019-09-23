from django.urls import path
from sdap.files import views


app_name = 'files'
# Define urls here
urlpatterns = [
    path('', views.index, name='index'),
    path('folder/<int:folderid>', views.subindex, name='subindex'),
    path('file/<int:fileid>', views.view_file, name='view_file'),
    path('file/<int:fileid>/visualize', views.get_visualization, name='get_visualization'),
    path('download/<int:fileid>', views.download_file, name='download_file'),
]
