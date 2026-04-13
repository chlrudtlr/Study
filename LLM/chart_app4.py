import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

df = pd.read_csv("avocado.csv")
df['date'] = df['date'].apply(lambda x: date.fromisoformat(x))




# [TODO] 선을 그릴 요소를 선택하는 widget을 기입합니다. selectbox사용, pandas unique()메소드 사용
selected_geography = st._____________________________
submitted = st.button('Submit')

# [TODO] plotly라이브러리를 사용해서 시각화합니다.
if submitted:
    filtered_avocado = df[df['geography'] == selected_geography]
    line_fig = px.line(filtered_avocado,
                       # [TODO]x에 date, y에 average_price 값을 지정합니다.
                       _______________________
                       color='type',
                       title=f'Avocado Prices in {selected_geography}')
    st.plotly_chart(line_fig)