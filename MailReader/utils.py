import re
from datetime import datetime
from email.header import Header, decode_header


def parse_email_date(date_str):
    """
    Парсинг строки с датой в объект datetime.
    """
    try:
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
    except Exception:
        return datetime.now()

def get_service_from_email(email_address):
    """
    Определение почтового сервиса по адресу электронной почты
    """
    domain = email_address.split('@')[-1]
    if "yandex" in domain:
        return "yandex"
    elif "gmail" in domain:
        return "gmail"
    elif "mail.ru" in domain:
        return "mail"
    else:
        return None
     
def decode_email_header(encoded_str):
    if isinstance(encoded_str, Header):
        encoded_str = ''.join(
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decode_header(str(encoded_str))
        )

    match = re.match(r'(.+?) <(.+?)>', encoded_str)
    if match:
        encoded_text = match.group(1).strip()
        email_address = match.group(2).strip()

        decoded_parts = decode_header(encoded_text)
        decoded_text = ''.join(
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded_parts
        )
        
        return f'{decoded_text} <{email_address}>'
    
    decoded_parts = decode_header(encoded_str)
    decoded_text = ''.join(
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded_parts
    ).strip()
    
    return decoded_text if decoded_text else encoded_str