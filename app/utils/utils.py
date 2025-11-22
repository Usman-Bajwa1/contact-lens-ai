def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return email
    try:
        user, domain = email.split("@")
        if len(user) > 2:
            masked_user = user[:2] + "****"
        else:
            masked_user = user + "****"
        return f"{masked_user}@{domain}"
    except:
        return email

def mask_phone(phone: str) -> str:
    if not phone:
        return phone
    # Keep last 4 digits
    clean_phone = "".join(filter(str.isdigit, phone))
    if len(clean_phone) > 4:
        return "*" * (len(clean_phone) - 4) + clean_phone[-4:]
    return phone