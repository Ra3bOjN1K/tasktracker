#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.conf import settings

from celery.task import task


@task(ignore_result=True)
def send_confirm_email(tracker_user):
    current_site_domain = settings.CURRENT_SITE_DOMAIN
    confirm_url = "{domain}/confirm-email/{key}/".format(domain=current_site_domain, key=tracker_user._key)
    subject = '[{domain}] Please Confirm Your E-mail Address'.format(domain=current_site_domain)
    message = "You're receiving this e-mail because user {username} at " \
              "{domain} has given yours as an e-mail address to " \
              "connect their account.\nTo confirm this is correct, go " \
              "to {confirm_url}".format(username=tracker_user.user.username, domain=current_site_domain,
                                        confirm_url=confirm_url)

    send_mail(subject, message, settings.EMAIL_HOST_USER, [tracker_user.user.email])
