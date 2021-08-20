from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string


def send_mail_template(subject, template_name, context, recipient_list,
                       from_mail=settings.DEFAULT_FROM_EMAIL, fail_silently=False):

    message_html = render_to_string(template_name, context)
    message_txt = striptags(message_html)

    connection = get_connection(
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD)

    email = EmailMultiAlternatives(
        subject=subject,
        body=message_txt,
        from_email=from_mail,
        to=recipient_list,
        connection=connection
    )

    email.attach_alternative(
        message_html,
        "text/html")

    email.send(fail_silently=fail_silently)