import streamlit as st
import pandas as pd
from datetime import date

df = pd.read_csv("avocado.csv")

# 날짜 데이터를 문자열에서 날짜 데이터 형식으로 옮깁니다.
df['date'] = df['date'].apply(lambda x: date.fromisoformat(x))

# [TODO] 테이블을 출력해봅니다.
st.dataframe(df)