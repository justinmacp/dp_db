"""
The Streamlit Interface

Start with:

streamlit run app.py

TODO: Write a registration page, that will add a new user to the credentials.yml and the USERS table in titanic.db
TODO: Add Logout function
TODO: Dashboard: add column selector for average and sum
TODO: Dashboard: add more mechanisms
TODO: Write privacy budget reset script (to be scheduled to regularly reset the budget)

"""


import streamlit as st
import navigation_bar
import yaml
import streamlit_authenticator as stauth


CREDENTIALS = 'data/credentials.yml'

with open(CREDENTIALS) as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)


navigation_bar.make_sidebar()

try:
    authenticator.login()
except Exception as e:
    st.error(e)


if st.session_state['authentication_status']:
    st.switch_page("pages/dashboard.py")
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')
