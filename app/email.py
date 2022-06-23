from flask_mail import Message
from flask import current_app, render_template, copy_current_request_context
from threading import Thread
from . import mail


def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], \
        recipients=[to,])
    
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    @copy_current_request_context
    def send_message(msg):
        mail.send(msg)

    sender = Thread(target=send_message, args=(msg,))
    sender.start()
