import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.title("Weekly Customer Email Processor")

# 1. Load Service Account Information (Corrected)
service_account_info = {
    "type": st.secrets["GDRIVE_TYPE"],
    "project_id": st.secrets["GDRIVE_PROJECT_ID"],
    "private_key_id": st.secrets["GDRIVE_PRIVATE_KEY_ID"],
    "private_key": st.secrets["GDRIVE_PRIVATE_KEY"],
    "client_email": st.secrets["GDRIVE_CLIENT_EMAIL"],
    "client_id": st.secrets["GDRIVE_CLIENT_ID"],
    "auth_uri": st.secrets["GDRIVE_AUTH_URI"],
    "token_uri": st.secrets["GDRIVE_TOKEN_URI"],
    "auth_provider_x509_cert_url": st.secrets["GDRIVE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": st.secrets["GDRIVE_CLIENT_X509_CERT_URL"],
}

# 2. Authenticate with Google Drive
try:
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build('drive', 'v3', credentials=creds)
except Exception as e:
    st.error(f"Error authenticating with Google Drive: {e}")
    st.stop()  # Stop app execution if authentication fails

# 3. File Upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # 3.1 Read CSV
        df_new = pd.read_csv(uploaded_file)
        st.write("Uploaded DataFrame:")
        st.write(df_new)

        # 3.2 Generate Filename
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"emails_{timestamp}.csv"

        # 3.3 Prepare Metadata
        file_metadata = {'name': file_name, 'parents': ['YOUR_FOLDER_ID']}
        media = MediaIoBaseUpload(uploaded_file, mimetype='text/csv')

        # 3.4 Upload to Google Drive
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success(f"File uploaded to Google Drive: {file_name} (ID: {file.get('id')})")

    except Exception as e:
        st.error(f"Error uploading to Google Drive: {e}")
