from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
import time

from sdap.studies.models import ExpressionStudy, ExpressionData, Database
from django.core.files import File
from sdap.users.models import User
from django.conf import settings

def process_study(row, database, superuser, study_folder):

    species_dict = {
        'Homo sapiens': '9606',
        'Mus musculus': '10090',
        'Rattus norvegicus': '10116',
        'Bos taurus': '9913',
        'Macaca mulatta': '9544',
        'Sus scrofa': '9823',
        'Gallus gallus': '9031',
        'Danio rerio': '7955',
        'Canis lupus familiaris': '9615',
    }

    study = ExpressionStudy.objects.filter(pmid=row['PubMedID'], technology=parse_values(row['technology']), species=parse_values(row['species']))

    if not study.count == 1:
        # Send mail admin?
        return


    dict = {
        "article": row['article'],
        "pmid": row['PubMedID'],
        "status": "PUBLIC",
        "ome": parse_values(row['ome']),
        "technology": parse_values(row['technology']),
        "species": parse_values(row['species']),
        "experimental_design": parse_values(row['experimental_design']),
        "topics": parse_values(row['biological_topics']),
        "tissues": parse_values(row['tissue_or_cell']),
        "sex": parse_values(row['sex']),
        "dev_stage":parse_values(row['developmental_stage']),
        "age": parse_values(row['age']),
        "antibody": parse_values(row['antibody']),
        "mutant": parse_values(row['mutant']),
        "cell_sorted": parse_values(row['cell_sorted']),
        "keywords": parse_values(row['keywords']),
        "samples_count": len(parse_values(row['sample_ID'])),
        "database": database,
        "created_by": superuser
    }
    print("Updating study " + dict["article"])

    study.update(**dict)

def populate_data(metadata_file, studies_folder):

    if not os.path.exists(metadata_file):
        print("Error : no metadata.csv file found.")
        return

    dbs = Database.objects.all()
    database = dbs[0]

    users = User.objects.filter(username='admin')
    superuser = users[0]

    df = pd.read_csv(metadata_file, sep=",")
    df = df.fillna('')
    for index, row in df.iterrows():
        process_study(row, database, superuser, studies_folder)

def parse_values(values):
    value_list = []
    if values:
        value_list = values.split("|")
    return value_list

class Command(BaseCommand):
    help = 'Edit studies'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('metadata_file', type=str, help='Path to metadata file', default="/app/loading_data/metadata.csv")
        parser.add_argument('studies_folder', type=str, help='Folder containing the studies folder', default="/app/loading_data/")

    def handle(self, *args, **options):
        folder = options['studies_folder']
        if not folder.endswith('/'):
            folder += "/"

        populate_data(options['metadata_file'], folder)
