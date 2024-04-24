from django.urls import path
from department.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('loginView', loginView.as_view(), name="LoginView"),
    path('changepassword', ChangePasswords.as_view(), name="Changepasswords"),
    # path('resetpassword', ResetPassword.as_view(), name="ResetPassword"),
    # path('SendEmail',SendResetPasswordEmaiView.as_view(), name="SendResetPasswordEmaiView"),
    # path("projectCreateView",projectCreateView.as_view(), name="ProjectCreateView"),
    # path("ProjectListView",ProjectListView.as_view(), name="ProjectListView"),
    # path("ProjectCRUDView/<int:id>",ProjectCRUDView.as_view(), name="ProjectCRUDView"),




]
