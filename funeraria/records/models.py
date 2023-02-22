from django.db import models
from accounts.models import User

from groups.models import Group


def get_upload_path(instance, filename):
    if instance.name is not None:
        return instance.name + '/' + filename
    return '/' + filename

class Record(models.Model):
    class Gender(models.TextChoices):
        MAN = "1", "Male"
        WOMAN = "2", "Female"
        OTHER = "3", "Other"

    class MaritalStatus(models.TextChoices):
        SINGLE = "1", "Single"
        MARIED = "2", "Maried"
        DIVORCED = "3", "Divorced"
        WIDOWER = "4", "Widower"

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    photo = models.FileField(upload_to=get_upload_path, null=True)
    name = models.CharField(max_length=255,unique=True, db_column='name') 
    gender = models.CharField(max_length=64, choices=Gender.choices, db_column='gender') 
    marital_status = models.CharField(max_length=64, choices=MaritalStatus.choices,  db_column='marital_status', null=True) 
    cc = models.CharField(max_length=16,unique=True, db_column='cc', null=True) 
    nif = models.CharField(max_length=16,unique=True, db_column='nif', null=True) 
    niss = models.CharField(max_length=16,unique=True, db_column='niss', null=True) 
    birthday = models.DateField(db_column='birthday', null=True) 
    age = models.IntegerField(db_column='age', null=True) 
    address = models.CharField(max_length=255, db_column='address', null=True) 
    parish = models.CharField(max_length=255, db_column='parish', null=True) 
    municipality = models.CharField(max_length=255, db_column='municipality', null=True) 
    mother_name = models.CharField(max_length=255, db_column='mother_name', null=True) 
    father_name = models.CharField(max_length=255, db_column='father_name', null=True) 
    last_mariage_date = models.DateField(db_column='last_mariage_date', null=True)

    spouse_name = models.CharField(max_length=255,unique=True, db_column='spouse_name')
    spouse_gender = models.CharField(max_length=64, choices=Gender.choices, db_column='spouse_gender')
    spouse_age = models.IntegerField(db_column='spouse_age', null=True)

    naturality_parish = models.CharField(max_length=255, db_column='naturality_parish', null=True) 
    naturality_municipality = models.CharField(max_length=255, db_column='naturality_municipality', null=True)

    death_date = models.DateField(db_column='death_date', null=True)
    death_time = models.TimeField(db_column='death_time', null=True)
    death_address = models.CharField(max_length=255, db_column='death_address', null=True) 
    death_parish = models.CharField(max_length=255, db_column='death_parish', null=True) 
    death_municipality = models.CharField(max_length=255, db_column='death_municipality', null=True)
    cemetery = models.CharField(max_length=255, db_column='cemetery', null=True)
    cemetery_municipality = models.CharField(max_length=255, db_column='cemetery_municipality', null=True)
    grave_number = models.CharField(max_length=16, db_column='grave_number', null=True)
    grave_row = models.CharField(max_length=16, db_column='grave_row', null=True)
    grave_site = models.CharField(max_length=64, db_column='grave_site', null=True)
    death_retired = models.BooleanField(db_column='death_retired', null= True)
    death_left_assets = models.BooleanField(db_column='death_left_assets', null= True)
    death_made_will = models.BooleanField(db_column='death_made_will', null= True)
    death_leaves_hereditary = models.BooleanField(db_column='death_leaves_hereditary', null= True)
    double_head = models.CharField(max_length=255, db_column='double_head', null=True)
    double_head_address = models.CharField(max_length=255, db_column='double_head_address', null=True)
    flowers = models.TextField(max_length=1024, db_column='flowers', null=True)
    dead_location = models.CharField(max_length=128, db_column='dead_location', null=True)
    cause_of_death = models.CharField(max_length=128, db_column='cause_of_death', null=True)
    grave_message = models.CharField(max_length=128, db_column='grave_message', null=True)

    wake_local = models.CharField(max_length=255, db_column='wake_local', null=True) 
    wake_date = models.DateField(db_column='wake_date', null=True)
    wake_time = models.TimeField(db_column='wake_time', null=True)
    leaving_mortuary_datetime = models.DateTimeField(db_column='leaving_mortuary_time', null=True)
    funeral_datetime = models.DateTimeField(db_column='funeral_datetime', null=True)
    funeral_local = models.TimeField(db_column='funeral_local', null=True)

    family_member_name = models.CharField(max_length=255, db_column='family_member_name', null=True) 
    family_member_cc = models.CharField(max_length=16, db_column='family_member_cc', null=True)
    family_member_cc_valid_until = models.DateField(db_column='family_member_cc_valid_until', null=True)
    family_member_kinship = models.CharField(max_length=64, db_column='family_member_kinship', null=True) 

    death_declaration_number = models.CharField(max_length=32, db_column='death_declaration_number', null=True) 
    


    def __str__(self):
        return self.name