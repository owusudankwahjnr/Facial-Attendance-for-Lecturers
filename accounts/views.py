import base64
import os
from io import BytesIO
import joblib
from deepface import DeepFace
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from PIL import Image
from django.views import View

from .face_training import train_and_save_model
# from .forms import CustomUserCreationForm

def register(request):
    # if request.method == 'POST':
    #     form = CustomUserCreationForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('login')
    # else:
    #     form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': ''})

def custom_logout_view(request):
    request.user.face_verified = False
    request.user.save()
    logout(request)  # This clears the session
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Change this to your desired redirect URL name


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            user.face_verified = False
            return redirect('dashboard')  # Change 'home' to your desired redirect page
        else:
            messages.error(request, 'Invalid login credentials')
    return render(request, 'accounts/login.html')


@login_required
def upload_training_images_view(request):
    """
    Render the face training page with camera.
    """
    context = {
        'redirect_url': reverse('train_model_view')
    }
    return render(request, 'accounts/upload_training_images.html', context)

@login_required
@csrf_exempt
@require_POST
def submit_training_data(request):
    import json
    data = json.loads(request.body)
    images = data.get('images', [])
    user = request.user
    user_dir = os.path.join(settings.MEDIA_ROOT, f"user_faces/{user.id}/")
    os.makedirs(user_dir, exist_ok=True)

    for i, img_data in enumerate(images):
        try:
            img_str = img_data.split(",")[1]  # strip "data:image/jpeg;base64,"
            img_bytes = base64.b64decode(img_str)
            img_path = os.path.join(user_dir, f"{user.id}_{i}.jpg")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"status": "success"})


@csrf_exempt
@require_POST
@login_required
def trigger_face_training(request):
    try:
        train_and_save_model(request.user)
        return JsonResponse({"success": True, "message": "Model trained successfully."})
    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"}, status=500)



def train_model_view(request):
    context = {
        'redirect_url': reverse('train_model_view')
    }
    return render(request, 'accounts/train.html')


@method_decorator(csrf_exempt, name='dispatch')
class FaceVerifyAPI(View):

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"verified": False, "error": "Unauthorized"}, status=401)

        img_data = request.POST.get("image")
        if not img_data:
            return JsonResponse({"verified": False, "error": "No image"}, status=400)

        # Decode base64 image
        try:
            content = img_data.split(',')[1]
            img_bytes = base64.b64decode(content)
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            img_path = os.path.join(settings.MEDIA_ROOT, f"temp_{user.id}.jpg")
            img.save(img_path)
        except Exception as e:
            return JsonResponse({"verified": False, "error": "Invalid image"}, status=400)

        # Load model
        model_path = os.path.join(settings.BASE_DIR, f"models/user_models/{user.id}/classifier.joblib")
        if not os.path.exists(model_path):
            return JsonResponse({"verified": False, "error": "No trained model found"}, status=404)

        try:
            model = joblib.load(model_path)
            embedding = DeepFace.represent(img_path=img_path, model_name="Facenet", enforce_detection=False)[0]['embedding']
            prediction = model.predict([embedding])[0]
            user.face_verified = bool(prediction)
            user.save()
            return JsonResponse({"verified": bool(prediction)})
        except Exception as e:
            return JsonResponse({"verified": False, "error": str(e)})
