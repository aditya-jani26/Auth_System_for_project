from django.urls import path
from department.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('loginView', loginView.as_view(), name="LoginView"),
    path('changepassword', Changepasswords.as_view(), name="Changepasswords"),
    path('resetpassword', ResetPassword.as_view(), name="ResetPassword"),
    path('SendEmail',SendResetPasswordEmaiView.as_view(), name="SendResetPasswordEmaiView"),


]
