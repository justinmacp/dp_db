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
