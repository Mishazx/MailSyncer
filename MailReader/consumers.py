import asyncio
import json
from django.utils import timezone
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .mail_reader import connect_to_mail, fetch_message_count, fetch_messages, fetch_single_message
import logging
from concurrent.futures import ThreadPoolExecutor

from .models import EmailMessage, EmailAccount

class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        email = data.get("email")
        password = data.get("password")
        
        if email and password:
            await self.fetch_mail(email, password)
        else:
            await self.send(text_data=json.dumps({
                "error": "Необходимо передать email и пароль"
            }))
    
    async def fetch_mail(self, email, password):
        try:
            account = await sync_to_async(EmailAccount.objects.get)(email=email)
        except EmailAccount.DoesNotExist:
            account = await sync_to_async(EmailAccount.objects.create)(email=email, password=password)

        try:
            mail = await sync_to_async(connect_to_mail)(email, password)
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Ошибка подключения к почте: {str(e)}"}))
            return

        if not mail:
            await self.send(text_data=json.dumps({"error": "Ошибка подключения к почте"}))
            return
        else:
            await self.send(text_data=json.dumps({"connected": True}))

        count_messages = fetch_message_count(mail)

        for i in range(1, count_messages + 1):
            try:
                message = fetch_single_message(mail, i)

                await EmailMessage.objects.acreate(
                    email_account=account,
                    subject=message["subject"],
                    from_email=message["from"],
                    sent_date=message["date"],
                    receive_date=message.get("receive_date", timezone.now()),
                    description=message.get("body", ""),
                    attachments=message.get("attachments", [])
                )
                
                data = {
                    "percent": int((i) / count_messages * 100),
                    "message": message["subject"],
                    "from": message["from"],
                    "sent_date": message["date"].strftime('%Y-%m-%d %H:%M:%S'),
                    "received_date": message.get("receive_date", timezone.now()).strftime('%Y-%m-%d %H:%M:%S'),
                    "body": message.get("body", ""),
                    "attachments": [{"filename": att["filename"], "url": att["url"]} for att in message.get("attachments", [])]
                }
                await self.send(text_data=json.dumps(data))
                await asyncio.sleep(0.5)
                
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "error": f"Ошибка обработки сообщения {i + 1}: {str(e)}"
                }))

