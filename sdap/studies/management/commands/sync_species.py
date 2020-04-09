
from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
import time
import json

from sdap.studies.models import Species
from django.core.files import File
from sdap.users.models import User
from django.conf import settings

def sync_species(jbrowse_folder):

    species = {
        'Homo sapiens': {
            'jbrowse_folder' : 'hg38',
            'species_id': '9606',
        },
        'Macaca mulatta': {
            'jbrowse_folder' : 'rheMac8',
            'species_id': '9544',
        },
        'Mus musculus': {
            'jbrowse_folder' : 'mm10',
            'species_id': '10090',
        },
        'Rattus norvegicus': {
            'jbrowse_folder' : 'rn6',
            'species_id': '10116',
        },
        'Canis lupus familiaris': {
            'jbrowse_folder' : 'canFam3',
            'species_id': '9615',
        },
        'Bos taurus': {
            'jbrowse_folder' : 'bosTau8',
            'species_id': '9913',
        },
        'Sus scrofa': {
            'jbrowse_folder' : 'susScr3',
            'species_id': '9823',
        },
        'Gallus gallus': {
            'jbrowse_folder' : 'galGal5',
            'species_id': '9031',
        },
        'Danio rerio': {
            'jbrowse_folder' : 'danRer10',
            'species_id': '7955',
        }
    }

    for key, value in species.items():
        path = os.path.join(jbrowse_folder, value['jbrowse_folder'], 'trackList.json')
        results = {}
        if os.path.exists(path):
            with open(path) as jbrowse_file:
                data = json.load(jbrowse_file)
                results = {'sequence': {}, 'annotations': []}
                for track in data['tracks']:
                    if track["type"] == "SequenceTrack":
                        results["sequence"] = {'name':track["key"], 'jbrowse_id':track["label"]}
                    elif track["type"] == "CanvasFeatures":
                        results["annotations"].append({'name':track["key"], 'jbrowse_id':track["label"]})

        species = Species.objects.filter(name=key)
        if not species:
            species = Species(name=key, species_id=value['species_id'], jbrowse_name=value['jbrowse_folder'])
            species.save()
        else:
            species = species[0]
        if results and not species.jbrowse_data == results:
            species.jbrowse_data = results
            species.save()

class Command(BaseCommand):
    help = 'Sync species'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('jbrowse_folder', type=str, help='Folder containing the jbrowse species data', default="/app/loading_data/")

    def handle(self, *args, **options):

        sync_species(options['jbrowse_folder'])
