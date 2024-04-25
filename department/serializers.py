
from rest_framework import serializers
from rest_framework.fields import empty
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
class ChangePasswordSerializer(serializers.Serializer):
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

    def validate(self, data):
        email = data.get('email')
        user_queryset = CustomUser.objects.filter(email=email)
        if user_queryset.exists():
            user = user_queryset.first()  # Get the first user in queryset
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded id", user_id)
            token = PasswordResetTokenGenerator().make_token(user)
            print("password reset token", token)
            link = 'http://localhost:3000/api/reset/'+user_id+'/'+token
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
# not-working
class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'
# almost
class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }
# almost-working
class ProjectCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model: Project
        fields = '__all__'