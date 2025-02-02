"""
The Streamlit Interface

Start with:

streamlit run login.py

TODO: unit tests for the required functions
TODO: Fix dashboard script: cleanup conditional statements
TODO: The sum mechanism causes a data leak: if a user asks for the sum and specifies 1 as lower and upper bound an exact
 count is given
TODO: Dashboard: implement selector for multiple tables
TODO: Dashboard: add more mechanisms
TODO: Find a scheduler for the privacy budget reset script (cron job): add this to readme
"""


import streamlit as st
import navigation_bar
import yaml
import streamlit_authenticator as stauth
from src.utils import consts


with open(consts.CREDENTIALS) as file:
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
