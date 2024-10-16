import pandas as pd
import plotly.express as px
import numpy as np

df = pd.read_csv("tests/tree_data_q1.csv")

df["Accuracy (%)"] = df["open-ai-gpt-4-0613"] * 100

fig = px.treemap(
    df,
    names=df["label"],
    values=df["assessment count"],
    ids=df["synset_id"],
    parents=df["parent_synset"],
    color="Accuracy (%)",
    color_continuous_scale="RdBu",
)
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
fig.show()
