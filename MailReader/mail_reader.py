import os
import logging
import imaplib
from datetime import datetime
import email
from email.header import decode_header, Header

from django.conf import settings
from django.core.files.base import ContentFile

from MailReader.utils import decode_email_header, get_service_from_email, parse_email_date
from MailSyncer.settings import IMAP_SERVERS


# Настройка базовой конфигурации
logging.basicConfig(level=logging.INFO)

# Создание логгера
logger = logging.getLogger(__name__)
    
# def flexible_decode_header(header):
#     decoded_fragments = decode_header(header)
#     subject_parts = []

#     for fragment, encoding in decoded_fragments:
#         if isinstance(fragment, bytes):
#             subject_parts.append(fragment.decode(encoding or 'utf-8', errors='replace'))
#         else:
#             subject_parts.append(fragment)

#     return ''.join(subject_parts)    


def connect_to_mail(email_address, password):
    """
    Подключение к почтовому серверу через IMAP
    """
    service = get_service_from_email(email_address)
    if service is None:
        print("Неизвестный почтовый сервис.")
        return None
    
    try:
        imap_host = IMAP_SERVERS[service]
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(email_address, password)
        return mail
    except Exception as e:
        print(f"Ошибка подключения к почтовому серверу: {e}")
        return None


def fetch_message_count(mail, folder="inbox"):
    """
    Получение количества сообщений в указанной папке
    """
    try:
        mail.select(folder)
        result, data = mail.search(None, "ALL")
        if result != "OK":
            print("Ошибка при поиске писем")
            return 0
        
        email_ids = data[0].split()
        return len(email_ids)
    
    except Exception as e:
        print(f"Ошибка получения количества сообщений: {e}")
        return 0


def fetch_single_message(mail, email_id):
    """
    Получение одного письма по его ID
    """
    message = None
    print(f"Получаем письмо с ID {email_id}")
    
    try:
        email_id = str(email_id)  # Преобразуем email_id в строку, если это still int
        result, msg_data = mail.fetch(email_id, "(RFC822)")
        if result != "OK":
            print(f"Ошибка получения письма с ID {email_id}")
            return message
            
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        
        from_ = decode_email_header(msg["From"])
        date = msg.get("Date")
        date_sent = parse_email_date(date)

        attachments = []
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    attachments.extend(handle_attachments(part)) 
                elif content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()

        message = {
            "subject": subject,
            "from": from_,
            "date": date_sent,
            "body": body,
            "attachments": attachments
        }

    except Exception as e:
        import traceback
        print(f"Ошибка {traceback.format_exc()}")
        print(f"Ошибка чтения письма: {e}")

    return message


def fetch_messages(mail, folder="inbox"):
    """
    Получение писем из почтового ящика
    """
    messages = []
    print(f"Получаем письма из папки {folder}")
    try:
        mail.select(folder)
        result, data = mail.search(None, "ALL")
        if result != "OK":
            print("Ошибка при поиске писем")
            return messages
        
        
        email_ids = data[0].split()[-50:]


        for email_id in email_ids:
            result, msg_data = mail.fetch(email_id, "(RFC822)")
            if result != "OK":
                print(f"Ошибка получения письма с ID {email_id}")
                continue
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            
            logger.info(f'From: {msg["From"]}')
            from_ = decode_email_header(msg["From"])
            
            date = msg.get("Date")
            date_sent = parse_email_date(date)

            attachments = []
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        attachments.extend(handle_attachments(part)) 
                    elif content_type == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                
                body = msg.get_payload(decode=True).decode()

            messages.append({
                "subject": subject,
                "from": from_,
                "date": date_sent,
                "body": body,
                "attachments": attachments
            })

    except Exception as e:
        import traceback
        print(f"Ошибка {traceback.format_exc()}")
        print(f"Ошибка чтения писем: {e}")

    return messages


def handle_attachments(part):
    """Обрабатывает вложения из части email-сообщения."""
    attachments = []
    filename, encoding = decode_header(part.get_filename())[0]
    
    if isinstance(filename, bytes):
        filename = filename.decode(encoding or 'utf-8')

    if filename:
        payload = part.get_payload(decode=True)

        attachments_dir = os.path.join(settings.MEDIA_ROOT, 'attachments')
        os.makedirs(attachments_dir, exist_ok=True)

        file_path = os.path.join(attachments_dir, filename)

        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            file_path = os.path.join(attachments_dir, f"{name}_{counter}{ext}")
            counter += 1

        with open(file_path, 'wb') as f:
            f.write(payload)

        media_relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
        media_url = os.path.join(settings.MEDIA_URL, media_relative_path).replace("\\", "/")
        
        attachments.append({
            "filename": filename,
            "url": media_url
        })

    return attachments

