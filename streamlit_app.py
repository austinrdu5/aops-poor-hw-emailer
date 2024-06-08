import streamlit as st
import pandas as pd
import os
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

try:
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build('drive', 'v3', credentials=creds)
except Exception as e:
    st.error(f"Error authenticating with Google Drive: {e}")
    st.stop()

# 2. File Upload and Processing
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
        # 2.1 Upload the File (Same as before)
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"emails_{timestamp}.csv"
        file_metadata = {'name': file_name, 'parents': ['YOUR_FOLDER_ID']}
        media = MediaIoBaseUpload(uploaded_file, mimetype='text/csv')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 2.2 List and Sort Files in Folder
        results = service.files().list(
            q=f"'YOUR_FOLDER_ID' in parents",
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])
        csv_paths = sorted([item['name'] for item in items if item['name'].endswith('.csv')], reverse=True)

        if len(csv_paths) >= 3:  # Ensure we have enough files for comparison
            # 2.3 Read and Concatenate Previous Files
            previous_dfs = [pd.read_csv(uploaded_file)]  # Start with the current file
            for i in range(1, 3):  # Read the next two most recent files
                file_id = [item['id'] for item in items if item['name'] == csv_paths[i]][0]
                request = service.files().get_media(fileId=file_id)
                previous_dfs.append(pd.read_csv(request))

            previous_df = pd.concat(previous_dfs[1:])  # Concatenate the previous two

            # 2.4 Remove Duplicate Rows
            merged_df = pd.merge(previous_dfs[0], previous_df, how='left', indicator=True)
            to_email = merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge')

            # 2.5 Format DataFrame and Provide Download
            to_email = to_email.rename(columns={'primary parent email': 'email'})
            to_email['student name'] = to_email['student name'].str.split().str[0]
            to_email['primary parent'] = to_email['primary parent'].str.title()
            to_email = to_email[['email', 'student name', 'class name', 'primary parent']]
            st.download_button("Download CSV", to_email.to_csv(index=False), file_name)

        else:
            st.warning("Not enough previous files in the folder for comparison.")
    
    except Exception as e:
        st.error(f"Error processing file: {e}")
