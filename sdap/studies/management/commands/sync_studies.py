
from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
import time
import json

from sdap.studies.models import ExpressionStudy, ExpressionData, Database
from django.core.files import File
from sdap.users.models import User
from django.conf import settings

def sync_study(row):

    studies = ExpressionStudy.objects.filter(pmid=row['PubMedID'], technology=parse_values(row['technology']), species=parse_values(row['species']))

    if studies.count() == 0:
        return False

    if studies.count() > 1 :
        print("Error : More than one study matching " + row['PubMedID'])
        return True

    dict = {
        "article": row['article'],
        "status": "PUBLIC",
        "ome": parse_values(row['ome']),
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
    }

    need_update = False
    for key, value in dict.items():
        if not getattr(studies[0], key) == value:
            need_update = True

    if need_update:
        print("Updating " + row['PubMedID'])
        studies.update(**dict)

    jbrowse_id = row['RGVID']
    for study in studies:
        if study.data:
            for data in study.data.all():
                need_update = False
                if not data.jbrowse_id == jbrowse_id:
                    data.jbrowse_id = jbrowse_id
                    need_update = True
                if "JBrowseStatus" in row:
                    if row["JBrowseStatus"] == "yes":
                        status = True
                    else:
                        status = False
                    if not data.has_jbrowse == status:
                        data.has_jbrowse = status
                        need_update = True

                if need_update:
                    data.save()
    return True

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

    if sync_study(row):
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
    print("Creating study " + dict["article"])

    study = ExpressionStudy(**dict)
    study.save()

    for path in parse_values(row['path']):
        print("Creating file with path: " + path)
        if not os.path.exists("/app/loading_data/" + path):
            print("Missing file : skipping")
            continue
        data_dict = {
            "name": "data_genelevel",
            "species": species_dict[row['species']],
            "technology": row['technology'],
            "study": study,
            "jbrowse_id": row['JBrowseLABEL'],
            "created_by": superuser
        }
        if path.split('/')[-1] != "data_genelevel.txt":
            data_dict['name'] = path.split('/')[-1].replace(".txt","").replace("_", " ")

        expression_file = ExpressionData(**data_dict)

        expression_file.file.save(path.split('/')[-1], File(open(study_folder + path)), save=False)
        expression_file.save()

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
    help = 'Add new studies to the DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('metadata_file', type=str, help='Path to metadata file', default="/rgv_data/studies/metadata.csv")
        parser.add_argument('studies_folder', type=str, help='Folder containing the studies folder', default="/rgv_data/")

    def handle(self, *args, **options):
        folder = options['studies_folder']
        if not folder.endswith('/'):
            folder += "/"

        populate_data(options['metadata_file'], folder)
