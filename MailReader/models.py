from django.db import models

class EmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email


class EmailMessage(models.Model):
    email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    from_email = models.EmailField()
    sent_date = models.DateTimeField()
    receive_date = models.DateTimeField()
    description = models.TextField()
    attachments = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.subject

