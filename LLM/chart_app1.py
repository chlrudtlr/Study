import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(layout="wide")

df = pd.read_csv("avocado.csv")
df['date'] = df['date'].apply(lambda x: date.fromisoformat(x))

# Boston, California, Los Angeles 에 대한 line chart를 갖는 그래프
plot_table = {
    "geography": [
        "Boston",
        "California",
        "Los Angeles"
    ]
}

line_chart = []

# [TODO] 선 그래프로 그려질 숫자들을 담아봅니다.
for i in plot_table["geography"]:
    line_chart.append(list(df[df["geography"] == i]["average_price"]))

plot_table["line"] = line_chart

st.dataframe(plot_table,
             column_config={
                 "line": st.column_config.LineChartColumn(
                     "Average Price",
                     width="medium"
                 )
             })
