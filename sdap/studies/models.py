import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django_better_admin_arrayfield.models.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps

import sys
import pickle, os

def get_upload_path(instance, filename):

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

    user_type = "user"
    if instance.created_by and instance.created_by.is_superuser:
        user_type = "admin"

    path =  os.path.join("studies/{}/{}/{}/{}/".format(user_type, instance.study.pmid, instance.technology, orga_dict[instance.species]), filename)
    return path

class Database(models.Model):

    DB_TYPE = (
        ('LOCAL', 'Local'),
        ('REMOTE', 'Remote'),
        ('FILE', 'File'),
    )

    STATUS = (
        ('AVAILABLE', 'Available'),
        ('DISABLE', 'Disable'),
    )

    name = models.CharField(max_length=200)
    description = models.TextField("description", blank=True)
    api_key = models.CharField(max_length=200, blank=True)
    apis = JSONField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=50, choices=DB_TYPE, default="TEXT")
    status = models.CharField(max_length=50, choices=STATUS, default="DISABLE")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')

    def __str__(self):
        return self.name

class ExpressionStudy(models.Model):

    STATUS = (
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
    )

    article = models.CharField(max_length=200)
    pmid = models.CharField(max_length=20)
    status = models.CharField(max_length=50, choices=STATUS, default="PRIVATE")
    ome = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    experimental_design = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    topics = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    tissues = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    sex = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    dev_stage = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    age = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    antibody = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    mutant = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    cell_sorted = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    keywords = ArrayField(models.CharField(max_length=200, blank=True), default=list)
    samples_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    database = models.ForeignKey(Database, blank=True, null=True, on_delete=models.CASCADE, related_name='from_database')

    def __str__(self):
        return self.pmid

class ExpressionData(models.Model):
    SPECIES_TYPE = (
        ('9606','Homo sapiens'),
        ('10090','Mus musculus'),
        ('10116','Rattus norvegicus'),
        ('9913','Bos taurus'),
        ('9544','Macaca mulatta'),
        ('9823','Sus scrofa'),
        ('9031','Gallus gallus'),
        ('7955','Danio rerio'),
        ('9615','Canis lupus familiaris')
    )

    TECHNOLOGY_TYPE = (
        ('RNA-Seq','RNA-Seq'),
        ('ATAC-Seq','ATAC-Seq'),
        ('scRNA-Seq','scRNA-Seq'),
        ('MeDIP-Seq','MeDIP-Seq'),
        ('MBD-Seq','MBD-Seq'),
        ('CAGE','CAGE'),
        ('HITS-CLIP','HITS-CLIP'),
        ('MNase-Seq','MNase-Seq'),
        ('DNase-Hypersensitivity','DNase-Hypersensitivity'),
        ('PolyA-Seq','PolyA-Seq'),
        ('hMeDIP-Seq','hMeDIP-Seq'),
        ('MRE-Seq','MRE-Seq'),
        ('CAP-Seq','CAP-Seq'),
        ('PAS-Seq','PAS-Seq'),
        ('RIP-Seq','RIP-Seq'),
        ('Microwell-Seq','Microwell-Seq'),
        ('ChIP-Seq','ChIP-Seq')
    )

    FILE_TYPE = (
        ('2D', '2D'),
        ('3D', '3D'),
    )

    name = models.CharField(max_length=200)
    technology = models.CharField(max_length=50, choices=TECHNOLOGY_TYPE, default="RNA-Seq")
    species = models.CharField(max_length=50, choices=SPECIES_TYPE, default="9606")
    type = models.CharField(max_length=50, choices=FILE_TYPE, default="2D")
    gene_type = models.CharField(max_length=200,null=True, blank=True)
    gene_number = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to=get_upload_path)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    cell_number = models.IntegerField(null=True, blank=True)
    class_name = ArrayField(models.CharField(max_length=50, blank=True, null=True), default=list)
    study = models.ForeignKey(ExpressionStudy, on_delete=models.CASCADE, related_name='data')
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(ExpressionData, self).save(*args, **kwargs)
        dIndex={'Sample':0}
        gene_type = "Entrez Gene"
        removed = ["X","Y","Sample"]
        pointer_list = []
        array_class = []
        f =  open(self.file.path)
        cell_number = 0
        nb_gene = 0

        while f.readline() != '':
            pointer_list.append(f.tell())

        for pointer in pointer_list:
            f.seek(pointer)
            sIdList = f.readline().rstrip().split("\t")[0]
            if cell_number == 0 :
                cell_number = len(f.readline().rstrip().split("\t"))-1

            if "Class:" in sIdList:
                array_class.append(sIdList.replace('Class:',''))
            if "Class" not in sIdList and sIdList not in removed and sIdList != '':
                nb_gene = nb_gene + 1
                if "ENS" in sIdList :
                    type = "Ensembl"
            dIndex[sIdList] = pointer
        pickle.dump(dIndex, open(self.file.path +".pickle","wb"))
        self.class_name = array_class
        self.gene_type = gene_type
        self.gene_number = nb_gene
        self.cell_number = cell_number
        super(ExpressionData, self).save(*args, **kwargs)

class Gene(models.Model):

    gene_id =  models.CharField(max_length=50)
    tax_id =  models.CharField(max_length=50, blank=True)
    symbol =  models.CharField(max_length=50, blank=True)
    synonyms =  models.TextField(blank=True)
    description =  models.TextField(blank=True)
    homolog_id =  models.CharField(max_length=50, blank=True)
    ensemble_id =  models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.gene_id
