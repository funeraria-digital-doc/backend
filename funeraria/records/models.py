#from django.db import models
from djongo import models
from groups.models import Group
from django_currentuser.db.models import CurrentUserField
import logging
from django.core.cache import cache
logger = logging.getLogger(__name__)
cache_keys = ['records_per_month_1', 'records_per_month_3', 'records_per_month_6', 'deaths_in_last_30', 'deaths_in_last_60', 'deaths_in_last_90', 'current_month_services', 'best_month', 'current_year_services']
class Record(models.Model):

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name = "record_group")
    created_by = CurrentUserField(related_name='record_created_by')
    updated_by = CurrentUserField(related_name='record_updated_by',on_update=True)
    
    email = models.EmailField(max_length=32, db_column='email', null=True, blank=True) 
    status = models.CharField(max_length=64,  db_column='status', null=True, blank=True, default="ACTIVE")  
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    photo = models.CharField(max_length=10000000, null=True)
    name = models.CharField(max_length=255,unique=True, db_column='name') 
    gender = models.CharField(max_length=64, db_column='gender') 
    marital_status = models.CharField(max_length=64,  db_column='marital_status', null=True, blank=True) 
    cc = models.CharField(max_length=16, db_column='cc', null=True, blank=True) 
    cc_valid_until = models.DateField(db_column='cc_valid_until', null=True, blank=True)
    nif = models.CharField(max_length=16, db_column='nif', null=True, blank=True) 
    niss = models.CharField(max_length=16, db_column='niss', null=True, blank=True) 
    birthday = models.DateField(db_column='birthday', null=True, blank=True) 
    age = models.IntegerField(db_column='age', null=True, blank=True) 
    address = models.CharField(max_length=255, db_column='address', null=True, blank=True) 
    parish = models.CharField(max_length=255, db_column='parish', null=True, blank=True) 
    municipality = models.CharField(max_length=255, db_column='municipality', null=True, blank=True) 
    district = models.CharField(max_length=255, db_column='district', null=True, blank=True) 
    nationality = models.CharField(max_length=255, db_column='nationality', null=True, blank=True) 
    mother_name = models.CharField(max_length=255, db_column='mother_name', null=True, blank=True) 
    father_name = models.CharField(max_length=255, db_column='father_name', null=True, blank=True) 
    last_mariage_date = models.DateField(db_column='last_mariage_date', null=True, blank=True)

    spouse_name = models.CharField(max_length=255,null=True, blank=True, db_column='spouse_name')
    spouse_gender = models.CharField(max_length=64, db_column='spouse_gender',null=True, blank=True)
    spouse_age = models.IntegerField(db_column='spouse_age', null=True, blank=True)

    naturality_parish = models.CharField(max_length=255, db_column='naturality_parish', null=True, blank=True) 
    naturality_municipality = models.CharField(max_length=255, db_column='naturality_municipality', null=True, blank=True)

    death_date = models.DateField(db_column='death_date', null=True, blank=True)
    death_time = models.TimeField(db_column='death_time', null=True, blank=True)
    death_address = models.CharField(max_length=255, db_column='death_address', null=True, blank=True) 
    death_parish = models.CharField(max_length=255, db_column='death_parish', null=True, blank=True) 
    death_municipality = models.CharField(max_length=255, db_column='death_municipality', null=True, blank=True)
    cemetery = models.CharField(max_length=255, db_column='cemetery', null=True, blank=True)
    cemetery_municipality = models.CharField(max_length=255, db_column='cemetery_municipality', null=True, blank=True)
    grave_number = models.CharField(max_length=16, db_column='grave_number', null=True, blank=True)
    grave_row = models.CharField(max_length=16, db_column='grave_row', null=True, blank=True)
    grave_site = models.CharField(max_length=64, db_column='grave_site', null=True, blank=True)
    death_retired = models.BooleanField(db_column='death_retired', null= True, blank=True)
    death_left_assets = models.BooleanField(db_column='death_left_assets', null= True, blank=True)
    death_made_will = models.BooleanField(db_column='death_made_will', null= True, blank=True)
    death_leaves_hereditary = models.BooleanField(db_column='death_leaves_hereditary', null= True, blank=True)
    double_head = models.CharField(max_length=255, db_column='double_head', null=True, blank=True)
    double_head_address = models.CharField(max_length=255, db_column='double_head_address', null=True, blank=True)
    flowers = models.TextField(max_length=1024, db_column='flowers', null=True, blank=True)
    dead_location = models.CharField(max_length=128, db_column='dead_location', null=True, blank=True)
    cause_of_death = models.CharField(max_length=128, db_column='cause_of_death', null=True, blank=True)
    grave_message = models.CharField(max_length=128, db_column='grave_message', null=True, blank=True)

    wake_local = models.CharField(max_length=255, db_column='wake_local', null=True, blank=True) 
    wake_date = models.DateField(db_column='wake_date', null=True, blank=True)
    wake_time = models.TimeField(db_column='wake_time', null=True, blank=True)
    leaving_mortuary_datetime = models.DateTimeField(db_column='leaving_mortuary_time', null=True, blank=True)
    funeral_datetime = models.DateTimeField(db_column='funeral_datetime', null=True, blank=True)
    funeral_local = models.CharField(max_length=255, db_column='funeral_local', null=True, blank=True)
    mortuary = models.CharField(max_length=255, db_column='mortuary', null=True, blank=True)

    family_member_name = models.CharField(max_length=255, db_column='family_member_name', null=True, blank=True) 
    family_member_cc = models.CharField(max_length=16, db_column='family_member_cc', null=True, blank=True)
    family_member_cc_valid_until = models.DateField(db_column='family_member_cc_valid_until', null=True, blank=True)
    family_member_kinship = models.CharField(max_length=64, db_column='family_member_kinship', null=True, blank=True) 
    family_member_phone = models.CharField(max_length=32, db_column='family_member_phone') 
    death_declaration_number = models.CharField(max_length=32, db_column='death_declaration_number', null=True, blank=True) 
    objects = models.DjongoManager()

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        cache.delete_many(cache_keys)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        cache.delete_many(cache_keys)
        super().save(*args, **kwargs)
    
    

    
