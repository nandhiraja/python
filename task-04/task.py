def add(a, b):
    return a + b

def send_email(to, template):
    if template == "fail":
        raise Exception("SMTPConnectionError")
    return f"Email sent to {to}"

def generate_thumbnail(image_id, size):
    return f"/thumbs/{image_id}_{size[0]}x{size[1]}.jpg"

def send_sms(phone, message):
    return f"SMS sent to {phone}: {message}"

def send_notification(user_id, message):
    return f"Notification sent to user {user_id}"

