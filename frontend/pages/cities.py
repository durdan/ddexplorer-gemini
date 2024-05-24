import streamlit as st
import pandas as pd

# Read data from CSV file
df = pd.read_csv("./assest/worldcities.csv")

# Group the data by 'country'
grouped_df = df.groupby('country')

# Display each group separately
for country, data in grouped_df:
    st.subheader(country)
    st.table(data)
