import plotly.express as px


def create_chart(formatted_gpx: list[dict[str, str]]):
    fig = px.line(formatted_gpx, x="distance", y="elevation",
                  hover_data={"distance": ":.2f", "elevation": ":.2f", "elevation_gain": ":.2f"})
    fig.update_layout(hovermode="x")
    fig.update_traces(
        hovertemplate='Distance: %{x:.2f} <br>Elevation: %{y:.0f} <br>Elevation Gain: %{customdata[0]:.0f}')
    chart_html = fig.to_html(full_html=False)
    return chart_html
