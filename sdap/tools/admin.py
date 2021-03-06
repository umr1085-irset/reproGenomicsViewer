from django.contrib import admin
from django import forms
from .models import Category, Tool, Tag, ArgumentType
import sdap.tools.forms as tool_forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps



class AdminForm(forms.ModelForm):

    class Meta:
        model = Tool
        fields = ['name', 'type', 'category', 'short_description', 'description', 'status', 'created_by', 'icon', 'visuel', 'link', 'form_name', 'command_line', 'path', 'script_name', 'tags', 'argument_types']

    def is_valid(self):
        valid = super(AdminForm, self).is_valid()
        if not valid:
            return valid
        form_function = getattr(tool_forms, self.cleaned_data['form_name'], False)
        if not form_function:
            self.add_error("form_name", ValidationError(_('No form called {} was found. Check if it is present in tools/forms.py'.format(self.cleaned_data['form_name']))))
            return False
        return True

class ArgumentTypeAdminForm(forms.ModelForm):

    TYPE_CHOICES = (('Text', 'Text'),)

    type = forms.ChoiceField(choices = TYPE_CHOICES, label="Argument type", initial='Text', widget=forms.Select(), required=True)

    class Meta:
        model = ArgumentType
        fields = ['type']

class ArgumentTypeAdmin(admin.ModelAdmin):
    model = ArgumentType
    form = ArgumentTypeAdminForm

class ArgumentsAdmin(admin.TabularInline):
    model = Tool.argument_types.through

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description']}),
    ]


# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ArgumentsAdmin,]
    form = AdminForm

admin.site.register(Tool, ToolsAdmin)
admin.site.register(Tag)
admin.site.register(ArgumentType, ArgumentTypeAdmin)
admin.site.register(Category, CategoryAdmin)
