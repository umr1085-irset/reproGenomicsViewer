from django.contrib import admin
from django import forms
from .models import *
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
import sdap.tools.forms as tool_forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps

class ExpressionStudyAdmin(admin.ModelAdmin, DynamicArrayMixin):
    fieldsets = [
        (None,               {'fields': ['database','article', 'pmid', 'status', 'ome', 'experimental_design', 'topics', 'tissues', 'sex',
                                        'dev_stage', 'age', 'antibody', 'mutant', 'cell_sorted', 'keywords', 'samples_count', 'read_groups', 'edit_groups',
                                        ]
                             }
        ),
    ]

class ExpressionDataAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'file','gene_type','gene_number', 'technology', 'species' ,'cell_number', 'study'
                                        ]
                             }
        ),
    ]
    list_display = ['name', 'class_name']

class GeneAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['gene_id','tax_id','symbol','synonyms','description','homolog_id','ensemble_id'
                                        ]
                             }
        ),
    ]
    list_display = ['symbol', 'gene_id']
    search_fields = ['symbol']

class GeneListAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name','created_by','species','genes'
                                        ]
                             }
        ),
    
    ]
    autocomplete_fields = ['genes']





admin.site.register(ExpressionStudy, ExpressionStudyAdmin)
admin.site.register(ExpressionData, ExpressionDataAdmin)
admin.site.register(GeneList, GeneListAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Database)



