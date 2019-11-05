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
        (None,               {'fields': ['database','article', 'pmid', 'ome', 'technology', 'species', 'experimental_design', 'topics', 'tissues', 'sex',
                                        'dev_stage', 'age', 'antibody', 'mutant', 'cell_sorted', 'keywords', 'samples_count', 'data'
                                        ]
                             }
        ),
    ]

class ExpressionDataAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'file',
                                        ]
                             }
        ),
    ]

class GeneAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['gene_id','tax_id','symbol','synonyms','description','homolog_id','ensemble_id'
                                        ]
                             }
        ),
    ]
    list_display = ['symbol', 'gene_id']



admin.site.register(ExpressionStudy, ExpressionStudyAdmin)
admin.site.register(ExpressionData, ExpressionDataAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Database)



