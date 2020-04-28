# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import altair as alt
from altair import datum
import geopandas as gpd
import panel as pn

alt.renderers.enable('altair_viewer')
alt.data_transformers.disable_max_rows() #disable the max row limitation of 5000

olympic_original = pd.read_csv("https://raw.githubusercontent.com/FitzWang/data-visualization/master/athlete_events.csv")

olympic_group_sport = olympic_original.dropna(subset=['Height', 'Weight']).groupby(['Sport']).agg('mean').round(2)
olympic_count_sport = olympic_original.groupby(['Sport']).count().reset_index().filter(["Sport","ID"]).rename(columns={"ID":"count"})
olympic_weight_height_mean = pd.merge(olympic_group_sport,olympic_count_sport,on="Sport")

Olympic_weight_height = alt.Chart(olympic_weight_height_mean).mark_circle().encode(
    x = alt.X(field = "Height", type = "quantitative", scale=alt.Scale(domain=[162, 192]),
              axis=alt.Axis(labelFontSize = 18,titleFontSize=20)),
    y = alt.Y(field = "Weight", type = "quantitative",scale=alt.Scale(domain=[45, 95]),
               axis=alt.Axis(labelFontSize = 18,titleFontSize=20)),
    color =  alt.Color('Sport:N',scale=alt.Scale(scheme='category20'),
                       legend=alt.Legend(labelFontSize = 15,titleFontSize=20)),
    size = alt.Size('count:Q',scale=alt.Scale(domain=[1,40000], range=[200,2000]),
                    legend=alt.Legend(labelFontSize = 15,titleFontSize=20)),
    tooltip=['Height:N','Weight:N','Sport:N','count:N']
).properties(
    width=1000,
    height=600
)
Olympic_weight_height

olympic_bar_height = alt.Chart(olympic_weight_height_mean).mark_bar(opacity=0.8,size=20).encode(
    alt.X('Height:Q', axis=alt.Axis(labels=False, title=None), scale=alt.Scale(domain=[163, 190])),
    alt.Y('count:Q', stack="zero",axis=alt.Axis(title=None)),
    color =  alt.Color('Sport:N',scale=alt.Scale(scheme='category20'))
).properties(width=1000,height = 100)

olympic_bar_weight = alt.Chart(olympic_weight_height_mean).mark_bar(size=20,opacity=0.8,orient="horizontal").encode(
    alt.X('count:Q', axis=alt.Axis(title=None), stack="zero"),
    alt.Y('Weight:Q', axis=alt.Axis(labels=False, title=None)),
    color =  alt.Color('Sport:N',scale=alt.Scale(scheme='category20'))
).properties(height = 600,width=100)

(olympic_bar_height&(Olympic_weight_height|olympic_bar_weight))
