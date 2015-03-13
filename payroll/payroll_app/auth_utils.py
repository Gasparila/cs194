from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import get_user_model, authenticate
import web_utils


def check_employer(employer_id, employer_key):
    employer = Employer.objects.get(employer_id = employer_id)
    return check_password(employer_key, employer.hash_key)

def create_account(email, password, confirm_password, name, address):
    if password is None: return "Password is required"
    if confirm_password is None: return "Password confirmation is required"
    if password != confirm_password: return "Password must match confirmation"
    hash_key = make_password(password)
    error=web_utils.addEmployer(employer_id = email, employer_name=name, address=address, hash_key=hash_key)
    if error is not None: return error
    get_user_model().objects.create_user(email, password)
    return None;


