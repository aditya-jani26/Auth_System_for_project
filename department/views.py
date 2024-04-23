from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
import re
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser


# =============================-RegisterView-====================================
class RegisterView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        reg_errors = self.validate_registration(request.data)
        
        if reg_errors:
            return Response({'msg': reg_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'msg': 'User has been registered Successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                reg_errors(f"Error occurred while saving user: {e}")
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_registration(self, data):
        reg_errors = []
                # Log the error for debugging
        username = data.get('username')
        print("username", username)
        email = data.get('email')
        password = data.get('password')
        User_type = data.get('user_type')
        is_active = data.get('is_active')
        is_admin = data.get('is_admin')
        
        if not username:
            reg_errors.append('Username:- is required.')
        elif not re.match(r'^[a-zA-Z0-9_.]{5,20}$', username):
            reg_errors.append('Username must be 5-20 characters long and may only contain letters, numbers, dots, or underscores.')

        if not email:
            reg_errors.append('Email:- is required.')
        elif not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            reg_errors.append('Invalid Email')

        if not password:
            reg_errors.append('Password:- is required.')
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', password):
            reg_errors.append('Password must contain at least one digit, one uppercase letter, one lowercase letter, and one special character.')
        allowed_user_types = [choice[0] for choice in CustomUser.user_typer]
        if not User_type:
            reg_errors.append('User_type is required.')
        elif User_type not in allowed_user_types:
            reg_errors.append('User_type must be one of the following options: "Admin", "Project_Manager", "Team_Leader", "Employee".')
        return reg_errors
# this is working and password stored in hash
# ============================-LoginView-=====================================
class loginView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        try:
            user = CustomUser.objects.get(username=request.data['username'])
        except CustomUser.DoesNotExist:
            return Response({'msg': 'User not found', 'status': 'error'}, status=404)

        if not check_password(request.data['password'], user.password):
            print(user.username, "user")
            return Response({'msg': 'Invalid credentials', 'status': 'warning'}, status=400)
        
        try: 
            token, created = CustomToken.objects.get_or_create(user=user)

            if created:
                # If a new token was created, generate the key
                print("eiughifgrei", token.generate_key())
                token.save()

            # Now you can access the token key from the 'token' instance
            serializer = {"username": user.username, "token": token.key}
        
        except Exception as e:
            print("Error", e)

        return Response(serializer, status=200)

# ============================================================================
        # if check_password(request.data['password'], user.password):
        #     print(user.username, "user")
        #     try: 
        #         token = CustomToken.objects.get_or_create(user=user)
        #         print(token, "token")
        #         # print(created, "created")

        #         if token:
        #             print("token ")
        #             # If a new token was created, generate the key
        #             # print("eiughifgrei", token.generate_key())
        #             # token.save()

        #         # Now you can access the token key from the 'token' instance
        #         # serializer = {"username": user.username, "token": token.key}
            
        #     except Exception as e:
        #         print("Error", e)

        #     # return Response(serializer, status=200)

        #     return Response(status=200)
        # else:
        #     return Response({'msg': 'Invalid credentials', 'status': 'warning'}, status=400)
            

    # default response
        


        
        # refresh = RefreshToken.for_user(user)
        # serializer = {
        #     'username': user.username,
        #     'token': str(refresh.access_token)

        # }
        # return Response(serializer, status=200)
    


# ==============================-Changepasswords-===================================
# class Changepasswords(APIView):
#     def post(self, request):
#         check, obj = token_auth(request)
#         print(obj,"object")
#         if not check:
#             return Response({'msg': obj}, status= 404)
#         else:
#             serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
#             print(serializer, "---->serializer<----")
            
#             if serializer.is_valid():
#                 return Response({'msg':'password changed Done'},status=status.HTTP_200_OK)
#         return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Changepasswords(APIView):
    def post(self, request):
        print(request.data, "request.data")
        check, obj = token_auth(request)
        print(obj,"object")
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ChangePasswordSerializer(data=request.data, context={'user': obj})
            print(serializer, "---->serializer<----")
            
            if serializer.is_valid():
                # Save the new password
                obj.set_password(serializer.validated_data['new_password'])
                obj.save()
                return Response({'msg': 'Password changed successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ==============================-ResetPassword-===================================
class ResetPassword(APIView):

    def post(self, request, format= None):
        serializers = ResetPasswordEmailRequestSerializer(data= request.data)
        print(serializers, 'Reset--->')
        if serializers.is_valid():
            return Response({'msg':'password Reset link send. Plase check your email inbox'},status= status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendResetPasswordEmaiView(APIView):
    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        print(serializer,'--->sendreset')
        serializer.is_valid(raise_exception=True)
        return Response({"Successful":"password reset link is sent..!"}, status=status.HTTP_200_OK)
# ==============================-=-=-=-=-=-=-=-=========================================
def token_auth(request):
    token = request.headers.get('token',None)
    if token is None:
        return False,"please provide a token"
    try:
        user = CustomToken.objects.get(key=token)
        return True,user
    except CustomToken.DoesNotExist:
        return False,"token does not valid"