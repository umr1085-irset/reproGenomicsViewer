from dal import autocomplete
from django.db.models import Q

from guardian.shortcuts import get_perms
from .models import ExpressionStudy, Gene, Species

def get_param_values(parameter, query):
    qs = ExpressionStudy.objects.all()
    values = set()
    for study in qs:
        for val in getattr(study, parameter):
            values.add(val)
    values = list(values)
    if query:
        values = [val for val in values if val.lower().startswith(query.lower())]
    return list(values)

class GeneAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        query = self.q
        species_id = self.forwarded.get('species')
        species= Species.objects.get(id=species_id)
        qs = Gene.objects.filter(tax_id=species.species_id)
        if query:
            qs = qs.filter(Q(symbol__icontains=query) | Q(synonyms__icontains=query)| Q(gene_id__icontains=query))
        return qs

    def get_result_label(self, result):
        return "{} ({})".format(result.symbol, result.gene_id)

class ExpressionStudyAutocomplete(autocomplete.Select2QuerySetView):

    def get_result_value(self, result):
        return result

    def get_result_label(self, result):
        return result

class OmeAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('ome', self.q)

class TechnologyAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('technology', self.q)

class ExperimentalDesignAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('experimental_design', self.q)

class TopicAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('topics', self.q)

class TissueAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('tissues', self.q)

class SexAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('sex', self.q)

class DevStageAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('dev_stage', self.q)

class AntibodyAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('antibody', self.q)

class MutantAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('mutant', self.q)

class CellSortedAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('cell_sorted', self.q)

class KeywordAutocomplete(ExpressionStudyAutocomplete):

    def get_queryset(self):
        return get_param_values('keywords', self.q)
