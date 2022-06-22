from __future__ import absolute_import, unicode_literals
from asyncio.log import logger

from celery import shared_task
from typing import List
from django.core.mail import send_mail
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(name="send_mail_task")
def send_mail_task(subject: str, body: str, from_email: str, to: List[str]) -> None:
    try:
        send_mail(subject, body, from_email, to)
        logger.info(f"Sent registraion email to {str(to)}")
    except Exception as e:
        logger.info(f"Failed to send registration email to {str(to)}")
        logger.info(f"Error: {e}")
