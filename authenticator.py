import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['abc', 'def'])

print(hashed_passwords)
