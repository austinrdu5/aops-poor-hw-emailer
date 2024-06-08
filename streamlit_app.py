import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import BytesIO
import json

# Read environment variables
GDRIVE_TYPE = st.secrets["GDRIVE_TYPE"]
GDRIVE_PROJECT_ID = st.secrets["GDRIVE_PROJECT_ID"]
GDRIVE_PRIVATE_KEY_ID = st.secrets["GDRIVE_PRIVATE_KEY_ID"]
GDRIVE_PRIVATE_KEY = st.secrets["GDRIVE_PRIVATE_KEY"]
GDRIVE_CLIENT_EMAIL = st.secrets["GDRIVE_CLIENT_EMAIL"]
GDRIVE_CLIENT_ID = st.secrets["GDRIVE_CLIENT_ID"]
GDRIVE_AUTH_URI = st.secrets["GDRIVE_AUTH_URI"]
GDRIVE_TOKEN_URI = st.secrets["GDRIVE_TOKEN_URI"]
GDRIVE_AUTH_PROVIDER_X509_CERT_URL = st.secrets["GDRIVE_AUTH_PROVIDER_X509_CERT_URL"]
GDRIVE_CLIENT_X509_CERT_URL = st.secrets["GDRIVE_CLIENT_X509_CERT_URL"]

# Create a dictionary for the service account credentials
credentials_dict = {
    "type": GDRIVE_TYPE,
    "project_id": GDRIVE_PROJECT_ID,
    "private_key_id": GDRIVE_PRIVATE_KEY_ID,
    "private_key": GDRIVE_PRIVATE_KEY.replace('\\n', '\n'),
    "client_email": GDRIVE_CLIENT_EMAIL,
    "client_id": GDRIVE_CLIENT_ID,
    "auth_uri": GDRIVE_AUTH_URI,
    "token_uri": GDRIVE_TOKEN_URI,
    "auth_provider_x509_cert_url": GDRIVE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": GDRIVE_CLIENT_X509_CERT_URL
}

# Authenticate and initialize Google Drive API
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
service = build('drive', 'v3', credentials=credentials)

st.title("Weekly Customer Email Processor")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df_new = pd.read_csv(uploaded_file)
    st.write("Uploaded DataFrame:")
    st.write(df_new)

    # Get the current date and generate the filename
    current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    file_name = f"emails_{current_date}.csv"
    
    # Save the DataFrame to a CSV file in-memory
    buffer = BytesIO()
    df_new.to_csv(buffer, index=False)
    buffer.seek(0)

    # Upload the file to Google Drive
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaIoBaseUpload(buffer, mimetype='text/csv', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    st.write("File uploaded successfully to Google Drive with ID:", file.get('id'))
