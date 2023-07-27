from email.message import EmailMessage
import pandas as pd
from time import sleep
from datetime import datetime
import streamlit as st
import ssl
import smtplib
from io import StringIO

def send_email(sender_name, sender_email, dest_email, email_subject, message, mailer):
    email = EmailMessage()
    email['From'] = f"{sender_name} <{sender_email}>"
    email['To'] = dest_email
    email['Subject'] = email_subject
    email.set_content(message, subtype = 'html')

    mailer.sendmail(sender_email, dest_email, email.as_string())
    return email

def get_email_dest_from_csv(filename, col = 'EMAIL', sep = ';'):
    try:
        return pd.read_csv(
                filename, 
                sep = ';', 
                usecols=['EMAIL'], 
                skip_blank_lines = True
                )['EMAIL'].to_list()
    
    except Exception as e:
        raise e

def get_emails_sent(session_state):
    email_sent_filename = session_state['email_sent_filename']
    try:
        return get_email_dest_from_csv(email_sent_filename, col = 'email', sep = ',')
    except :
        return []


def get_emails_to_send(session_state, test_mode):
    if test_mode:
        return session_state['test_emails']
    
    else:
        if session_state['email_dest_file']:
            
            emails_to_send = get_email_dest_from_csv(session_state['email_dest_file'])
            emails_sent = get_emails_sent(session_state)

            for email in emails_sent:
                if email in emails_to_send:
                    emails_to_send.remove(email)

            return emails_to_send
        else:
            raise "No emails found"

def show_emails_list(col, session_state, test_mode = False):
    try:
        emails_list = get_emails_to_send(session_state, test_mode)
        col.write(emails_list)
    except Exception as e:
        col.write(e)

def update_emails_sent(col, emails_sent_filename, dest_emails_sent):
    new_emails_sent_df = pd.DataFrame(dest_emails_sent, columns= ['index', 'email','subject', 'datetime'])
    try:
        emails_sent_df = pd.read_csv(emails_sent_filename)
        all_emails_sent_df = pd.concat([emails_sent_df,new_emails_sent_df]).reset_index(drop = True)
    except:
        all_emails_sent_df = pd.DataFrame(new_emails_sent_df)
    
    all_emails_sent_df.to_csv(emails_sent_filename, index = False)
    col.write(f'emails sent updated in file {emails_sent_filename}')
    return all_emails_sent_df

def get_newsletter(newsletter_filename):
    return open(newsletter_filename, 'r').read()

def test_function(elmt_list, col):
    elmt_list.append(str(datetime.today())[:-7])
    col.write(elmt_list)

def del_state_elmt(elmt): 
    del st.session_state[elmt]

def batch_send_emails(col, session_state, test_mode):
    
    server = session_state['server']
    port = session_state['port']
    sender_email = session_state['sender_email']
    password = session_state['password']
    sender_name = session_state['sender_name']
    email_subject = session_state['email_subject']
    email_sent_filename = session_state['email_sent_filename']
    message = session_state['message'] = get_message(session_state['newsletter_file'])
    # if email_sent_filename:
    #     col.write(f"email_sent_filename : {email_sent_filename}")
    # if message:
    #     col.write(f"message found (size {len(message)})")
    
    dest_emails_sent = []
    dest_emails = get_emails_to_send(session_state, test_mode)

    with smtplib.SMTP(server, port) as mailer:
        # Setting debug level in order to get detailed information for debuging
        # mailer.set_debuglevel(1)
        context = ssl.create_default_context()
        mailer.starttls(context=context)
        
        # # Authentication
        mailer.login(sender_email, password)

        # Sending the email
        for ind, dest_email in enumerate(dest_emails, start=1):

                try:
                    email = send_email(
                        sender_name = sender_name,
                        sender_email = sender_email,
                        dest_email = dest_email,
                        email_subject = email_subject,
                        message = message,
                        mailer = mailer
                    )
                    subject = email['Subject']
                    dest_emails_sent.append([ind, dest_email, subject, datetime.now()])
                    col.write(f'[{ind:03}] : {dest_email}')
                except Exception as e:
                     print(f"Exception : {e}")
                     break
        
        emails_sent_df = update_emails_sent(col, email_sent_filename, dest_emails_sent)
        nb_mails_sent = len(emails_sent_df)
        col.write('Done')
        col.write(f'All emails sent : {nb_mails_sent}')

                
def get_message(message_file):
    try:
        stringio = StringIO(message_file.getvalue().decode("utf-8"))
        return stringio.read()
    except Exception as e:
        raise e