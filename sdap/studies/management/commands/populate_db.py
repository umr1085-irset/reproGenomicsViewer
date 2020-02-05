from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
import time

from sdap.studies.models import ExpressionStudy, ExpressionData, Database
from django.core.files import File
from sdap.users.models import User
from django.conf import settings

def create_admin_user(admin_mail, admin_password):
    user = User.objects.create_superuser(username="admin", email=admin_mail, password=admin_password)
    return user

def create_database():
    return Database(name="The ReproGenomic Viewer").save()

def cleanup_files(pmid, technology, species, filename):

    orga_dict = {
        '9606': 'Homo_sapiens',
        '10090': 'Mus_musculus',
        '10116': 'Rattus_norvegicus',
        '9913': 'Bos_taurus',
        '9544': 'Macaca_mulatta',
        '9823': 'Sus_scrofa',
        '9031': 'Gallus_gallus',
        '7955': 'Danio_rerio',
        '9615': 'Canis_lupus_familiaris'
    }

    path =  os.path.join("studies/admin/{}/{}/{}/".format(pmid, technology, orga_dict[species]), filename)
    full_path =  settings.MEDIA_ROOT + "/" + path
    if os.path.exists(full_path):
        os.remove(full_path)
    if os.path.exists(full_path + ".pickle"):
        os.remove(full_path + ".pickle")

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
            "created_by": superuser
        }
        if path.split('/')[-1] != "data_genelevel.txt":
            data_dict['name'] = path.split('/')[-1].replace(".txt","").replace("_", " ")

        expression_file = ExpressionData(**data_dict)
        cleanup_files(study.pmid, data_dict['technology'], data_dict['species'], path.split('/')[-1])

        expression_file.file.save(path.split('/')[-1], File(open(study_folder + path)), save=False)
        expression_file.save()

def populate_data(metadata_file, studies_folder, admin_mail, admin_password):

    if not os.path.exists(metadata_file):
        print("Error : no metadata.csv file found.")
        return

    # Create DB
    dbs = Database.objects.all()
    if not dbs:
        database = create_database()
    else:
        database = dbs[0]

    users = User.objects.filter(username='admin')
    if not users:
        superuser = create_admin_user(admin_mail, admin_password)
    else:
        print("Warning: an admin user already exists. Skipping admin creation")
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
    help = 'Populate DB with data'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('metadata_file', type=str, help='Path to metadata file', default="/app/loading_data/metadata.csv")
        parser.add_argument('studies_folder', type=str, help='Folder containing the studies folder', default="/app/loading_data/")
        parser.add_argument('admin_mail', type=str, help='Admin mail address')
        parser.add_argument('admin_password', type=str, help='Admin password')

    def handle(self, *args, **options):
        folder = options['studies_folder']
        if not folder.endswith('/'):
            folder += "/"

        populate_data(options['metadata_file'], folder, options['admin_mail'], options['admin_password'])

