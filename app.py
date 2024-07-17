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
st.write("This app uses [AoPS Poor Homework Reports](https://sandiego-cv.aopsacademy.org/reports/poor-hw-performance) to generate CSVs for weekly sequence emailing." +
         " You can get a report by using the 'Export to CSV' button.")
st.write("To begin, upload the most recent Poor Homework Report (into [this Google Drive folder](https://drive.google.com/drive/folders/1pS27r6Hpb_a17kmQPURIRNfS2RYUnZc5) and refresh the page. " +
         "Since files are sorted by name, please maintain the preexisting naming conventions (poor_hw_reportYYYY-MM-DD... .csv) so the app can detect which Reports are most recent.")

# Authenticate
if 'service' not in st.session_state:
    st.session_state['service'] = authenticate(service_account_info)
service = st.session_state['service']

# Get most recent files in the folder
if 'csv_list' not in st.session_state:
    st.session_state['csv_list'] = list_csv_info(service, 3, CSV_FOLDER_ID)
csv_list = st.session_state['csv_list']

# Early termination
if len(csv_list) == 0:
    st.error(f"No files detected in Google Drive folder.")
    st.stop()

st.header('Customization')
st.write("If a student consistently shows up in the Poor HW Reports and you want to avoid emailing those parents too frequently, you can omit repeated emails from up to two prior reports here.")

# Dynamically display most recent files 
option1 = 'Prior 2 weeks'
option2 = 'Prior week'
option3 = 'Keep all emails'
selected_option = st.selectbox("Remove repeated emails from:", options=[option1, option2, option3])

with st.container():
    
    st.write('The final result will include parent emails from this file:')
    st.write("- " + csv_list[0]['name'])

    st.write("But exclude parent emails from these files:")
    if selected_option == option1:
        st.write("- " + csv_list[1]['name'])
        st.write("- " + csv_list[2]['name'])
    elif selected_option == option2:
        st.write("- " + csv_list[1]['name'])
    elif selected_option == option3:
        st.write("No emails to be omitted.")

with st.container():
    st.header("Download Sequence CSVs")
    st.write("Use the button below to generate CSVs for use with Front's sequence emailer. " +
             "These are designed for the templates titled \"Poor HW Report\" and should have columns email, student name, class name, and primary parent.")

    # Button to process and download CSVs
    if st.button("Get this week's sequence CSVs"):
        with st.spinner("Processing emails..."):

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
                download_csv(lower, f"lower_{date_string}.csv", "CSV for lower-level students")
                download_csv(middle, f"middle_{date_string}.csv", "CSV for mid-level students")
                download_csv(upper, f"upper_{date_string}.csv", "CSV for upper-level students")