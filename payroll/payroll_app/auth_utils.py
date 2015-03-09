def check_employer(employer_id, employer_key):
    employer = Employer.objects.get(employer_id = employer_id)
    return check_password(employer_key, employer.hash_key)
