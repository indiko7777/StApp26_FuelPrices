# all chart functions, so every chart has the same style
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# strong colors that are easy to see on a white background
FUEL_COLORS = {"Diesel": "#0057B8", "E10": "#E07B00", "SP98": "#00875A"}
RED = "#D62728"
BLUE = "#0057B8"
BLACK = "#222222"
PRICE_LABEL = "Price (€/L)"

# blue = cheaper, red = more expensive (same on every chart)
DIVERGING = "RdBu_r"

EVENTS = [
    ("2020-03-17", "COVID lockdown"),
    ("2022-02-24", "War in Ukraine"),
]
DISCOUNT = ("2022-04-01", "2022-12-31")


def _style(fig, height=420):
    fig.update_layout(template="simple_white", height=height, font=dict(size=14),
                      margin=dict(l=10, r=10, t=30, b=10), legend_title_text="", hovermode="x unified")
    fig.update_yaxes(showgrid=True, gridcolor="#e6e6e6")
    return fig


def _add_events(fig, start, end):
    for date, text in EVENTS:
        d = pd.Timestamp(date)
        if start <= d <= end:
            fig.add_shape(type="line", x0=d, x1=d, y0=0, y1=1, yref="paper",
                          line=dict(color=RED, width=3, dash="dash"))
            fig.add_annotation(x=d, y=1, yref="paper", text=f"<b>{text}</b>", showarrow=False,
                               yanchor="bottom", font=dict(color=RED, size=13))
    d0, d1 = pd.Timestamp(DISCOUNT[0]), pd.Timestamp(DISCOUNT[1])
    if start <= d1 and d0 <= end:
        fig.add_vrect(x0=d0, x1=d1, fillcolor=RED, opacity=0.12, line_width=0)
        fig.add_annotation(x=d0 + (d1 - d0) / 2, y=0.03, yref="paper", text="<b>State discount</b>",
                           showarrow=False, font=dict(color=RED, size=13))


def fuel_lines(df, y="avg_price", ylabel=PRICE_LABEL, fmt=".3f", unit=" €/L", ref=None, end_labels=True):
    """one line per fuel, with the fuel name written at the end of each line"""
    fig = go.Figure()
    for fuel, color in FUEL_COLORS.items():
        d = df[df["fuel"] == fuel].sort_values("month")
        if d.empty:
            continue
        fig.add_trace(go.Scatter(x=d["month"], y=d[y], name=fuel, mode="lines",
                                 line=dict(color=color, width=3),
                                 hovertemplate=f"{fuel}: %{{y:{fmt}}}{unit}<extra></extra>"))
        if end_labels:
            last = d.iloc[-1]
            fig.add_annotation(x=last["month"], y=last[y], text=f"<b>{fuel}</b>", showarrow=False,
                               xanchor="left", xshift=8, font=dict(color=color, size=14))
    if ref is not None:
        fig.add_hline(y=ref, line=dict(color=BLACK, width=2, dash="dot"),
                      annotation_text="<b>2019 level</b>", annotation_position="bottom right",
                      annotation_font=dict(color=BLACK, size=13))
    _add_events(fig, df["month"].min(), df["month"].max())
    fig = _style(fig, height=450)
    fig.update_xaxes(title="")
    fig.update_yaxes(title=ylabel)
    if end_labels:
        fig.update_layout(showlegend=False, margin=dict(r=70))
    else:
        fig.update_layout(legend=dict(orientation="h", y=1.12, x=1, xanchor="right"))
    return fig


def dept_map(df, geo):
    # departments colored by cents above / below the France average
    lim = max(df["diff"].abs().max(), 1)
    fig = px.choropleth(df, geojson=geo, locations="dept", featureidkey="properties.code",
                        color="diff", color_continuous_scale=DIVERGING, range_color=(-lim, lim),
                        hover_name="name", custom_data=["avg_price"])
    fig.update_traces(marker_line_color="#555555", marker_line_width=0.4,
                      hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]:.3f} €/L"
                                    "<br>%{z:+.1f} cts vs France<extra></extra>")
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(coloraxis_colorbar=dict(title="cts/L<br>vs France"))
    fig = _style(fig, height=560)
    fig.update_layout(hovermode="closest", margin=dict(t=10))
    return fig


def ranking_bars(df):
    # df has columns name, avg_price, group ("Cheapest" / "Most expensive")
    fig = px.bar(df, x="avg_price", y="name", color="group", orientation="h",
                 color_discrete_map={"Cheapest": BLUE, "Most expensive": RED},
                 text=df["avg_price"].map(lambda p: f"{p:.3f} €"),
                 labels={"avg_price": PRICE_LABEL, "name": "", "group": ""})
    fig.update_traces(textposition="outside", hovertemplate="%{y}: %{x:.3f} €/L<extra></extra>")
    fig.update_xaxes(range=[df["avg_price"].min() - 0.08, df["avg_price"].max() + 0.06])
    fig.update_yaxes(categoryorder="total ascending")
    fig = _style(fig, height=520)
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=1.08, x=0))
    return fig


def region_heatmap(pivot):
    # pivot: regions in rows, years in columns, cents vs France in the cells
    lim = max(pivot.abs().max().max(), 1)
    fig = px.imshow(pivot, text_auto="+.0f", aspect="auto", color_continuous_scale=DIVERGING,
                    zmin=-lim, zmax=lim, labels=dict(x="Year", y="", color="cts/L vs France"))
    fig.update_traces(hovertemplate="%{y}, %{x}: %{z:+.1f} cts vs France<extra></extra>",
                      textfont=dict(size=13))
    fig.update_xaxes(side="top", dtick=1)
    fig = _style(fig, height=max(300, 38 * len(pivot) + 80))
    fig.update_layout(hovermode="closest")
    fig.update_yaxes(showgrid=False)
    return fig


def station_range(df, france_avg):
    """one line per region: cheap station, typical station, expensive station"""
    q = df.groupby("region")["price"].quantile([0.1, 0.5, 0.9]).unstack()
    q.columns = ["cheap", "typical", "expensive"]
    q = q.sort_values("typical")

    fig = go.Figure()
    # the line between the cheap and the expensive station
    for region, row in q.iterrows():
        fig.add_trace(go.Scatter(x=[row["cheap"], row["expensive"]], y=[region, region], mode="lines",
                                 line=dict(color="#9DB9DD", width=6), showlegend=False, hoverinfo="skip"))
    dots = [("cheap", "Cheap station (10% cheapest)", BLUE),
            ("typical", "Typical station (middle price)", BLACK),
            ("expensive", "Expensive station (10% most expensive)", RED)]
    for col, name, color in dots:
        fig.add_trace(go.Scatter(x=q[col], y=q.index, mode="markers", name=name,
                                 marker=dict(color=color, size=13, line=dict(color="white", width=1)),
                                 hovertemplate="%{y}<br>" + name + ": %{x:.3f} €/L<extra></extra>"))
    fig.add_vline(x=france_avg, line=dict(color=BLACK, width=2, dash="dot"),
                  annotation_text=f"<b>France average {france_avg:.2f} €</b>", annotation_position="top",
                  annotation_font=dict(color=BLACK, size=13))
    fig = _style(fig, height=max(320, 42 * len(q) + 140))
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", y=-0.12, x=0, yanchor="top"))
    fig.update_xaxes(title="Station price in 2025 (€/L)", showgrid=True, gridcolor="#e6e6e6")
    fig.update_yaxes(showgrid=False)
    return fig


def station_type_bars(df):
    # df has columns group, gap (cts vs department average), n (number of stations)
    df = df.sort_values("gap")
    colors = [RED if g > 0 else BLUE for g in df["gap"]]
    labels = [f"{g:+.1f} cts" for g in df["gap"]]
    names = [f"{g} ({n:,} stations)" for g, n in zip(df["group"], df["n"])]
    fig = go.Figure(go.Bar(x=df["gap"], y=names, orientation="h", marker_color=colors,
                           text=labels, textposition="outside",
                           hovertemplate="%{y}<br>%{x:+.1f} cts/L vs department average<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=BLACK, width=2))
    lo, hi = df["gap"].min(), df["gap"].max()
    fig.update_xaxes(title="Gap with the average of its department (cts/L)",
                     range=[min(lo, 0) - 3, hi + 4], showgrid=True, gridcolor="#e6e6e6")
    fig = _style(fig, height=80 + 60 * len(df))
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig
