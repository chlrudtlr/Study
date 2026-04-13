import streamlit as st
import pandas as pd
from datetime import date

df = pd.read_csv("avocado.csv")
df['date'] = df['date'].apply(lambda x: date.fromisoformat(x))

plot_table = {
    "geography": [
        "Boston",
        "California",
        "Los Angeles"
    ]
}

# bar chart를 위한 pivot table을 만듭니다.
pivot_df = pd.pivot_table(df, index="date",columns=["geography","type"])

# [TODO] bar chart를 시각화합니다.
st.______________________________