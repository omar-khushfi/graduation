from django.shortcuts import render, redirect
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
import random
from django.db.models.functions import ExtractWeek
import string
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from pycountry import countries
from .models import *
from exam.models import *
from folders_words.models import *
import json
from django.db.models import Count, Sum, Case, When, IntegerField
from .forms import *
from django.conf import settings
from django.core.mail import EmailMessage
import pycountry
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .forms import *

def generate_random_code(length=6):
    characters = string.ascii_letters + string.digits  
    code = ''.join(random.choices(characters, k=length))  
    return code

websitename = "W"
myemail = 'omar.khu.2004@gmail.com'
COUNTRY_CHOICES = [(country.name, country.name) for country in pycountry.countries]
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('accounts:login_view')

class Login_View(View):
    template_name = 'account_template/login.html'
    
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = None
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)            
        if user:
            if check_password(password, user.password):
                login(request, user)
                return redirect("folders_words:folders")
            else:
                messages.error(request, 'Incorrect password!')
                return render(request, self.template_name)    
        else:
            messages.error(request, 'User not found!')
            return render(request, self.template_name)    


from .tokens import email_verification_token

def activate(request, uid, token):
    user = get_object_or_404(User, pk=uid)
    user.is_verified = True
    user.save()
    return redirect('accounts:login_view')
   


class Signup_View(View):
    template_name = 'account_template/signup.html'
    
    def get(self, request):
        countries=COUNTRY_CHOICES
        return render(request, self.template_name,{'countries':countries})
    
    def post(self, request):
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        age = request.POST.get("age")
        country= request.POST.get("country")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email already exists")
            return render(request, self.template_name)
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username already exists")
            return render(request, self.template_name)
        if password1 != password2:
            messages.error(request, "Your passwords do not match")
            return render(request, self.template_name)
        
        user = User.objects.create(
            email=email,
            password=make_password(password1),
            age=age,
            username=username,
            first_name=first_name,
            last_name=last_name,
            country=country
        )
        
        if user:
            token = email_verification_token.make_token(user)
            uid = user.pk
            activation_link = request.build_absolute_uri(
                reverse("accounts:activate", kwargs={"uid": uid, "token": token})
            )

            email_body = f"""
            Hi {user.username},

            Thank you for registering!  
            Please click the link below to activate your account:

            {activation_link}

            If you didn’t request this, you can ignore this email.
            """

            email_message = EmailMessage(
                "Activate your account",          # عنوان الرسالة
                email_body,                       # نص الرسالة
                settings.EMAIL_HOST_USER,         # المرسل
                [email],                          # المستلم
            )
            email_message.fail_silently = True
            email_message.send()
            login(request, user)
            return redirect("accounts:activate_account")

def active_account(request):
    return render(request,"account_template/acitve_account.html")

def get_user_answer_analytics(user):
    one_month_ago = timezone.now() - timedelta(days=30)
    
    answers = Answer.objects.filter(
        user=user,
        created_at__gte=one_month_ago
    )
    
    analytics = answers.annotate(
        week=ExtractWeek('created_at')
    ).values('week').annotate(
        total_answers=Count('id'),
        correct_answers=Sum(Case(When(is_true=True, then=1), output_field=IntegerField())),
        wrong_answers=Sum(Case(When(is_true=False, then=1), output_field=IntegerField()))
    ).order_by('week')
    
    return analytics       
        

@login_required(login_url='/account/login/')
def profile(request):
    
    user = request.user
    if user.is_verified == False:
        return redirect("accounts:activate_account")

    analytics = get_user_answer_analytics(user)
    
    analytics_json = json.dumps(list(analytics))
    context = {
        'analytics_json': analytics_json,
        'user': user,
        'count_words':Word.objects.all().count(),
        'count_folders':Folder.objects.all().count(),
        'languages':Language.objects.filter(user=user)
    }    
    return render(request, 'account_template/profile.html', context)


@login_required(login_url='/account/login/')
def update_profile(request):
    user = request.user
    if user.is_verified == False:
        return redirect("accounts:activate_account")
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if User.objects.filter(email=request.POST.get("email")) and request.POST.get("email") != user.email:
            messages.error(request, "This email already exists")

            return render(request, 'account_template/update_profile.html', {'form': form})
            
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')  
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'account_template/update_profile.html', {'form': form})


class ForgotPassword(View):
    def get(self,request):
        return render(request, 'account_template/forgot_password.html')
    def post(self,request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()
            password_reset_url = reverse('accounts:reset-password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )
            email_message.fail_silently = True
            email_message.send()
            return redirect('accounts:password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('accounts:forgot-password')

  

def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'account_template/password_reset_sent.html')
    else:
      
        messages.error(request, 'Invalid reset id')
        return redirect('accounts:forgot-password')



class ResetPassword(View):
    def get(self, request, reset_id):
        try:
            password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
            return render(request, 'account_template/reset_password.html')
        except PasswordReset.DoesNotExist:
            messages.error(request, 'Invalid reset id')
            return redirect('accounts:forgot-password')

    def post(self, request, reset_id):
        try:
            password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            passwords_have_error = False

            # Validate passwords
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')
            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            # Check if the reset link has expired
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            # If no errors, reset the password
            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('accounts:login_view')
            else:
                # Redirect back to the reset password page with errors
                return redirect('accounts:reset-password', reset_id=reset_id)

        except PasswordReset.DoesNotExist:
            messages.error(request, 'Invalid reset id')
            return redirect('accounts:forgot-password')




@login_required
def edit_languages(request):
    if request.user.is_verified == False:
        return redirect("accounts:activate_account")
    LanguageFormSet = modelformset_factory(
        Language,
        form=LanguageForm,
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = LanguageFormSet(
            request.POST,
            queryset=Language.objects.filter(user=request.user),
            prefix='language'
        )
        has_error = False
        
        if formset.is_valid():
            for form in formset.forms:
                if form in formset.deleted_forms:
                    if form.instance.pk:
                        form.instance.delete()
            
            language_codes = []
            for form in formset.forms:
                if form not in formset.deleted_forms and form.cleaned_data.get('code'):
                    code = form.cleaned_data.get('code')
                    if code in language_codes:
                        has_error = True
                        messages.error(request, 'لا يمكن اختيار نفس اللغة أكثر من مرة')
                        break
                    language_codes.append(code)
            
            if not has_error:
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.user = request.user
                    try:
                        if not instance.pk and Language.objects.filter(user=request.user, code=instance.code).exists():
                            has_error = True
                            messages.error(request, 'هذه اللغة موجودة بالفعل في قائمة لغاتك')
                            continue
                        instance.save()
                    except Exception:
                        has_error = True
                        messages.error(request, 'حدث خطأ أثناء حفظ اللغات')
                        continue
                
                if not has_error:
                    native_languages = Language.objects.filter(user=request.user, is_native=True).count()
                    if native_languages == 0 and instances:
                        first_language = Language.objects.filter(user=request.user).first()
                        if first_language:
                            first_language.is_native = True
                            first_language.save()
                    
                    messages.success(request, 'تم تحديث اللغات بنجاح!')
                    return redirect('accounts:profile')
        else:
            messages.error(request, 'يرجى التأكد من صحة البيانات المدخلة')
    
    else:
        formset = LanguageFormSet(
            queryset=Language.objects.filter(user=request.user),
            prefix='language'
        )
    
    return render(request, 'account_template/edit_languages.html', {
        'formset': formset,
        'available_languages': dict(Language.LANGUAGE_CHOICES)
    })
    
    
    
# def Theme(request):
#     user=None
#     if request.POST.get('theme')==True:
#         user = User.objects.get(id=request.user.id)
#         user.theme=True
#     else:
#        user = User.objects.get(id=request.user.id)
#        user.theme=False
#     user.save()
#     return redirect("/")      
        