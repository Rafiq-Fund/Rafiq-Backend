import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site

def generate_activation_jwt(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "type": "activation"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def send_activation_email(user, request):
    token = generate_activation_jwt(user)
   
    # Build activation URL
    activation_url = f"{settings.RAFIQ_URL}/email-verified/{token}"
    
    # Email content
    subject = "Welcome to Rafiq - Activate Your Account"
    
    # Context for HTML template
    context = {
        'user': user,
        'activation_url': activation_url,
        'support_email': 'support@rafiq.com',
        'expiry_hours': 24,  # Token expiry time
    }
    
    # Render HTML and plain text versions
    html_content = render_to_string('emails/account_activation.html', context)
    text_content = strip_tags(html_content)
    
    # Create and send email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        reply_to=[settings.EMAIL_HOST_USER],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Add headers for better email deliverability
    email.extra_headers = {
        'X-Priority': '1',  # High priority
        'X-MC-Tags': 'account-activation',
    }
    
    email.send()
    
def generate_password_reset_jwt(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "type": "password_reset"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def send_password_reset_email(user, request):
    token = generate_password_reset_jwt(user)
    
    # Build reset URL with token for security
    current_site = get_current_site(request)
    reset_url = f"{settings.RAFIQ_URL}/reset-password/{token}/"
    
    # Email context
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': current_site.name,
        'support_email': 'support@rafiq.com',
        'expiry_hours': 24,
    }
    
    # Render HTML and plain text versions
    html_content = render_to_string('emails/password_reset.html', context)
    text_content = strip_tags(html_content)
    
    # Create email
    email = EmailMultiAlternatives(
        subject="Password Reset Instructions for Your Rafiq Account",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.EMAIL_HOST_USER],
    )
    email.attach_alternative(html_content, "text/html")
    
    # Add headers for better email deliverability
    email.extra_headers = {
        'X-Priority': '1',  # High priority
        'X-MC-Tags': 'password-reset',
    }
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        # Log the error
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(f"Failed to send password reset email: {str(e)}")