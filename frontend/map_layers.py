import pydeck as pdk


def rectangle_polygon(min_lat: float, max_lat: float, min_lon: float, max_lon: float):
    return [
        [min_lon, min_lat],
        [max_lon, min_lat],
        [max_lon, max_lat],
        [min_lon, max_lat],
        [min_lon, min_lat],
    ]


def make_zone_layer(name: str, zone: dict, fill_color: list[int], line_color: list[int]) -> pdk.Layer:
    polygon = rectangle_polygon(
        min_lat=zone["min_lat"],
        max_lat=zone["max_lat"],
        min_lon=zone["min_lon"],
        max_lon=zone["max_lon"],
    )

    data = [
        {
            "name": name,
            "polygon": polygon,
            "fill_color": fill_color,
            "line_color": line_color,
        }
    ]

    return pdk.Layer(
        "PolygonLayer",
        data=data,
        get_polygon="polygon",
        get_fill_color="fill_color",
        get_line_color="line_color",
        stroked=True,
        filled=True,
        pickable=True,
        line_width_min_pixels=2,
    )


def make_point_layer(points: list[dict], color: list[int], radius: int = 10) -> pdk.Layer:
    return pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[longitude, latitude]",
        get_fill_color=color,
        get_radius=radius,
        pickable=True,
    )


def make_deck(layers: list[pdk.Layer], center_lat: float, center_lon: float) -> pdk.Deck:
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=16,
        pitch=0,
    )

    return pdk.Deck(
        initial_view_state=view_state,
        layers=layers,
        map_style="",
    )