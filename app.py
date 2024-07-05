import streamlit as st
import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

CSV_FOLDER_ID = "1pS27r6Hpb_a17kmQPURIRNfS2RYUnZc5"

# Service Account Information (Google Drive API)
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

# Function to authenticate with Google Drive
def authenticate(service_account_info=service_account_info):
    try:
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Error authenticating with Google Drive: {e}")
        st.stop()

# Function to list alphabetically last 3 files in the specified folder
def get_csvs(service, folder_id=CSV_FOLDER_ID):
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            orderBy='name',
            fields='nextPageToken, files(id, name)'
        ).execute()
        items = results.get('files', [])
        return items[:-4:-1]
    except Exception as e:
        st.error(f"Error accessing files: {e}")
        st.stop()

# Function to read CSVs by ID
def read_csv(service, file_id):
    try:
        request = service.files().get_media(fileId=file_id)
        response_content = request.execute()
        return pd.read_csv(BytesIO(response_content))
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Function to process most recent CSVs
def process_csvs(service, csv_list):
    try:
        # Read the most recent CSVs
        dfs = [read_csv(service, item['id']) for item in csv_list]
        df = pd.concat(dfs)

        # Process the data
        df = df.groupby('email').agg(
            student_name=('student name', 'first'),
            class_name=('class name', 'first'),
            primary_parent=('primary parent', 'first')
        ).reset_index()

        # Download the CSV
        download_csv(df, "processed_data.csv")
    except Exception as e:
        st.error(f"Error processing CSVs: {e}")
        st.stop()

# Function to download CSV to user's local machine
def download_csv(df, file_name):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)


# Begin Streamlit App
st.title("SDCV Poor HW Emailer")
st.write("This app processes a CSV file of student information and sends emails to parents who have not completed homework.")

# Authenticate with Google Drive
service = authenticate(service_account_info)

# List most recent files in the folder
try: 
    csv_list = get_csvs()

    with st.container():
        st.header("Most recent files in folder (alphabetically):")

        if not csv_list:
            st.write('No files found.')
        else:
            for item in csv_list:
                st.write(f"- {item['name']}")  # Display file names

except Exception as e:
    st.error(f"Error accessing files: {e}")

st.write("To add a new file, please upload a CSV into [this Google Drive folder](https://drive.google.com/drive/folders/1pS27r6Hpb_a17kmQPURIRNfS2RYUnZc5). \
         Please note that the app uses the file names to sort by newest, so please following the naming conventions within the folder (poor_hw_reportYYYY-MM-DD....csv).")

# Process and Download CSVs
if st.button("Get This Week's Sequence CSVs"):
    with st.spinner("Processing reports..."):
        pass

# 2. File Upload and Processing
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
 
        # 2.2 List and Sort Files in Folder
        results = service.files().list(
            q=f"'{CSV_FOLDER_ID}' in parents",
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])
        csv_paths = sorted([item['name'] for item in items if item['name'].endswith('.csv')], reverse=True)

        if len(csv_paths) >= 3:
            # 2.3 Read and Concatenate Previous Files
            previous_dfs = [pd.read_csv(uploaded_file)] 
            for i in range(1, 3):
                file_id = [item['id'] for item in items if item['name'] == csv_paths[i]][0]
                request = service.files().get_media(fileId=file_id)
                response_content = request.execute() 
                previous_dfs.append(pd.read_csv(BytesIO(response_content)))  # Read from BytesIO

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
