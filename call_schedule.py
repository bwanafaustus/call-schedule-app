import streamlit as st
import pandas as pd
import datetime
import pyodbc

@st.cache_resource
def init_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
            + st.secrets["secrets"]["SERVER"]
            + ";DATABASE="
            + st.secrets["secrets"]["DATABASE"]
            + ";UID="
            + st.secrets["secrets"]["UID"]
            + ";PWD="
            + st.secrets["secrets"]["PWD"]
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

conn = init_connection()

st.title('TBL VISITS SCHEDULE')

# Load BDR base
bdr_base = r'C:\Users\C_regnafau\OneDrive - Anheuser-Busch InBev\Attachments\PYTHON\DATA\bdr_base.csv'

@st.cache_data
def load_bdr(filepath):
    data = pd.read_csv(filepath)
    return data

data = load_bdr(bdr_base)

# Select BDR Name
name = st.selectbox("Choose BDR Name:", data['bdr_name'].unique())

# Select Date
d = st.date_input("Choose Date:", datetime.date.today())

#Retrieving data from database
@st.cache_data
def run_query(query):
    try:
        data = pd.read_sql(query, conn)
        data['date'] = pd.to_datetime(data['date']).dt.date
        return data
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return []

visits = run_query("""SELECT A.*,B.latitude, B.longitude
                    FROM TZ_Visits_Schedule_2025 A
                    LEFT JOIN RTMDB.dbo.KUJA_CUST_SEP B ON A.accountId=B.account_id""")


visits = visits[(visits['bdr_name'] == name) & (visits["date"] == d)]
visits['latitude'] = visits['latitude'].astype(float)
visits['longitude'] = visits['longitude'].astype(float)

st.write(f'Number of visits: {visits.shape[0]}')

if st.checkbox(f'Show POC list'):
    st.dataframe(visits,hide_index=True)

st.subheader('Map of pocs')
st.map(visits)





















