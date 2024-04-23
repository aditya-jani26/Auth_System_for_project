from django.db import models
from django.utils.timezone import now
from django.core.validators import EmailValidator,MinLengthValidator,MaxLengthValidator
from .models import *
import binascii
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os
class CustomUser(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator])
    password = models.CharField(max_length=250, 
                                validators=[MaxLengthValidator(limit_value=250), 
                                            MinLengthValidator(limit_value=8, 
                                                               message="Password must be at least 8 characters")])
    is_active = models.BooleanField(default=True)
    confirm_password = models.CharField(max_length=250, 
                                validators=[MaxLengthValidator(limit_value=250), 
                                            MinLengthValidator(limit_value=8, 
                                            message="Password must be at least 8 characters")
                                            ])
    user_typer=[
        ('Admin', 'Admin'), 
        ('Project_Manager', 'Project_Manager'),
        ('Team_Leader', 'Team_Leader'),
        ('Employee', 'Employee'),
    ]
    is_admin = models.BooleanField(default=False) 

class Project(models.Model):
    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='created_by')

    assignToProject_Manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='assign_to_pm')
    # have done changes here
    project_id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=50)
    projectDescription = models.CharField(max_length=500)
    projectStartDate = models.DateField(default=now)
    projectEndDate = models.DateField(null=True)
    todoChoices = [
        ('In progress', 'In progress'),
        ('Completed', 'Completed'),
    ]
    projectStatus = models.CharField(max_length=100, choices=todoChoices)



# example for tocken

class CustomToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(CustomUser, related_name='custom_token', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    def generate_key(self):
        self.key = binascii.hexlify(os.urandom(20)).decode()
        print("key ", self.key)

    def save(self, *args, **kwargs):
        if self.key:
            self.key = self.generate_key()
            print("key/// ", self.key)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.key
