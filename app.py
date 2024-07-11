from funcs import *
import streamlit as st
import datetime as dt

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

# -- Begin Streamlit App --

st.title("SDCV Poor HW Emailer")
st.write("This app processes a CSV file of student information and sends emails to parents who have not completed homework.")

# Authenticate
service = authenticate(service_account_info)

# Display most recent files
with st.container():
    st.header("Most recent files in folder (alphabetically):")

    # Get most recent files in the folder
    csv_list = list_csv_info(service, 3, CSV_FOLDER_ID)

    if not csv_list:
        st.write('No files found.')
    else:
        for item in csv_list:
            st.write(f"- {item['name']}") 

st.write("To add a new file, please upload a CSV into [this Google Drive folder](https://drive.google.com/drive/folders/1pS27r6Hpb_a17kmQPURIRNfS2RYUnZc5). \
         Please note that the app uses the file names to sort by newest, so please following the preexisting naming conventions (poor_hw_reportYYYY-MM-DD... .csv).")

with st.container():
    st.header("Generate CSVs for this week's sequence emails")

    st.write("This will process the three most recent files in the folder and generate three CSVs for lower-, middle-, and upper-level students respectively. \
             Behind the scenes, the app will omit emails that have already been sent in the previous 2 weeks ()")

# Button to process and download CSVs
if st.button("Get this week's sequence CSVs"):
    with st.spinner("Processing reports..."):

        if len(csv_list) == 0:
            st.warning("Not enough files in the folder to process.")
            st.stop()
        else:
            # convert CSVs to DataFrames
            df_list = [read_csv(service, item['id']) for item in csv_list]

            # process DataFrames into lower, middle, and upper 
            lower, middle, upper = process_dfs(*df_list)

            # get date as string
            date_string = dt.datetime.now().strftime("%Y-%m-%d")

            # download DataFrames as CSVs
            download_csv(lower, f"lower_{date_string}.csv")
            download_csv(middle, f"middle_{date_string}.csv")
            download_csv(upper, f"upper_{date_string}.csv")
