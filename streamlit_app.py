import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# ... (rest of your imports)

# Load credentials from Streamlit secrets (no need to modify the private key)
creds = service_account.Credentials.from_service_account_info(
    st.secrets,
    scopes=["https://www.googleapis.com/auth/drive"]
)
service = build('drive', 'v3', credentials=creds)

# ... (Your Streamlit app title)

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df_new = pd.read_csv(uploaded_file)
    st.write("Uploaded DataFrame:")
    st.write(df_new)

    # Generate filename with timestamp (More robust)
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"emails_{timestamp}.csv"

    # Prepare for Google Drive upload (Simplified)
    file_metadata = {
        'name': file_name,
        'parents': ['1aokxbYgfqCEia1c0uvK2EPDM_Vfm03Yb']  # Specify your folder ID
    }
    media = MediaIoBaseUpload(uploaded_file, mimetype='text/csv')

    # Upload to Google Drive
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
   
    st.write(f"File uploaded to Google Drive: {file_name} (ID: {file.get('id')})")
