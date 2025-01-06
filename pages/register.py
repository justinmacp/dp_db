import streamlit as st
import yaml
import streamlit_authenticator as stauth
from src.utils.consts import CREDENTIALS, DATABASE
from src.utils import io


with open(CREDENTIALS) as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

try:
    email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user()
    if email_of_registered_user:
        st.success('User registered successfully')
        with open(CREDENTIALS, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        io.update_database(
            f"INSERT INTO users ('name', 'max_privacy_budget', 'current_privacy_budget') VALUES "
            f"('{username_of_registered_user}',100.0,100.0)", DATABASE, modify=True
        )

except Exception as e:
    st.error(e)
