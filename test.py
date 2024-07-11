import streamlit as st

# Sample data for demonstration
data = {
    "Option 1": "This is the content for Option 1.",
    "Option 2": "Some different content for Option 2.",
    "Option 3": "And yet another type of content for Option 3."
}

st.title("Dynamic Content with Checkbox")

files = [f"file_{i}.csv"  for i in [1, 2, 3]]

selected_option = st.selectbox("Remove duplicates from:", options=['last 2 weeks', 'last week', 'none'])

st.write('Emailing:')
st.write(files[0])

if selected_option == 'last 2 weeks':
    st.write('except emails from:')
    st.write(files[1])
    st.write(files[2])
elif selected_option == 'last week':
    st.write('except emails from:')
    st.write(files[1])
elif selected_option == 'none':
    pass