import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

@st.cache #use @st.cache decorator to cache the data, so it don't need to load data every panel update
def load_data(filename):  #function to load data
    df=pd.read_excel(filename)
    return df

def caculate(df, column): #function to caculate statistical data
    describe = df[column].describe() #use pandas to caculate mean, max, min and so on
    mode = df[column].mode()[0] #use pandas mode to caculate mode
    median = df[column].median() #use pandas median to caculate median
    price_dict = {"Mean":describe[1],"Std":describe[2],"median":median,"mode":mode,"min":describe[3],"25%":describe[4],"50%":describe[5],"75%":describe[6],"max":describe[7]}
    return price_dict # create dict, which include all statistical data and columns name

def caculate_distance(position,df): # use Euclidean distance  as two points distance
    lat = float(position.split(";")[0].strip())#get the lat and lon
    lon = float(position.split(";")[1].strip())
    return np.sqrt((df["lat"] - 100) ** 2 + (df["lon"] - 200) ** 2)

def main_panel():  # main function, mainly used to layout widget and response for user input
    df = load_data("cl_used_cars_7000_sample.xlsx") #df is a dataframe which contain all info in the excel
    st.title("Used cars for sale on Craigslist :sunglasses:") # set title
    df = df.rename (columns = {"long":"lon"}) #rename column name from long to lon
    df_new = df[["lat","lon"]].dropna(axis=0, how='any') #delete the rows which lat or lon is missing
    if st.sidebar.checkbox('Show Distribution map'): #if the checkbox is selected
        st.markdown("")
        st.markdown('Distribution map, based on lat and lon')
        st.map(df_new,zoom=1) # show map
    if st.sidebar.checkbox('Show Price Distribution'):
        st.markdown('')
        st.markdown('Show statistical price:')
        data = caculate(df, "price")
        df1 = pd.DataFrame()
        df1 = df1.append(data, ignore_index=True)
        df1.index = ["price"]
        st.table(df1) #show totle distribution for price
        df2 = df[df["price"] < 80000]

        fig, (ax0, ax1) = plt.subplots(nrows=2, figsize=(9, 6))
        ax0.hist(df.price, 40, histtype='bar', facecolor='yellowgreen', alpha=0.75)

        ax0.set_title('Price Distrbution')
        ax0.set_ylabel('used cars number', fontdict={'weight': 'normal', 'size': 10})
        ax1.hist(df2.price, 20, histtype='bar', facecolor='pink', alpha=0.75, cumulative=False, rwidth=0.8)

        ax1.set_title("Price Distrbution(Detial)") # when price> 8000, there is few cars, so we focus on the price < 8000
        fig.subplots_adjust(hspace=0.4)
        plt.xlabel('price', fontdict={'weight': 'normal', 'size': 10})
        ax1.set_ylabel('used cars number', fontdict={'weight': 'normal', 'size': 10})
        st.markdown('Show price distrbution:')
        st.pyplot(fig)

    st.markdown("")
    st.markdown('Filter Used Cars infomation')
    state = df['state'].unique().tolist() # filter based on state
    if np.nan in state:
        state.remove(np.nan)
    selected_state = st.selectbox("which state do you want to check ??",state)
    manufacturers = df['manufacturer'].unique().tolist() # filter based on manufacturers
    if np.nan in manufacturers:
        manufacturers.remove(np.nan)
    selected_manufacturers = st.multiselect('which manufacturer do you like ???',manufacturers)
    price_str = st.text_input('Enter Price you want to search, format like 10000-2000')# filter based on price range
    models = df.model.unique().tolist()
    if np.nan in models:
        models.remove(np.nan)
    selected_model = st.multiselect('which model do you like ???', models)# filter based on model
    conditions = df.condition.unique().tolist()
    conditions.remove(np.nan)
    selected_conditions = st.multiselect("which conditions do you want to check ??", conditions) ## filter based on cars condition
    drives = df.drive.unique().tolist()
    drives.remove(np.nan)
    selected_drives = st.multiselect("which drives do you like ??", drives)
    types = df.type.unique().tolist()
    types.remove(np.nan)
    selected_types = st.multiselect("which types do you like ??", types) # filter based on cars type
    paint_color = df.paint_color.unique().tolist()
    paint_color.remove(np.nan)
    selected_paint_color = st.multiselect("which paint color do you like ??", paint_color)# filter based on paint_color

    # based on selected conditions, filter data used pandas
    if selected_state!="":
        df = df[df["state"]==selected_state ]

    if selected_manufacturers!=[]:
        for manufacturer in selected_manufacturers:
            df = df[df["manufacturer"]==manufacturer ]
    if price_str!="":
        price_min = int(price_str.split("-")[0])
        price_max = int(price_str.split("-")[1])
        df = df[(df["price"]>=price_min) & (df["price"]<=price_max)]

    if selected_model!= []:
        for model in selected_model:
            df = df[df["model"]==model ]
    if selected_conditions!= []:
        for condition in selected_conditions:
            df = df[df["condition"]==condition ]
    if selected_drives!=[]:
        for drive in selected_drives:
            df = df[df["drive"]==selected_drives ]
    if selected_types!=[]:
        for type in selected_types:
            df = df[df["type"]==type ]

    if selected_paint_color != []:
        for c in selected_paint_color :
            df = df[df["paint_color"]==c ]
    # if show result is selected, there will appear two checkbox, used for sort records. if show by distance is selected,
    # it will need to input your position with format "lat;lon". then can caculate distance, and create a new column named distance
    #to store this value. if only this check box is selected, sort by distance. if sorted by time is also selected, sort by distance
    # and posting time. if only show result by time,sort by posting time.
    # if no sort checkbox is selected, show result table normal
    if st.checkbox('Show Result'):
        if st.sidebar.checkbox('Show Result By distance'):
            position = st.text_input('Enter Your position, format as lat;long')
            if position !="":
                df["distance"] = caculate_distance(position,df)
            if st.sidebar.checkbox('Show Result By posting time'):
                if "distance" in df.columns:
                    df_sort_multi = df.sort_values(by=['posting_date', "distance"])
                    st.table(df_sort_multi)
                else:
                    st.markdown('Warining: You should input your position first!!! :smile:')
            else:
                if "distance" in df.columns:
                    df_sort_distance = df.sort_values(by='distance')
                    st.table(df_sort_distance)
                else:
                    st.markdown('Warining: You should input your position first!!! :smile:')
        elif st.sidebar.checkbox('Show Result By posting time'):
            df_sort_time = df.sort_values(by='posting_date', ascending=False)
            st.table(df_sort_time)

        else:
            st.table(df)

main_panel()







# st.markdown('####Used cars for sale on Craigslist :sunglasses:')
# x = st.slider('输入一个数字')
# st.write(x, '的三次方为：', x**3)
# st.markdown('> Streamlit挺好用 :+1:')
