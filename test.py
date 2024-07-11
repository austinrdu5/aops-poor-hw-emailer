import streamlit as st

# Sample data for demonstration
data = {
    "Option 1": "This is the content for Option 1.",
    "Option 2": "Some different content for Option 2.",
    "Option 3": "And yet another type of content for Option 3."
}

st.title("Dynamic Content with Checkbox")

selected_option = st.checkbox("Show Option 1")
22222221
if selected_option:
    st.write(data["Option 1"])
else:
    # Get the selected options from the previous session
    if 'selected_options' not in st.session_state:
        st.session_state['selected_options'] = []
    selected_options = st.session_state['selected_options']

    # Create a multiselect widget to allow the user to select multiple options
    options = st.multiselect("Select options:", list(data.keys()), default=selected_options)

    # Update the selected options in the session state
    st.session_state['selected_options'] = options

    # Display the selected options
    for option in options:
        st.write(data[option])