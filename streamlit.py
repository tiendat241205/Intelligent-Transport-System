import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
from datetime import datetime
import plost
import os
from PIL import Image

import pyrebase
import pandas as pd
import json

firebaseConfig = {
  'apiKey': "AIzaSyCGG-jBPJnckskxmh2WpUlbAdsTonyeTyc",
  'authDomain': "intelligent-transport-b2268.firebaseapp.com",
  'databaseURL': "https://intelligent-transport-b2268-default-rtdb.firebaseio.com",
  'projectId': "intelligent-transport-b2268",
  'storageBucket': "intelligent-transport-b2268.appspot.com",
  'messagingSenderId': "576496544016",
  'appId': "1:576496544016:web:6cff7ea5d7c1bf79361d95",
  'measurementId': "G-P8VWLSMBPG"
};



firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
email = 'admin@gmail.com'
password = '123456'
auth.sign_in_with_email_and_password(email, password)
print("successfully signed in!")




def get_json():
  people = db.get().val()['people']
  data = {'people':people}
  data = json.dumps(data)
  return data



def get_human_count():
  people = db.get().val()['people']
  time =[]
  count = []
  for key,val in people.items():
    time.append(key)
    count.append(val)
  df = pd.DataFrame(list(zip(time, count)),columns =['TimeStamp', 'People'])
  return df


### Seting current working
owd = os.getcwd()

st.set_page_config(
    page_title = 'Intelligent Transport Alert – ITA',
    page_icon = '✅',
    layout = 'wide',
    menu_items={'About': """# Recorded Data from Camera 
                            This is an *extremely* cool app!"""}    
)

# dashboard title
st.title("Intelligent Transport Alert – ITA")

DATE_COLUMN = 'TimeStamp'


def load_data():
# Load data into the dataframe.
    ##### HUMAN COUNT ####
    human_count = get_human_count()
    human_count['TimeStamp'] = pd.to_datetime(human_count['TimeStamp'])
    return human_count

@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Đang cập nhật dữ liệu')
human_count = load_data()

# Notify the reader that the data was successfully loaded.
data_load_state.text('Cập nhật dữ liệu thành công!')


#### Make output dir
try:
    os.mkdir('output')
except:
    pass


##### SIDEBAR ####
with st.sidebar:
    #### QUERY TIME ####
    st.header("OPTIONAL")
    if st.button('Reload'):
        human_count = load_data()
    start_dt = st.sidebar.date_input('Start Time', value=human_count['TimeStamp'].min())
    human_count = human_count[human_count['TimeStamp'] > datetime(start_dt.year, start_dt.month, start_dt.day)]
    type_dashboard = st.radio("Choose Type of Dashboard for show:", ('RealTime', 'RangeTime'))
    if type_dashboard == 'RangeTime':
        end_dt = st.sidebar.date_input('End Time', value=human_count['TimeStamp'].max())
        if start_dt <= end_dt:
            human_count = human_count[human_count['TimeStamp'] < datetime(end_dt.year, end_dt.month, end_dt.day+1)]
        else:
            st.error('Start date must be > End date')
        

    ## Checkbox show data
    show_data = st.checkbox('Show data')   


    json_data = get_json()
    json_button = st.download_button(label="Download JSON",
    file_name="data.json", mime="application/json",data=get_json())
    if json_button:
        st.success("Already export data to JSON!")
    st.json(json_data, expanded=False)
    ### Message
    with st.spinner("Loading..."):
        time.sleep(1)
    



about_tab, people_tab= st.tabs(["About the Project", "Mật độ giao thông"])

#### Tab giới thiệu
with about_tab:
    st.header("Project")
    Mohinh= st.image('mohinh.jpg', caption = 'Architecture')
    st.subheader("Giới thiệu")
    Gioithieu = st.image('giới thiệu.jpg', caption='Giới thiệu về dự án')
    
    
    
    
# Tab số liệu 
with people_tab:

    current_people = np.array(human_count['People'])

    if current_people[-1] <= 7:
        st.success(f'Mật độ: bình thường')
    # elif <điều kiện>:
    #     câu lệnh .... 
    elif current_people[-1] < 12:
        st.success(f'Mật độ: khá đông')
    elif current_people[-1] < 17:
        st.success(f'Mật độ: đông') 
        st.error(f'Mật độ: rất đông')



    if type_dashboard == 'RealTime':
        tit, cur_time =  st.columns(2)
        tit.header("People Counting")
        t = datetime.now()
        t = t.strftime("%Y-%m-%d %H:%M:%S")
        cur_time.header(f'{t}')    


    a, curr, avg , b =  st.columns(4)
    with curr:
        current_people = np.array(human_count['People'])
        st.metric(label='Current People', value=f"{current_people[-1]}")
    with avg:
        st.metric(label='AVG People', value=f"{human_count['People'].mean():.0f}")

    if show_data:
        graph, data_col= st.columns([3, 1])
        with graph:
            plost.line_chart(  human_count, x='TimeStamp',  # The name of the column to use for the x axis.
                y= ( 'People'), height=400,pan_zoom='minimap')
        with data_col:
            st.subheader('Data Record')
            human_count = human_count.sort_values(by=['TimeStamp'])
            st.write(human_count)
        ## Button Export CSV
            csv = convert_df(human_count)
            people = st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='human_count.csv',
                    mime='text/csv')
            if people:
                st.success("Data downloaded successfully!")
    else:
        plost.line_chart( human_count, x='TimeStamp',  # The name of the column to use for the x axis.
                        y= ( 'People'),pan_zoom='minimap')    

# https://plost.streamlitapp.com/
# https://github.com/Socvest/streamlit-on-Hover-tabs
# https://github.com/PablocFonseca/streamlit-aggrid
