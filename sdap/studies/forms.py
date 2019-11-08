from dal import autocomplete
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, HTML, Button, Fieldset
from crispy_forms.bootstrap import FormActions, InlineField, StrictButton
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from django.http import JsonResponse, QueryDict



class ExpressionStudyFilterForm(forms.Form):

    article = forms.CharField(max_length=200, required=False, label="")

    def __init__(self, *args, **kwargs):

        studies = kwargs.pop('studies')
        super(ExpressionStudyFilterForm, self).__init__(*args, **kwargs)

        columns = {
            "pmid": set(),
            "ome": set(),
            "technology": set(),
            "species": set(),
            "experimental_design": set(),
            "topics": set(),
            "tissues": set(),
            "sex": set(),
            "dev_stage": set(),
            "age": set(),
            "antibody": set(),
            "mutant": set(),
            "cell_sorted": set(),
            "keywords": set()
        }
        # Get all values for columns
        for study in studies:
            for key, value in columns.items():
                value |= set(getattr(study, key, []))

        for key, value in columns.items():
            choices = ((None, "All"),)
            for content in value:
                choices = choices + ((content,content),)
            self.fields[key] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class':'browser-default custom-select'}))

        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'

class GeneFilterForm(forms.Form):

    gene = forms.ModelChoiceField(
        queryset=Gene.objects.all(),
        widget=autocomplete.ModelSelect2(url='/studies/gene-autocomplete', attrs={'data-minimum-input-length': 2})
    )

    def __init__(self, *args, **kwargs):

        super(GeneFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'gene',
            StrictButton('Add', css_class='btn-default'),
        )
