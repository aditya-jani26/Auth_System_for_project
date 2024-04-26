from warnings import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from department.permissions import *
from .serializers import *
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
from rest_framework.generics import ListAPIView
# import django_filters.rest_framework
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.permissions import IsAdminUser
from django.core.mail import send_mail

# ===============================================-RegisterView-==========================================

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
# with this i can send all error messages so that user can get txt after runing the code
    def validate_registration(self, data):
            errors = {}           
            if CustomUser.objects.filter(username=data.get('username')).exists():
                errors['username'] = 'This username is already in use.'
            return errors
# this is working and password stored in hash
    
# ==============================================-LoginView-====================================================
# when the user is logged in Token should be creaded
    
class loginView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            user = CustomUser.objects.get(username=request.data['username'])
        except CustomUser.DoesNotExist:
            return Response({'msg': 'User not found', 'status': 'error'}, status=404)

        if check_password(request.data['password'], user.password):
                token, created = CustomToken.objects.get_or_create(user=user)
                if created:
                    # If a new token was created, generate the key
                    token.generate_key()
                    token.save()
                # Now you can access the token key from the 'token' instance
                serializer = {"username": user.username, "token": token.key}
                return Response(serializer, status=status.HTTP_200_OK)
        else:
            return Response({'msg':'ckeck your password before you enter', status:'wrong'}, status=404)
            
# this is working just need to check how can i register the tocken as it might not work so moving on to creat new function 

# ===========================================-Changepasswords-=========================================
# Here the password will change on API level
        
class ChangePasswords(APIView):

    def post(self, request):
        check, obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                user = obj.user  # Access the associated CustomUser
                new_password = serializer.validated_data['password']
                user.password = new_password
                user.save()
                return Response({'msg': 'Password changed successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# working till here full and final solution.
        
# ===============================================-ResetPassword-==============================================
# here we reset the password will work on Email base 
        
class ResetPassword(APIView):
    
    def post(self, request, format= None):
        check, obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializers = ResetPasswordEmailRequestSerializer(data= request.data)
            print(serializers, 'Reset--->')
            if serializers.is_valid():
                return Response({'msg':'password Reset link send. Plase check your email inbox'},status= status.HTTP_200_OK)

class SendResetPasswordEmaiView(APIView):

    def post(self, request):
        check, obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SendResetPasswordEmailSerializer(data=request.data)
            print(serializer,'--->sendreset')
            serializer.is_valid(raise_exception=True)
        return Response({"Successful":"password reset link is sent..!"}, status=status.HTTP_200_OK)

# =============-token_auth-=================-=-=-=-=-=-=-=-================================-token_auth-=========
    
def token_auth(request):

    token = request.headers.get('token',None)

    if token is None:
        return False,"please provide a token"
    try:
        user = CustomToken.objects.get(key=token)
        return True,user
    except CustomToken.DoesNotExist:
        return False,"token does not valid"

#==================================================-ProjectList-====================================================
class ProjectList(ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        check, obj = token_auth(self.request)
        print(obj)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        elif check:
            user = self.request.user
            if user:
                return Project.objects.all()
        else:
            return Response({'msg': obj})

        #from this list Api the use can only be able to View list of projects
# ===-project-===========================================================-projectCreateView-===============================-project-=========

class projectCreateView(APIView):

    def post(self, request):
        check, obj = token_auth(request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProjectCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)   
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ===-project-=========================================================-ProjectCRUDView-========================================-project-============
    
# this is use to do delte and update in any project here i have used 2 def function through which project can be deleted and updated

class ProjectCRUDView(APIView):

    def patch(self, request, id):
        check, obj = token_auth(request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                project = Project.objects.get(pk=id)
                serializer = ProjectCRUDSerializer(project, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"Success": "Changes updated successfully.", "updated_data":serializer.data}, status=status.HTTP_200_OK)
            except Project.DoesNotExist:
             return Response({"error": "Project does not exists."},status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        check, obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                project = Project.objects.get(pk=id)    
                project.delete()
                return Response({"success": "Project deleted successfully."},status=status.HTTP_204_NO_CONTENT)
            except Project.DoesNotExist:
                return Response({"error": "Project does not exists."},status=status.HTTP_404_NOT_FOUND)

# =================================================================================================================
class Projectallocations(APIView):

    def post(self, request):
        check,obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProjectallocationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"Success": "Project allocation successful.", "allocation": serializer.data},
                        status=status.HTTP_201_CREATED)

# =============================================================================================================================

class EmployeeAllocationListView(APIView):

    def get(self, request):
        if check:
            check,obj = token_auth(request)
            employees = CustomUser.objects.filter(userType="Employee")
            serializer = EmployeeListSerializer(employees, many=True)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
    

# add leave management system:

# class LeaveList(ListAPIView):
#     queryset = Leave.objects.all()
#     serializer_class = LeaveListSerializer

#     def get_queryset(self):
#         check, obj = token_auth(self.request)
#         print(obj)
#         if not check:
#             return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
#         elif check:
#             user = self.request.user
#             if user:
#                 return Leave.objects.all()
#         else:
#             return Response({'msg': obj})


