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
    )

    name = models.CharField(max_length=200)
    gene_type = models.CharField(max_length=200,null=True, blank=True)
    gene_number = models.IntegerField(null=True, blank=True)
    file = models.FileField(upload_to='files/')
    species = models.CharField(max_length=50, choices=SPECIES_TYPE, default="9606")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    cell_number = models.IntegerField(null=True, blank=True)
    class_name = ArrayField(models.CharField(max_length=50, blank=True, null=True), default=list)
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
    api_key = models.CharField(max_length=200)
    apis = JSONField(blank=True, null=True)
    address = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=DB_TYPE, default="TEXT")
    status = models.CharField(max_length=50, choices=STATUS, default="DISABLE")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')

    def __str__(self):
        return self.name




class ExpressionStudy(models.Model):

    article = models.CharField(max_length=200)
    pmid = models.CharField(max_length=20)
    ome = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    technology = ArrayField(models.CharField(max_length=50, blank=True), default=list)
    species = ArrayField(models.CharField(max_length=50, blank=True), default=list)
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
    data = models.ManyToManyField(ExpressionData, related_name="studies")

    def __str__(self):
        return self.pmid

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
