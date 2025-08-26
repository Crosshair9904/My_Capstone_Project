import streamlit as st
from supabase import create_client, Client
import webbrowser



#TO RUN APP: RUN THE CODE AND TAKE THE PATH AND USE THE RUN COMMAND IN TERMINAL

#all the pages setup
#logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("services/settings.py", title="Settings", icon=":material/settings:")

home = st.Page(
"services/home.py",
title="Home",
icon=":material/home:",
)
ai = st.Page("services/ai.py", title="Ai Tools", icon=":material/network_intelligence:")

#defines page groups
account_pages = [settings]
services_pages = [home, ai]

page_dict = {}
page_dict["Services"] = services_pages


if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)

pg.run()


