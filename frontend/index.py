import streamlit as st
from streamlit_navigation_bar import st_navbar
import pages as pg
import os
st.set_page_config(initial_sidebar_state="collapsed", layout="centered", page_title="Tourist Itinerary Builder", 
                   page_icon="🌍")

# pages = ["Install", "User Guide", "API", "Examples", "Community", "GitHub"]
pages = ["Home", "Poi"]
parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "./assest/logo.svg")
# urls = {"GitHub": "https://github.com/gabrieltempass/streamlit-navigation-bar"}
styles = {
    "nav": {
        "background": "royalblue",
        "justify-content": "left",
        
    },
    "img": {
        "padding-right": "14px",
        "width": "200px",
        "height": "150px"
    },
    "span": {
        "color": "white",
        "padding": "4px",
    },
    "active": {
        "background-color": "white",
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "10px",
    }
}
options = {
    "show_menu": False,
    "show_sidebar": False,
}

page = st_navbar(
    pages,
    logo_path=logo_path,
    # urls=urls,
    styles=styles,
    options=options,
)
 
functions = {
    "Home": pg.show_home,
    # "Cities": pg.show_install,
    # "Route": pg.show_user_guide,
    # "Chat": pg.show_api,
    "Poi": pg.show_poi
}
go_to = functions.get(page)
if go_to:
    go_to()








