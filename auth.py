import streamlit as st
import streamlit_authenticator as stauth


@st.cache_data
def get_credentials():
    return {
        "usernames": {
            "admin": {
                "name": "Store Manager",
                "password": stauth.Hasher.hash(st.secrets["passwords"]["admin"]),
            },
            "staff1": {
                "name": "Checkout Staff",
                "password": stauth.Hasher.hash(st.secrets["passwords"]["staff1"]),
            },
        }
    }


def authenticate_user():
    """Renders the login form and halts the app if the user is not authenticated."""
    authenticator = stauth.Authenticate(
        get_credentials(),
        cookie_name="grocery_dashboard_session",
        cookie_key=st.secrets["cookies"]["key"],
        cookie_expiry_days=30,
    )

    authenticator.login()

    if st.session_state["authentication_status"] is False:
        st.error("😕 Invalid username or password.")
        st.stop()
    elif st.session_state["authentication_status"] is None:
        st.stop()
    else:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.write(f"👤 Welcome, **{st.session_state['name']}**")
        return True
