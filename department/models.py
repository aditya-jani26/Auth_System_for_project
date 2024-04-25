from django.db import models
from django.core.validators import EmailValidator,MinLengthValidator,MaxLengthValidator
from .models import *
import binascii
from datetime import datetime   

import os

class CustomUser(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator])
    password = models.CharField(max_length=250, 
                                validators=[MaxLengthValidator(limit_value=250), 
                                            MinLengthValidator(limit_value=8, 
                                                               message="Password must be at least 8 characters")])
    is_active = models.BooleanField(default=True)
    user_typer=[
        ('Admin', 'Admin'), 
        ('Project_Manager', 'Project_Manager'),
        ('Team_Leader', 'Team_Leader'),
        ('Employee', 'Employee'),
    ]
    is_admin = models.BooleanField(default=False) 

class Project(models.Model):
# is it  like only the admin can create a project
    # and at time he can assign it to the PM with "it'es PK".
    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_by')
    # assignToProject_Manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  related_name='assign_to_pm')
    # have done changes here
    project_id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=50)
    projectDescription = models.CharField(max_length=500)
    projectStartDate = models.DateField(null = False)

    projectEndDate = models.DateField(null=True)
    todoChoices = [
                ('In progress', 'In progress'),
                ('Completed', 'Completed'),
                
            ]
    projectStatus = models.CharField(max_length=100,null = True, choices=todoChoices)

class CustomToken(models.Model):

    key = models.CharField(max_length=40)
    user = models.OneToOneField(CustomUser, related_name='custom_token', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now())
    
    def generate_key(self):
        self.key = binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.key
