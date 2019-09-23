from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from django.core.validators import MaxValueValidator, MinValueValidator

class VisualisationArgumentForm(forms.Form):

    def __init__(self, *args, **kwargs):

        visu_type = kwargs.pop('visu_type', False)
        table = kwargs.pop('table', False)
        super(VisualisationArgumentForm, self).__init__(*args, **kwargs)

        if visu_type and (visu_type == "Pieplot" or visu_type == "Barplot"):
            self.fields['Yvalues'] = forms.IntegerField(validators=[
                MaxValueValidator(len(table.index)),
                MinValueValidator(0)
            ])

        self.helper = FormHelper(self)
        self.helper.form_id= "visualization_form"
        self.helper.form_method = 'POST'
