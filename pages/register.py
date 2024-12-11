import streamlit as st


try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
except Exception as e:
    st.error(e)