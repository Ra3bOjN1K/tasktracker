# -*- coding: utf-8 -*-

from celery.task import task


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def just_print():
    print("Print from celery task")
