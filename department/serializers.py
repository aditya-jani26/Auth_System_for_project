from rest_framework import serializers
from .models import *
from rest_framework import serializers
from department.Utils import Utils
from .models import CustomUser,Project
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password


# working
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def __init__(self, instance=None, data=..., **kwargs):
        try:
            data = data.copy()
            data['password'] = make_password(data['password'])
        except:
            pass
        super().__init__(instance, data, **kwargs)
# working
class ChangePasswordSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=True)

    def save(self, **kwargs):
        user = self.context['request'].user  # Get the user from the request
        password = self.validated_data['password']

        # Set password directly to the password field
        user.password = password
        user.save()
        return user
    def __init__(self, instance=None, data=..., **kwargs):
        # this init is used as i wasnt to encript the password field even i change the password field through API.
        try:
            data = data.copy()
            data['password'] = make_password(data['password'])
        except:
            pass
        super().__init__(instance, data, **kwargs)

# working
    
class ResetPasswordEmailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields  = ['email']
    # through this it is said that when we run this API the request Fields will be only EMAIL fields

    def validate(self, data):
        email = data.get('email')
        # AS soon as we get here iit will check if the email data which we got from the user itself is valid of not.
        user_queryset = CustomUser.objects.filter(email=email)
        # this will get the email and chek is the email which is given is within the current database with the fillter method.
        if user_queryset.exists():
            # if the variable is at . exists then it will move into this variable
            user = user_queryset.first()  # Get the first user in queryset
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            # this is used to encript the user id
            print("Encoded id", user_id)
            token = PasswordResetTokenGenerator().make_token(user)
            # the token will be genrated when the for the first user.
            print("password reset token", token)
            link = 'http://localhost:3000/api/reset/'+user_id+'/'+token
            # here is the link that will be in the Email Address
            print("password reset link", link)
            body = 'Click following link to reset password ' + link
            email_data =  {'subject':'Reset Your Password', 'body':body, 'to_email':user.email}
            Utils.send_email(email_data)
            return data
        else:
            raise serializers.ValidationError({'INVALID EMAIL': 'Email does not exist'})
        
class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        email = data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded id", user_id)
            token = PasswordResetTokenGenerator().make_token(user)
            print("password reset token", token)
            link = 'http://localhost:3000/api/reset/'+user_id+'/'+token
            print("password reset link", link)
            body = 'Click following link to reset password ' + link
            email_data =  {'subject':'Reset Your Password', 'body':body, 'to_email':user.email}
            print("email_data",email_data)
            Utils.send_email(email_data)
            return email_data

        else:
            raise serializers.ValidationError({'INVALID_EMAIL': 'Email does not exist'})
#working
class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
#working
class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            'user': {'write_only': True}
        }
#working
class ProjectCRUDSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
#working
class ProjectAllocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectAllocation
        fields = "__all__"

    def validate(self, data):
        emp_allocation = data.get('emp_allocation')
        project = data.get('project')

        # Check if the project is already assigned to the user
        if ProjectAllocation.objects.filter(emp_allocation=emp_allocation, project=project).exists():
            raise serializers.ValidationError("This project is already assigned to the user.")
        return data
    def create(self, validated_data):
        allocation_percentage = validated_data.get('allocation_percentage', None)
        emp_allocation = validated_data.get('emp_allocation')
        
        total_allocation_percentage = ProjectAllocation.objects.filter(emp_allocation=emp_allocation).aggregate(total_allocation=models.Sum('allocation_percentage'))['total_allocation'] or 0
        remaining_percentage = 100 - total_allocation_percentage
        
        if allocation_percentage is not None and allocation_percentage > remaining_percentage:
            raise serializers.ValidationError("The allocation percentage exceeds the remaining percentage.")

        if allocation_percentage is not None:
            emp_allocation.allocation_percentage = total_allocation_percentage + allocation_percentage
            emp_allocation.save()
        
        return ProjectAllocation.objects.create(**validated_data)

#working
class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
class LeavelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"

#working
class ProjectAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAllocation
        fields = "__all__"

    def validate(self, data):
        emp_allocation = data.get('emp_allocation')
        project = data.get('project')

        # Check if the project is already assigned to the user
        if ProjectAllocation.objects.filter(emp_allocation=emp_allocation, project=project).exists():
            raise serializers.ValidationError("This project is already assigned to the user.")
        return data

    def create(self, validated_data):
        allocation_percentage = validated_data.get('allocation_percentage', None)
        emp_allocation = validated_data.get('emp_allocation')
        
        total_allocation_percentage = ProjectAllocation.objects.filter(emp_allocation=emp_allocation).aggregate(total_allocation=models.Sum('allocation_percentage'))['total_allocation'] or 0
        remaining_percentage = 100 - total_allocation_percentage
        
        if allocation_percentage is not None and allocation_percentage > remaining_percentage:
            raise serializers.ValidationError("The allocation percentage exceeds the remaining percentage.")

        if allocation_percentage is not None:
            emp_allocation.allocation_percentage = total_allocation_percentage + allocation_percentage
            emp_allocation.save()
        
        return ProjectAllocation.objects.create(**validated_data)

#working
class ProjectInfoSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    class Meta:
        model = ProjectAllocation
        fields = ('project_name', 'allocation_percentage')

    def get_project_name(self, obj):

        return obj.Project.projectName
#working
class EmployeeAllocationListSerializer(serializers.ModelSerializer):
    projects = ProjectInfoSerializer(source='projectallocation_set', many=True, read_only=True)
    total_allocation_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'projects', 'allocation_percentage', 'total_allocation_percentage')

    def get_total_allocation_percentage(self, obj):
        total_allocation = sum([allocation.allocation_percentage for allocation in obj.projectallocation_set.all()])
        return total_allocation
    
class LeavetakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        
class ApproveLeavetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ('approveLeave')

class SalarySerializers(serializers.ModelSerializer):
    class meta:
        model = Salary
        field = ('amount','transaction_id')

class SalaryPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Salary
        fields = ['user', 'amount']  # Include 'user' field in the serializer
# =====>
# how can i max use this serializer????????