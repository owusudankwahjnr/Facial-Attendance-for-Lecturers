from django.urls import path
from django.views.generic import TemplateView

from . import views



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),

    path("upload-training-images/", views.upload_training_images_view, name="upload-training-images"),
    path("submit-training-data/", views.submit_training_data, name="submit_training_data"),
    path('api/train-model/', views.trigger_face_training, name='train_model'),
    path('train-model/', views.train_model_view, name='train_model_view'),
    path("verify-face/", TemplateView.as_view(template_name="accounts/verify_face.html"), name="verify_face_page"),
    path("verify-face-api/", views.FaceVerifyAPI.as_view(), name="verify_face_api"),
]
