
import secrets
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

from .models import User, EmailOTP
from .forms import PortalRegistrationForm, PortalOTPVerificationForm, PortalLoginForm


# HOME
def home(request):
    return render(request, 'accounts/home.html')


# PORTAL REGISTRATION
def portal_register(request):
    if request.user.is_authenticated:
        return redirect('portal-dashboard')

    if request.method == 'POST':
        form = PortalRegistrationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(name=form.cleaned_data['name'], email=form.cleaned_data['email'], phone=form.cleaned_data['phone'], password=form.cleaned_data['password'], role=form.cleaned_data['role'], is_active=False, is_email_verified=False)

                    otp = str(secrets.randbelow(900000) + 100000)
                    otp_obj = EmailOTP(user=user, expires_at=timezone.now() + timedelta(minutes=5))
                    otp_obj.set_otp(otp)
                    otp_obj.save()

                    send_mail(subject="Inventory Portal Email Verification OTP", message=f"Hello {user.name},\n\nYour verification OTP is {otp}.\nIt expires in 5 minutes.", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], fail_silently=False)

                request.session['pending_verification_email'] = user.email
                messages.success(request, "Registration successful. Please verify your email.")
                return redirect('portal-verify-otp')

            except Exception:
                messages.error(request, "Registration failed. Please try again.")
    else:
        form = PortalRegistrationForm()

    return render(request, 'accounts/portal_register.html', {'form': form})


# PORTAL OTP VERIFICATION
def portal_verify_otp(request):
    initial_email = request.session.get('pending_verification_email', '')

    if request.method == 'POST':
        form = PortalOTPVerificationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            otp = form.cleaned_data['otp'].strip()

            try:
                with transaction.atomic():
                    user = User.objects.select_for_update().filter(email__iexact=email).first()

                    if not user:
                        form.add_error('email', 'User not found.')
                    elif user.is_email_verified:
                        form.add_error(None, 'Email is already verified.')
                    else:
                        otp_obj = EmailOTP.objects.select_for_update().filter(user=user, is_used=False).order_by('-created_at').first()

                        if not otp_obj:
                            form.add_error(None, 'OTP not found. Please register again.')
                        elif not otp_obj.verify_otp(otp):
                            form.add_error('otp', 'Invalid or expired OTP.')
                        else:
                            otp_obj.is_used = True
                            otp_obj.save(update_fields=['is_used'])
                            EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

                            user.is_email_verified = True
                            user.is_active = True
                            user.save(update_fields=['is_email_verified', 'is_active'])

                            request.session.pop('pending_verification_email', None)
                            messages.success(request, "Email verified successfully. Please login.")
                            return redirect('portal-login')

            except Exception:
                form.add_error(None, 'Verification failed. Please try again.')
    else:
        form = PortalOTPVerificationForm(initial={'email': initial_email})

    return render(request, 'accounts/portal_verify_otp.html', {'form': form})


# PORTAL LOGIN
def portal_login(request):
    if request.user.is_authenticated:
        return redirect('portal-dashboard')

    if request.method == 'POST':
        form = PortalLoginForm(request.POST, request=request)

        if form.is_valid():
            user = form.cleaned_data['user']

            if user.is_superuser or user.role == User.Role.ADMIN:
                messages.error(request, "Admin accounts must use Django Admin.")
                return redirect('portal-login')

            if user.role not in [User.Role.STORE_MANAGER, User.Role.INVENTORY_STAFF]:
                messages.error(request, "You are not authorized to access this portal.")
                return redirect('portal-login')

            login(request, user)

            next_url = request.POST.get('next')

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)

            return redirect('portal-dashboard')
    else:
        form = PortalLoginForm(request=request)

    return render(request, 'accounts/portal_login.html', {'form': form})


# PORTAL LOGOUT
@require_POST
@login_required(login_url='portal-login')
def portal_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('portal-login')


# ROLE-BASED PORTAL DASHBOARD
@login_required(login_url='portal-login')
def portal_dashboard(request):
    user = request.user

    if user.is_superuser or user.role == User.Role.ADMIN:
        return redirect('/admin/')

    if user.role == User.Role.STORE_MANAGER:
        return render(request, 'accounts/store_manager_dashboard.html', {'user': user, 'role': 'Store Manager'})

    elif user.role == User.Role.INVENTORY_STAFF:
        return render(request, 'accounts/inventory_staff_dashboard.html', {'user': user, 'role': 'Inventory Staff'})

    logout(request)
    messages.error(request, "Your account does not have portal access.")
    return redirect('portal-login')


# STORE MANAGER DASHBOARD
@login_required(login_url='portal-login')
def store_manager_dashboard(request):
    if request.user.role != User.Role.STORE_MANAGER:
        return redirect('portal-dashboard')

    return render(request, 'accounts/store_manager_dashboard.html', {'user': request.user, 'role': 'Store Manager'})
