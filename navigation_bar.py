import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import time


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    """
    Creates the sidebar with the navigation functionality.
    """
    with st.sidebar:
        st.title("Differential Privacy Tool")
        st.write("")
        st.write("")

        if st.session_state.get("authentication_status", False):
            st.page_link("pages/dashboard.py", label="dashboard")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "login":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("login.py")


def logout():
    """
    Implements the logout function by clearing the session state and redirecting to the login page.
    """
    st.session_state['logout'] = True
    st.session_state['name'] = None
    st.session_state['username'] = None
    st.session_state['authentication_status'] = None
    st.session_state['email'] = None
    st.session_state['roles'] = None
    st.session_state['privacy_budget'] = None
    st.info("Logged out successfully!")
    time.sleep(0.5)
    st.switch_page("login.py")
