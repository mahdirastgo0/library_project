from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, logout, login as auth_login
from django.contrib import messages
from .forms import UserChangeForm
from accounts.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from .utils import generate_token, verify_token, send_verification_email
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if User.objects.filter(username=username).exists():
            messages.error(request, "username Already Registered!!")
            return redirect('accounts:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('accounts:register')

        if username is None or len(username) > 20:
            messages.error(request, "Username must be under 20 characters!!")
            return redirect('accounts:register')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('accounts:register')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('accounts:register')

        myuser = User.objects.create_user(username=username,email=email, password=pass1)
        myuser.save()
        messages.success(request, "Registration successful! Please check your email to verify your account.")
        return redirect("accounts:login")

        token = generate_token(email)

        # Send the verification email
        subject = "Verify Your Email"
        verification_url = f"http://{request.get_host()}/verify-email/{token}/"
        html_message = render_to_string('accounts/verification_email.html', {'verification_url': verification_url})
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)

        return redirect("accounts:login")


    return render(request, "accounts/register.html")




def user_login(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email")
        password = request.POST.get("password")

        # Check if the input is an email or username
        try:
            validate_email(username_or_email)
            is_email = True
        except ValidationError:
            is_email = False

        # Authenticate the user
        if is_email:
            user = authenticate(request, email=username_or_email, password=password)
        else:
            user = authenticate(request, username=username_or_email, password=password)


        if user is not None:
            if user.is_verified:
                auth_login(request, user)  # Log the user in
                return redirect("library:home")  # Redirect to home page after successful login
            else:
                messages.error(request, "Your account is not verified. Please check your email.")
                return render(request, "accounts/login.html", {'resend_verification': True, 'email': user.email})
        else:
            messages.error(request, "Invalid username/email or password")
            return redirect("accounts:login")

    # If the request method is not POST, render the login page
    return render(request, "accounts/login.html")


def custom_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("library:home")




def profile(request, email):
    if request.method == "POST":
        user = get_object_or_404(User, email=email)
        form = UserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("profile", email=user_form.email)

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.filter(email=email).first()
    if user:
        form = UserChangeForm(instance=user)
        return render(
            request=request,
            template_name="accounts/profile.html",
            context={'user': user, 'form': form}
        )

    return redirect("accounts/profile.html", user_form.email)


def best_selling_books(request):
    best_sellers = Book.objects.filter(status="sold").order_by("-price")[:5]

    return render(request, "books/best_sellers.html", {"best_sellers": best_sellers})

def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except Exception:
        return None


def verify_email(request, token):
    print("Entering verify_email view")  # Debugging
    print(f"Token: {token}")  # Debugging

    email = verify_token(token)
    print(f"Email: {email}")  # Debugging

    if email is None:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("accounts:login")

    try:
        user = User.objects.get(email=email)
        print(f"User: {user}")  # Debugging
        if user.is_verified:
            messages.warning(request, "Your account is already verified.")
        else:
            user.is_verified = True
            user.is_active = True  # Activate the user
            user.save()
            messages.success(request, "Email verified successfully! You can now log in.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect("accounts:login")

def resend_verification(request, email):
    try:
        user = User.objects.get(email=email)
        if user.is_verified:
            messages.warning(request, "Your account is already verified.")
        else:
            send_verification_email(user)  # Send the verification email
            messages.success(request, "Verification email sent. Please check your inbox.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect("accounts:login")




