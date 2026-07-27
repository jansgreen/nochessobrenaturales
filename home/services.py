from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


class EmailConfigurationError(RuntimeError):
    pass


def send_contact_email(contact_data):
    recipient = settings.CONTACT_RECIPIENT_EMAIL.strip()
    sender = settings.DEFAULT_FROM_EMAIL.strip()

    if not recipient or not sender:
        raise EmailConfigurationError(
            "The contact email recipient and sender must be configured."
        )

    if settings.EMAIL_BACKEND.endswith("smtp.EmailBackend"):
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            raise EmailConfigurationError(
                "The SMTP username and app password must be configured."
            )

    context = {
        **contact_data,
        "submitted_at": timezone.localtime(),
    }
    subject = f"[Noches Sobrenaturales] {contact_data['topic']}"
    text_body = render_to_string("emails/contact_message.txt", context)
    html_body = render_to_string("emails/contact_message.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=sender,
        to=[recipient],
        reply_to=[contact_data["email"]],
    )
    email.attach_alternative(html_body, "text/html")

    if email.send(fail_silently=False) != 1:
        raise RuntimeError("The email backend did not send the contact message.")

