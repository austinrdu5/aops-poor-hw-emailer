import streamlit as st
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from io import BytesIO
import datetime

# Authenticate and initialize PyDrive
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

drive = authenticate_drive()

st.title("Weekly Customer Email Processor")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df_new = pd.read_csv(uploaded_file)
    st.write("Uploaded DataFrame:")
    st.write(df_new)

    # Get the current date and generate the filename
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'customer_emails_{current_date}.csv'

    # Save the uploaded file to Google Drive
    file_drive = drive.CreateFile({'title': filename})
    file_drive.SetContentFile(uploaded_file.name)
    file_drive.Upload()
    st.write(f'File uploaded to Google Drive as {filename}')

    # List files in Google Drive and filter by date
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    date_threshold = datetime.datetime.now() - datetime.timedelta(weeks=2)
    recent_files = [
        file for file in file_list
        if datetime.datetime.strptime(file['title'].split('_')[-1].replace('.csv', ''), '%Y-%m-%d') >= date_threshold
    ]

    # Collect emails from recent files
    recent_emails = set()
    for file in recent_files:
        file_drive = drive.CreateFile({'id': file['id']})
        file_drive.GetContentFile(file['title'])
        df = pd.read_csv(file['title'])
        recent_emails.update(df['email'])

    # Filter out recent emails from the new dataframe
    df_filtered = df_new[~df_new['email'].isin(recent_emails)]

    # Display filtered dataframe
    st.write("Filtered DataFrame:")
    st.write(df_filtered)

    # Download the filtered dataframe
    def to_csv(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        processed_data = output.getvalue()
        return processed_data

    st.download_button(label="Download filtered data as CSV",
                       data=to_csv(df_filtered),
                       file_name='filtered_customer_emails.csv',
                       mime='text/csv')
