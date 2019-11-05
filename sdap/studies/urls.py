from django.urls import path, re_path
from sdap.studies import views

app_name = 'studies'
# Define urls here
urlpatterns = [
    path('', views.index, name='index'),
    path('select/table', views.render_table, name='render_table'),
    path('select/document', views.document_select, name='select_documents'),
    path('graph', views.show_graph, name='graph'),
    path('graph_data', views.get_graph_data, name="graph_data"),
    re_path(r'^gene-autocomplete/$', views.GeneAutocomplete.as_view(), name='gene-autocomplete'),
    path('gene/<int:gene_id>', views.get_gene, name="get_gene"),
    path('ajax/get_stud_db', views.get_stud_db, name="get_stud_db"),
    path('ajax/group_info', views.get_group_info, name="group_info"),
    path('ajax/autocomplete_gene', views.autocomplete_genes, name="autocomplete_genes"),
]
