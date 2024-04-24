from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from department.permissions import *
from .serializers import *
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
import re
from rest_framework.permissions import IsAuthenticated
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
# with this i can send all error messages so that user can get notified after runing the code
    def validate_registration(self, data):
            errors = {}           
            if CustomUser.objects.filter(username=data.get('username')).exists():
                errors['username'] = 'This username is already in use.'
            
            return errors
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
            return Response({'msg': 'Invalid credentials', 'status': 'warning'}, status=400)
        try: 
            token, created = CustomToken.objects.get_or_create(user=user)
            if created:
                # If a new token was created, generate the key
                token.generate_key()
                token.save()
            # Now you can access the token key from the 'token' instance
            serializer = {"username": user.username, "token": token.key}
            return Response(serializer, status=200)
        except Exception as e:
            print("Error", e)
            return Response("error!!!", status=501)
# this is working just need to check how can i register the tocken as it might not work so moving on to creat new function 

# =============================-Changepasswords-=====================================
        
class ChangePasswords(APIView):
    def post(self, request):
        check, obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                user = obj.user  # Access the associated CustomUser
                new_password = serializer.validated_data['confirm_password']
                user.password = new_password
                user.save()
                return Response({'msg': 'Password changed successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ==============================-ResetPassword-===================================
# class ResetPassword(APIView):
#     def post(self, request, format= None):
#         serializers = ResetPasswordEmailRequestSerializer(data= request.data)
#         print(serializers, 'Reset--->')
#         if serializers.is_valid():
#             return Response({'msg':'password Reset link send. Plase check your email inbox'},status= status.HTTP_200_OK)
#         return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class SendResetPasswordEmaiView(APIView):
#     def post(self, request):
#         serializer = SendResetPasswordEmailSerializer(data=request.data)
#         print(serializer,'--->sendreset')
#         serializer.is_valid(raise_exception=True)
#         return Response({"Successful":"password reset link is sent..!"}, status=status.HTTP_200_OK)

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
    #   =   =   = = = = = ==    == ====     ==  
    # here the problem is that this is trying to acces the reques.user 
