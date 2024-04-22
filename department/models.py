from django.db import models
from django.utils.timezone import now
from django.core.validators import EmailValidator,MinLengthValidator,MaxLengthValidator

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
    assignToPM = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='assign_to_pm')
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