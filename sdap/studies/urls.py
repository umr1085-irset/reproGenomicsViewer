from django.urls import path, re_path
from sdap.studies import views
from sdap.studies import autocompletes

app_name = 'studies'
# Define urls here
urlpatterns = [
    path('', views.index, name='index'),
    path('view/<int:stdid>', views.ExpressionStudyDetailView, name="study_view"),
    path('create/study', views.CreateExpressionStudyView.as_view(), name='study_create'),
    path('create/gene_list', views.create_gene_list, name='gene_list_create'),
    path('create/document/<int:stdid>', views.add_document, name='document_create'),
    path('edit/study/<int:stdid>', views.EditExpressionStudyView.as_view(), name='study_edit'),
    path('download/document/<int:documentid>', views.download_document, name='document_download'),
    path('delete/document/<int:documentid>', views.delete_document, name='document_delete'),
    path('delete/study/<int:stdid>', views.delete_study, name='study_delete'),
    path('select/table', views.render_table, name='render_table'),
    path('select/document', views.document_select, name='select_documents'),
    path('graph', views.show_graph, name='graph'),
    path('graph_data', views.get_graph_data, name="graph_data"),
    re_path(r'^gene-autocomplete/$', autocompletes.GeneAutocomplete.as_view(), name='gene-autocomplete'),
    path('gene/<int:gene_id>', views.get_gene, name="get_gene"),
    path('table/<int:document_id>', views.get_genes_values_table, name="get_genes_values_table"),
    path('ajax/get_stud_db', views.get_stud_db, name="get_stud_db"),
    path('ajax/group_info', views.get_group_info, name="group_info"),
    path('ajax/class_info', views.get_class_info, name="class_info"),
    path('ajax/autocomplete_genes/<str:taxonid>', views.autocomplete_genes, name="autocomplete_genes"),
    re_path(r'^ome-autocomplete/$', autocompletes.OmeAutocomplete.as_view(), name="ome-autocomplete"),
    re_path(r'^technology-autocomplete/$', autocompletes.TechnologyAutocomplete.as_view(), name="technology-autocomplete"),
    re_path(r'^experimental-design-autocomplete/$', autocompletes.ExperimentalDesignAutocomplete.as_view(), name="experimental-design-autocomplete"),
    re_path(r'^topic-autocomplete/$', autocompletes.TopicAutocomplete.as_view(), name="topic-autocomplete"),
    re_path(r'^tissue-autocomplete/$', autocompletes.TissueAutocomplete.as_view(), name="tissue-autocomplete"),
    re_path(r'^sex-autocomplete/$', autocompletes.SexAutocomplete.as_view(), name="sex-autocomplete"),
    re_path(r'^dev-stage-autocomplete/$', autocompletes.DevStageAutocomplete.as_view(), name="dev-stage-autocomplete"),
    re_path(r'^antibody-autocomplete/$', autocompletes.AntibodyAutocomplete.as_view(), name="antibody-autocomplete"),
    re_path(r'^mutant-autocomplete/$', autocompletes.MutantAutocomplete.as_view(), name="mutant-autocomplete"),
    re_path(r'^cell-sorted-autocomplete/$', autocompletes.CellSortedAutocomplete.as_view(), name="cell-sorted-autocomplete"),
    re_path(r'^topic-autocomplete/$', autocompletes.TopicAutocomplete.as_view(), name="topic-autocomplete"),
]
