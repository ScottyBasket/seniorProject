from django.urls import path

from . import views


urlpatterns = [
    path("emailCode/", views.EmailCodeView.as_view(), name="emailCode"),    
    path("signup/", views.SignUpView.as_view(), name="sign_up"),
    path("verifyCode/", views.VerifyCodeView.as_view(), name="verify_code"),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('forgotpassword/', views.ForgotPasswordView.as_view(), name='forgotpassword'),
    path('message/<str:code>/', views.MessageView.as_view(), name='message'),
    path('mail/', views.MailView.as_view(), name='mail'),
]