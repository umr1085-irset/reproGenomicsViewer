from dal import autocomplete
from operator import itemgetter
import csv
import pandas as pd
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, HTML, Button, Fieldset
from crispy_forms.bootstrap import FormActions, InlineField, StrictButton
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from django.http import JsonResponse, QueryDict
from django.contrib.postgres.forms import SimpleArrayField

class ExpressionStudyCreateForm(forms.ModelForm):

    ome = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/ome-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    experimental_design = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/experimental-design-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    topics = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/topic-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    tissues = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/tissue-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )
    age = SimpleArrayField(forms.CharField(), required=False)

    sex = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/sex-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    dev_stage = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/dev-stage-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    antibody = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/antibody-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    mutant = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/mutant-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    cell_sorted = autocomplete.Select2ListCreateChoiceField(
                required=False,
                widget=autocomplete.TagSelect2(url='/studies/cell-sorted-autocomplete', attrs={"data-tags":"true", "data-html":True})
              )

    keywords = SimpleArrayField(forms.CharField(), required=False)

    class Meta:
        model = ExpressionStudy
        fields = ["article", "pmid", "samples_count", "read_groups", "edit_groups"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ExpressionStudyCreateForm, self).__init__(*args, **kwargs)
        self.fields['read_groups'].help_text = "Groups with viewing permission on project and subentities. Will be ignored if the visibility is set to public. Use 'ctrl' to select multiple/unselect."
        self.fields['edit_groups'].help_text = "Groups with editing permission on project and subentities. Use 'ctrl' to select multiple/unselect."

        # TODO : Give link to group creation interface?
        groups = self.user.groups.all()
        self.fields['read_groups'].queryset = groups
        self.fields['edit_groups'].queryset = groups

        self.fields.keyOrder = [
            'article',
            'pmid',
            'samples_count',
            'species'
            'ome',
            'technology',
            'experimental_design',
            'topics',
            'tissues',
            'age',
            'sex',
            'dev_stage',
            'antibody'
            'mutant',
            'cell_sorted',
            'edit_groups',
            'read_groups']

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class ExpressionStudyEditForm(ExpressionStudyCreateForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ExpressionStudyCreateForm, self).__init__(*args, **kwargs)
        self.fields['read_groups'].help_text = "Groups with viewing permission on project and subentities. Will be ignored if the visibility is set to public. Use 'ctrl' to select multiple"
        self.fields['edit_groups'].help_text = "Groups with editing permission on project and subentities. Use 'ctrl' to select multiple/unselect."

        # TODO : Give link to group creation interface?
        groups = self.user.groups.all()
        self.fields['read_groups'].queryset = groups
        self.fields['edit_groups'].queryset = groups

        # Need to do this because array fields don't play nice
        for key, value in self.fields.items():
            value.initial = getattr(self.instance, key)

        self.fields.keyOrder = [
            'article',
            'pmid',
            'samples_count',
            'species'
            'ome',
            'technology',
            'experimental_design',
            'topics',
            'tissues',
            'age',
            'sex',
            'dev_stage',
            'antibody'
            'mutant',
            'cell_sorted',
            'edit_groups',
            'read_groups']

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class ExpressionDataForm(forms.ModelForm):
    class Meta:
        model = ExpressionData
        fields = ["name", "technology", "species", "type", "file"]

    def __init__(self, *args, **kwargs):
        super(ExpressionDataForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'

    def clean_file(self):
        csv_file = self.cleaned_data['file']
        path = csv_file.temporary_file_path()
        try:
            data = pd.read_csv(path, sep='\t', header=None, nrows=20)
        except pandas.errors.ParserError as e:
            raise forms.ValidationError("File is not a proper TSV file.")

        if not len(data.columns) > 1:
            raise forms.ValidationError("The file must contains more than 1 column")

        data = data[data.columns[0]]
        if not all([var in data.values for var in ['Sample', 'X', 'Y']]):
            raise forms.ValidationError("The file must contain one ligne beginning with Sample, X and Y")
        if not any([var for var in data.values if var.startswith('Class:')]):
            raise forms.ValidationError("The file must contains at least one class, starting with 'Class:'")

        return csv_file




class ExpressionStudyFilterForm(forms.Form):

    article = forms.CharField(max_length=200, required=False, label="")
    pmid = forms.CharField(max_length=50, required=False, label="")

    def __init__(self, *args, **kwargs):

        studies = kwargs.pop('studies')
        super(ExpressionStudyFilterForm, self).__init__(*args, **kwargs)

        columns = {
            "ome": set(),
            "technology": set(),
            "species": {},
            "experimental_design": set(),
            "topics": set(),
            "tissues": set(),
            "sex": set(),
            "dev_stage": set(),
            "antibody": set(),
            "mutant": set(),
            "cell_sorted": set(),
        }
        # Get all values for columns
        for study in studies:
            for key, value in columns.items():
                if key == "technology":
                    value |= set([getattr(data, key, []) for data in study.data.all()])
                # Hacky hacky : we need to display the display value, and send the real value
                elif key == "species":
                    for data in study.data.all():
                        value[data.species] = data.get_species_display()
                else:
                    value |= set(getattr(study, key, []))

        for key, value in columns.items():
            choices = ((None, "All"),)
            if key == "species":
                for id, name in value.items():
                    choices = choices + ((id, name),)
            else:
                for content in value:
                    choices = choices + ((content,content),)
            choices = tuple(sorted(choices, key=itemgetter(1)))
            self.fields[key] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class':'browser-default custom-select'}))

        # We add it later for proper ordering
        self.fields['keywords'] = forms.CharField(max_length=200, required=False, label="")


        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'

class GeneListCreateForm(forms.ModelForm):

    genes = forms.ModelMultipleChoiceField(
                queryset=Gene.objects.all(),
                required=True,
                widget=autocomplete.ModelSelect2Multiple(url='/studies/gene-autocomplete', forward=['species'], attrs={'data-minimum-input-length': 3})
            )

    class Meta:
        model = GeneList
        fields = ["name", "species", "genes"]

    def __init__(self, *args, **kwargs):
        super(GeneListCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
