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
from datetime import datetime, timedelta
from django.db.models import Sum
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
            

class TaskStatusView(APIView):

    def patch(self, request, id):
        project_allocaction = ProjectAllocation.objects.get(pk=id)
        user_name = request.user.name
        serializer = TaskStatusSerializer(project_allocaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if project_allocaction.taskStatus == True:
            response_data = {
                "Success": f"Task has been completed successfully by {user_name}.",
                "updated_data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"Pending": "Task has not completed.", "updated_data":serializer.data}, status=status.HTTP_200_OK)

# =============-allocations-==================================-allocations-==============================================-allocations-====================
class Projectallocations(APIView):

    def post(self, request):
        check,obj = token_auth(request)
        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProjectAllocationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"Success": "Project allocation successful.", "allocation": serializer.data},
                    status=status.HTTP_201_CREATED)

class employeesallocations(APIView):

    def get(self, request):
    
        check,obj = token_auth(request)
        if check:
            employees = CustomUser.objects.filter(user_type='Employee')
            serializer = EmployeeListSerializer(employees, many=True)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)

# =============================================================================================================================

class Levetaken(APIView):
    def post(self, request):
        check, obj = token_auth(self.request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            start_date_str = request.data.get('leaveStartDate')
            end_date_str = request.data.get('leaveEndDate')

            if start_date_str is None or end_date_str is None:
                return Response({'error': 'Leave start date or end date is missing'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Convert string dates to datetime objects
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        # i need to put error message for handling the exception if  exception in e  

            # Calculate total leave days
        mutable_data = request.data.copy()
        
        # Calculate total leave days and add it to the request data
        total_leave_days = (end_date - start_date).days + 1
        mutable_data['leave_days'] = total_leave_days

        # Add empName to the request data
        mutable_data['empName'] = request.user.id

        # Serialize and save leave request
        serializer = LeavetakenSerializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class leaveapproved(APIView):

    def patch(self,request, id):
        check, obj = token_auth(self.request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            leave = Leave.objects.get(pk=id)
            serializer = ApproveLeavetSerializer(leave, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if leave.approveLeave == True:
                response_data = {   
                    "Success": "Leave has been granted...",
                    "updated_data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"Success": "Leave has been rejected!!!", "updated_data":serializer.data}, status=status.HTTP_200_OK)

class LeaveList(ListAPIView):

    queryset = Leave.objects.all()
    serializer_class = LeavelListSerializer

    def get_queryset(self):
        check, obj = token_auth(self.request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        elif check:
            user = self.request.user
            if user:
                return Leave.objects.all()
        else:
            return Response({'msg': obj})


# class salary(APIView):

#     def post(self, request):
#         check, obj = token_auth(self.request)

#         if not check:
#             return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        
#         else:
#             username = request.data.get('username')
#             print("user",username)




#             provided_salary_amount = float(request.data.get('amount'))
#             # =============
            
#             emp = Leave.objects.filter(empName__id=username)


#             # ....
#             print("emp",emp)

#             # Get the total approved leave days for the user
#             # total_leave_days = user.leaves_requested.filter(approveLeave=True).aggregate(total_leave_days=models.Sum('leaveDays'))['total_leave_days'] or 0
#             total_leave_days = Leave.objects.filter(empName=username, approveLeave=True).aggregate(total_leave_days=Sum('leave_days'))['total_leave_days']
#             print("total_leave_days", total_leave_days)  
#             # Calculate the remaining working days after deducting leave days
#             remaining_working_days = 21 - total_leave_days

#             # Calculate the total salary percentage based on remaining working days
#             total_salary_percentage = (remaining_working_days / 21) * 100

#             # Get the user's default salary percentage
#             default_salary_percentage = 100

#             # Determine the actual salary percentage to be used
#             actual_salary_percentage = min(default_salary_percentage, total_salary_percentage)

#             # Calculate the salary amount based on the actual salary percentage
#             salary_amount = (actual_salary_percentage / 100) * provided_salary_amount
#             print("salary_amount",salary_amount)
#             amount = int(salary_amount)
#             # Save the salary payment information
#             serializer = SalaryPaymentSerializer(data={'user': username, 'amount': amount, 'payment_method': request.data.get('payment_method')})
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#add permission class so that only admin can access this class (project list)
    # admin can approve leave of pm and tl also admin can not take leave  
        # admin can create project 
        # only pm and tl can do CRUD operations 
        # employees can take leave can send request to pl
        # permissions class ==>  admin can list all projects
                            # ==> admin and pl and tl can create  project 
                                # ==> tl can assign project to pl 
                                    #==> pl can assign the project to emp
                                        # ==> here one emp can only work on new project if that emp is not associated to projects 100% of his time
# permission class ==> 

class salary(APIView):
    def post(self, request):
        check, obj = token_auth(self.request)

        if not check:
            return Response({'msg': obj}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            username = request.data.get('username')
            provided_salary_amount = request.data.get('amount')
            if username and provided_salary_amount is True :
            # Fetch employee leave data
                emp = Leave.objects.filter(empName=username)
                print("emp", emp)

                # Get the total approved leave days for the user
                total_leave_days = Leave.objects.filter(empName=username, approveLeave=True).aggregate(total_leave_days=Sum('leave_days'))['total_leave_days']
                print("total_leave_days", total_leave_days)

                # If total_leave_days is None, set it to 0
                total_leave_days = total_leave_days or 0

                # Calculate the remaining working days after deducting leave days
                remaining_working_days = 21 - total_leave_days

                # Calculate the total salary percentage based on remaining working days
                if total_leave_days == 0:
                    total_salary_percentage = 100  # 100% salary if no leaves
                else:
                    total_salary_percentage = (remaining_working_days / 21) * 100

                # Get the user's default salary percentage
                default_salary_percentage = 100

                # Determine the actual salary percentage to be used
                actual_salary_percentage = min(default_salary_percentage, total_salary_percentage)

                # Calculate the salary amount based on the actual salary percentage
                salary_amount = (actual_salary_percentage / 100) * provided_salary_amount
                print("salary_amount", salary_amount)
                amount = int(salary_amount)

                # Save the salary payment information
                serializer = SalaryPaymentSerializer(data={'user': username, 'amount': amount})
                print(serializer,'serializer')

                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
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