import os, shutil, time, sys
from twilio.rest import Client

ACCOUNT_SID = "ACbe9ca3f562c7d7fe80fc560db69fa588"
AUTH_TOKEN = "9a8ffae380118f71a6e693956c34a4b5"
SMS_NUMBER = "+18125788368"
MESSAGING_SERVICE_ID = "MG5eb6a2e338a34fa801960c2a827522d3"

def sendSMS(mobilenumber,message,url):
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	message = client.messages \
	              .create(
                       body="message from www.slickhire.in and click to submit the info " + url,
                       messaging_service_sid=MESSAGING_SERVICE_ID,
                       to=mobilenumber
                   )

def makeVoiceCall(mobilenumber, message):
	client = Client(ACCOUNT_SID, AUTH_TOKEN)
	call = client.calls.create(
        url='https://handler.twilio.com/twiml/EHf4053f6f0d0778cc93de166e1856f7c3',
                        to=mobilenumber,
                        from_=SMS_NUMBER
                    )

def send_email(candidate_name,
          job_title,
          company_name,
          location,
          com_link,
          desc_link,
          input_link,
          optout_link,
          to_mail
          ):
    send_mail(
    'Job Alert SlickHire',
    get_template('email.html').render(
        {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'company_name': company_name,
            'location': location,
            'com_link': com_link,
            'desc_link': desc_link,
            'input_link': input_link,
	    'optout_link': optout_link
        }
    ),
    settings.EMAIL_HOST_USER,
    [to_mail],
    fail_silently = False)