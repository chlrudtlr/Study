import streamlit as st
import pandas as pd
from datetime import date

df = pd.read_csv("avocado.csv")
df['date'] = df['date'].apply(lambda x: date.fromisoformat(x))

# [TODO] 테이블을 수정 가능한 테이블로 출력해봅니다.
new_df = st.data_editor(df)