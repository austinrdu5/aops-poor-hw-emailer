from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from googleapiclient.http import MediaIoBaseUpload


# Function to authenticate with Google Drive
def authenticate(service_account_info):
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
# Returns a list of dictionaries with file ID and name
def list_csv_info(service, n, folder_id):
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            orderBy='name',
            fields='nextPageToken, files(id, name)'
        ).execute()
        items = results.get('files', [])
        return items[:-(n+1):-1]
    except Exception as e:
        st.error(f"Error accessing files: {e}")
        st.stop()

# Helper function to read CSVs by ID
def read_csv(service, file_id):
    try:
        request = service.files().get_media(fileId=file_id)
        response_content = request.execute()
        return pd.read_csv(BytesIO(response_content))
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Function that takes a pandas series and returns a string with Oxford comma
def _oxford_comma(series):
    # remove duplicates with set
    seen = set()
    str_list = [x for x in series if not (x in seen or seen.add(x))]

    if len(str_list) == 1:
        return str_list[0]
    elif len(str_list) == 2:
        return str_list[0] + ' and ' + str_list[1]
    else:
        return ', '.join(str_list[:-1]) + ', and ' + str_list[-1]

# Helper function to combine rows with the same students and classes
# Assumes df only has students of the same class level (1, 2, or 3)
def _combine_siblings_and_classes(df):

    combined = df.groupby('email').agg({'student name': _oxford_comma,
                                        'class name': _oxford_comma,
                                        'primary parent': 'first'}).reset_index()

    return combined

# Function to process most recent CSVs, returns list of DataFrames
def process_dfs(*args):
    try:
        # handle different number of arguments
        if len(args) == 0:
            st.warning("Not enough files in the folder to process.")
            st.stop()
        elif len(args) == 1:
            to_email = args[0]
        else:
            if len(args) == 2:
                current = args[0]
                previous = args[1]
            else:
                current = args[0]
                previous1 = args[1]
                previous2 = args[2]

            # TODO: add conditional check here
            previous = pd.concat([previous1, previous2])

            # remove rows in current_df that occur in previous_df
            merged_df = current.merge(previous, how='left', indicator=True)
            to_email = merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge')

        # rename email column to 'email' (Front requires this)
        to_email = to_email.rename(columns={'primary parent email': 'email'})

        # in student name, only keep first name
        to_email['student name'] = to_email['student name'].str.split().str[0]

        # in parent name, change to title case
        to_email['primary parent'] = to_email['primary parent'].str.title()

        # only keep columns email, student name, and class name
        to_email = to_email[['email', 'student name', 'class name', 'primary parent']]

        # split into lower, middle, and upper class levels
        lower = to_email[to_email['class level'] == 1].drop(columns=['class level'])
        middle = to_email[to_email['class level'] == 2].drop(columns=['class level'])
        upper = to_email[to_email['class level'] == 3].drop(columns=['class level'])

        # combine siblings and classes
        lower = _combine_siblings_and_classes(lower)
        middle = _combine_siblings_and_classes(middle)
        upper = _combine_siblings_and_classes(upper)

        return [lower, middle, upper]   

    except Exception as e:
        st.error(f"Error while processing CSVs: {e}")
        st.stop()

# Function to download CSV to user's local machine
def download_csv(df, file_name):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)
