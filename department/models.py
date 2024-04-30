from django.db import models
from django.core.validators import EmailValidator,MinLengthValidator,MaxLengthValidator
from .models import *
import binascii
from datetime import datetime
from django.utils import timezone   
import os

class CustomUser(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator])
    password = models.CharField(max_length=250, 
                                validators=[MaxLengthValidator(limit_value=250), 
                                            MinLengthValidator(limit_value=8,
                                                               message="Password must be at least 8 characters")])
    user_type = models.CharField(max_length=15, choices=[
        ('Admin', 'Admin'), 
        ('Project_Manager', 'Project_Manager'),
        ('Team_Leader', 'Team_Leader'),
        ('Employee', 'Employee'),
    ])

    last_login = models.DateTimeField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def get_email_field_name(self):
        return 'email'

class Project(models.Model):

    projectCreator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_by')
    assignToProject_Manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assign_to_pm')
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

class Leave(models.Model):
    EmployeeName = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, related_name='leaves_requested')
    leaveStartDate = models.DateField(default=timezone.now)
    leaveEndDate = models.DateField(null = True)
    typeOfLeave = [('full-day', 'full-day'),('half-day', 'half-day')]
    leaveType = models.CharField(max_length=100, choices=typeOfLeave ,default='full-day')
    leaveReason = models.CharField(max_length=500)
    notifyTo = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leaves_notified')
    approveLeave = models.BooleanField(default=False, null=True)
    leave_days = models.IntegerField(default=0)

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
    
class ProjectAllocation(models.Model):
    emp_allocation = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  
    allocation_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    taskName = models.CharField(max_length=100)
    taskDescription = models.CharField(max_length=500)
    taskStartDate = models.DateField(null=True)
    taskEndDate = models.DateField(null=True)
    taskStatus = models.BooleanField(default=False, null=True)
    # this will check if the emp is already on project, list total emp on a project , project & emp id 
    