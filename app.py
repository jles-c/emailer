import streamlit as st
import streamlit.components.v1 as components
from io import StringIO
import pandas as pd
import numpy as np

import json
import ssl
import smtplib
from email.message import EmailMessage
import pandas as pd
from datetime import datetime, time, timedelta
from time import sleep

import helpers


CONFIG_FILEPATH = "config.json"
today = datetime.today().date()

with open(CONFIG_FILEPATH, "r") as json_file:
    config = json.load(json_file)

config['email_sent_filename'] = config['email_sent_filename'].format(today = today)

# Keep vars in the session state
for var in config['session_state_var']:
    if var not in st.session_state: 
        if var in config:
            st.session_state[var] = config[var]
        else:
            st.session_state[var] = None

st.title('Newsletter app')

st.session_state['test_mode'] = st.checkbox("Mode test")
test_mode = st.session_state['test_mode']


#======== SIDEBAR ========#
with st.sidebar:

# Horaire
    # Email parameters
    st.subheader("Paramètres d'emails")
    st.session_state['sender_name'] = st.text_input('Nom expéditeur (visible dans la boîte de réception)', value = config['sender_name'])
    st.session_state['email_subject'] = st.text_input("Objet de l'email")

# Email login
    st.subheader('Login infos')
    st.session_state['sender_email'] = st.text_input('Adresse email : expéditeur', value = config['sender_email'])
    st.session_state['password'] = st.text_input('Mot de passe', value = config['password'])
    st.session_state['server'] = st.text_input('Serveur SMTP', value = config['server'])
    st.session_state['port'] = st.text_input('Port', value = config['port'])

    # Recipients & Email content
    st.subheader('Fichiers à uploader')
    if not test_mode:
        email_dest_file = st.session_state['email_dest_file'] = st.file_uploader('Upload adresses email : destinataires (CSV)')
    newsletter_file = st.session_state['newsletter_file'] = st.file_uploader('Upload newsletter (HTML)')

#=========================#

#======== PROGRAMMER EMAIL ========#
schedule_email = st.checkbox("Programmer l'expédition")
if schedule_email:
    time_selector = st.session_state['scheduled_time'] = st.time_input('Sélectionner un horaire',value = time(17,0))
    if st.checkbox("Montrer l'horaire choisie"):
        st.write(time_selector)
#==================================#

#=====PREVISUALISER NEWSLETTER=====#
render_html = st.checkbox('Prévisualiser le contenu de la newsletter')
if render_html:
    if newsletter_file:
        newsletter_html_content = helpers.get_message(newsletter_file)
        components.html(newsletter_html_content, height = 600, scrolling = True)
    else:
        st.write('Aucune newsletter à visualiser.')
#==================================#

#==========ENVOYER EMAILS==========#
with st.expander('Envoi des emails', expanded=False):
    col1, col2 = st.columns([1,3])
    
    with col1:
        st.write(f'Mode test : {test_mode}')
        test_emails = st.session_state['test_emails'] = config['test_emails']

        emails_to_send_btn = st.button('emails à envoyer', 
                                       on_click = helpers.show_emails_list, 
                                       args= [col2, st.session_state, test_mode]
                                       )
        
        clean_btn = st.button('clean', on_click= helpers.del_state_elmt, 
                              args = ['email_dest_file'])
        
        send_mails_btn = st.button('Envoyer', 
                                on_click = helpers.batch_send_emails, 
                                args = [col2, st.session_state, test_mode]
                                )
#==================================#