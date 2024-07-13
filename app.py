from flask import Flask, request, Response
from celery import Celery
import logging
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

#configure celery
app.config.update(
    CELERY_BROKER_URL='pyamqp://guest@localhost//',
    CELERY_RESULT_BACKEND='rpc://'
)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def send_email_task(email):
    msg = MIMEText("This is a test email sent from a Python app using RabbitMQ and Celery.")
    msg['Subject'] = 'Test Email'
    msg['From'] = 'adeshiletosin111@gmail.com'
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('adeshiletosin111@gmail.com', 'wdowgvhuxplfwknd')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

@app.route('/', methods=['GET'])
def handle_request():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')

    if sendmail:
        email = sendmail.split('mailto:')[-1]
        send_email_task(email)
        return 'Email has been queued for sending.', 200
    elif talktome:
        log_message = f"{datetime.now()}: talktome parameter received\n"
        log_path = '/var/log/messaging_system.log'

        try:
            with open(log_path, 'a') as log_file:
                log_file.write(log_message)
            return 'Current time logged.', 200
        except PermissionError:
            return 'Permission denied for writing to log file.', 500
    else:
        return 'Please provide a parameter.', 400

@app.route('/logs', methods=['GET'])
def get_logs():
    log_path = '/var/log/messaging_system.log'
    try:
        with open(log_path, 'r') as log_file:
            logs = log_file.read()
        return Response(logs, mimetype='text/plain'), 200
    except FileNotFoundError:
        return 'Log file not found.', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
