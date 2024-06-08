import streamlit as st
import pandas as pd
from io import BytesIO

st.title("CSV File Uploader and Downloader")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display the dataframe
    st.write("Uploaded DataFrame:")
    st.write(df)

    # Perform some basic manipulation
    df['New_Column'] = df.iloc[:, 0] * 2  # Example manipulation
    
    # Display the manipulated dataframe
    st.write("Manipulated DataFrame:")
    st.write(df)

    # Download the manipulated dataframe
    def to_csv(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        processed_data = output.getvalue()
        return processed_data

    st.download_button(label="Download data as CSV",
                       data=to_csv(df),
                       file_name='manipulated_data.csv',
                       mime='text/csv')
