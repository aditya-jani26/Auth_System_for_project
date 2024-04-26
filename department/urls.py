from django.urls import path
from department.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login', loginView.as_view(), name="LoginView"),
    path('change_password', ChangePasswords.as_view(), name="Changepasswords"),
    path('reset_password', ResetPassword.as_view(), name="ResetPassword"),
    path('SendEmail',SendResetPasswordEmaiView.as_view(), name="SendResetPasswordEmaiView"),
    path("project_List",ProjectList.as_view(), name="ProjectListView"),
    path("project_create",projectCreateView.as_view(), name="ProjectCreateView"),
    path("projectCRUD/<int:id>",ProjectCRUDView.as_view(), name="ProjectCRUDView"),
    # path("LeaveList",LeaveList.as_view(), name="LeaveList"),
]