import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django_better_admin_arrayfield.models.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.urls import reverse

from guardian.shortcuts import assign_perm, remove_perm, get_group_perms, get_user_perms

import sys
import pickle, os
import requests
from xml.etree import ElementTree as ET

def _set_values(study):
    species = set()
    technology = set()
    for data in study.data.all():
        species.add(data.get_species_display())
        technology.add(data.get_technology_display())
    study.species = list(species)
    study.technology = list(technology)
    study.save()

def _extract_date(elem):
    publish_date = ""
    year = ""
    month = ""
    year_elem = elem.find('Year')
    if year_elem is not None:
        year = year_elem.text
    month_elem = elem.find('Month')
    if month_elem is not None:
        month = month_elem.text
    if year:
        publish_date = year
    if month:
        publish_date =  month + ". " + publish_date
    return publish_date

def _extract_author(author_element):
    author_list = []
    for author in author_element:
        if author.find("CollectiveName") is not None:
            author_list.append(author.find("CollectiveName").text)
        else:
            name = ""
            lastname = author.find("LastName")
            firstname = author.find("Initials")
            if lastname is not None:
                name = lastname.text
            if firstname is not None:
                name = firstname.text + " " + name
            if name:
                author_list.append(name)
    return ",".join(author_list)

def get_pubmed_info(pmid):
    abstract = ""
    title = ""
    publish_date = ""
    authors = ""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&rettype=abstract".format(pmid)
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        elem = root.find('.//AbstractText')
        if elem is not None:
            abstract = elem.text
        elem = root.find('.//ArticleTitle')
        if elem is not None:
            title = elem.text
        elem = root.find('.//PubDate')
        if elem is not None:
            publish_date = _extract_date(elem)
        elem = root.find('.//AuthorList')
        if elem is not None:
            authors = _extract_author(elem)

    return abstract, title, publish_date, authors

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

def change_permission_owner(self):
    owner_permissions = ['view_expressionstudy', 'change_expressionstudy', 'delete_expressionstudy']

    if self.initial_owner:
        # If update, remove permission, else do nothing
        if self.initial_owner != self.created_by:
            initial_owner_permission = get_user_perms(self.initial_owner, self)
            for permission in owner_permissions:
                if permission in initial_owner_permission:
                    remove_perm(permission, self.initial_owner, self)

    user_permissions = get_user_perms(self.created_by, self)
    for permission in owner_permissions:
        if permission not in user_permissions:
            assign_perm(permission, self.created_by, self)

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
    title = models.CharField(max_length=200, blank=True)
    abstract = models.TextField(blank=True, default='', verbose_name='Abstract')
    publish_date = models.CharField(max_length=50, blank=True)
    authors = models.TextField(blank=True, default='', verbose_name='Authors')
    status = models.CharField(max_length=50, choices=STATUS, default="PRIVATE")
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
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    database = models.ForeignKey(Database, blank=True, null=True, on_delete=models.CASCADE, related_name='from_database')
    read_groups = models.ManyToManyField(Group, blank=True, related_name='read_access_to')
    edit_groups = models.ManyToManyField(Group, blank=True, related_name='edit_access_to')

    class Meta:
        permissions = (('view_expressionstudy', 'View study'),)
        default_permissions = ('add', 'change', 'delete')

    def __init__(self, *args, **kwargs):
        super(ExpressionStudy, self).__init__(*args, **kwargs)
        self.initial_pmid = self.pmid
        self.initial_owner = self.created_by
        self.initial_status = self.status

    def save(self, *args, **kwargs):
        super(ExpressionStudy, self).save(*args, **kwargs)
        if self.initial_pmid != self.pmid:
            self.abstract, self.title, self.publish_date, self.authors = get_pubmed_info(self.pmid)
        super(ExpressionStudy, self).save(*args, **kwargs)
        change_permission_owner(self)

    def get_absolute_url(self):
        return reverse('studies:study_view', kwargs={"stdid": self.id})

    def __str__(self):
        return self.pmid





@receiver(m2m_changed, sender=ExpressionStudy.read_groups.through)
def update__permissions_read(sender, instance, action, **kwargs):
    if instance.read_groups.all():
        if action == 'pre_remove':
            for group in instance.read_groups.all():
                if 'view_expressionstudy' in get_group_perms(group, instance):
                    remove_perm('view_expressionstudy', group, instance)
        if action == 'post_add':
            for group in instance.read_groups.all():
                if 'view_project' not in get_group_perms(group, instance):
                    assign_perm('view_expressionstudy', group, instance)

@receiver(m2m_changed, sender=ExpressionStudy.edit_groups.through)
def update__permissions_write(sender, instance, action, **kwargs):
    if instance.edit_groups.all():
        if action == 'pre_remove':
            for group in instance.edit_groups.all():
                if 'change_project' in get_group_perms(group, instance):
                    remove_perm('change_expressionstudy', group, instance)
        if action == 'post_add':
            for group in instance.edit_groups.all():
                if 'change_expressionstudy' not in get_group_perms(group, instance):
                    assign_perm('change_expressionstudy', group, instance)


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
        _set_values(self.study)

@receiver(models.signals.pre_delete, sender=ExpressionData)
def auto_delete_signature_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.exists(instance.file.path):
            os.remove(instance.file.path)
        if os.path.exists(instance.file.path + ".pickle"):
            os.remove(instance.file.path + ".pickle")

@receiver(models.signals.post_delete, sender=ExpressionData)
def auto_refresh_data_on_delete(sender, instance, **kwargs):
    if instance.study:
        _set_values(instance.study)

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
