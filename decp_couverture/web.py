import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas

from decp_couverture import download
from decp_couverture import load
from decp_couverture import conf


def contours_layer_topojson(geo_data, topojson_key):
    """Construit une couche de contours pour Folium à partir d'un topojson

    Args:
        geo_data (dict): Données géographiques (format topojson)
        topojson_key (str): Clé topojson

    Returns:
        folium.TopoJson: Couche affichant les objets des données géographiques
    """
    return folium.TopoJson(geo_data, topojson_key)


def contours_layer_geojson(geo_data):
    """Construit une couche de contours pour Folium à partir d'un geojson

    Args:
        geo_data (dict): Données géographiques (format geojson)

    Returns:
        folium.GeoJson: Couche affichant les objets des données géographiques
    """
    return folium.GeoJson(geo_data)


def chloropleth_layer(
    key_on: str,
    column: str,
    geo_data: dict,
    decp_stats: pandas.DataFrame,
    topojson_key=None,
):
    """Construit une couche chloropleth pour Folium à partir de données géographiques (format topojson ou geojson)

    Args:
        key_on (str): [description]
        column (str): [description]
        geo_data (dict): Données géographiques (format geojson ou topojson)
        decp_stats (pandas.DataFrame): Données pour la couleur du chloropleth
        topojson_key (str, optional): Clé topojson. Defaults to None.

    Returns:
        folium.Choropleth: Couche affichant le choropleth
    """
    decp_stats = decp_stats.dropna()
    choropleth = folium.Choropleth(
        geo_data=geo_data,
        topojson=topojson_key,
        key_on=key_on,
        data=decp_stats,
        columns=[column, "idMarche"],
        fill_color="YlGn",  #'YlOrRd',  #'YlGnBu',
        fill_opacity=0.6,
        line_opacity=0.5,
        line_weight=0,
        nan_fill_color="black",
        nan_fill_opacity=0.1,
        highlight=True,
        legend_name="Nombre de marchés recensés dans les DECP",
    )
    return choropleth


def build_chloropleth_layer_for_cities(topo_cities, decp_stats):
    return chloropleth_layer(
        "feature.properties.ID",
        "codeCommuneAcheteur",
        topo_cities,
        decp_stats,
        topojson_key="objects.poly",
    )


def build_chloropleth_layer_for_departments(topo_departements, decp_stats):
    return chloropleth_layer(
        "feature.properties.code", "departementAcheteur", topo_departements, decp_stats
    )


def build_chloropleth_layer_for_regions(topo_regions, decp_stats):
    return chloropleth_layer(
        "feature.properties.code", "codeRegionAcheteur", topo_regions, decp_stats
    )


def run():

    decp_columns = [
        "idMarche",
        "anneeNotification",
        "codeRegionAcheteur",
        "departementAcheteur",
        "codeCommuneAcheteur",
    ]

    decp = load.load_decp(columns=decp_columns)
    # TODO : build decp_stats as part of a GitHub Action workflow
    decp_stats = decp.groupby(
        [
            "anneeNotification",
            "codeCommuneAcheteur",
            "codeRegionAcheteur",
            "departementAcheteur",
        ]
    )["idMarche"].nunique()
    decp_stats = decp_stats.reset_index()

    st.set_page_config(
        page_title=conf.web.titre_page,
        page_icon="decp_couverture/static/favicon.ico",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.image("decp_couverture/static/logo.png", width=300)
    st.title(conf.web.titre_page)

    st.sidebar.markdown(conf.web.texte_haut_barre_laterale)
    selected_year = st.sidebar.selectbox("Année", conf.web.annees)
    selected_scale = st.sidebar.selectbox(
        "Echelle", ["Communes", "Départements", "Régions"], index=1
    )
    st.sidebar.markdown(conf.web.texte_bas_barre_laterale)

    selected_year_decp_stats = decp_stats[
        decp_stats["anneeNotification"] == selected_year
    ]

    selected_year_decp_stats_cities = (
        selected_year_decp_stats.groupby(["codeCommuneAcheteur"])["idMarche"]
        .sum()
        .reset_index()
    )
    selected_year_decp_stats_departments = (
        selected_year_decp_stats.groupby(["departementAcheteur"])["idMarche"]
        .sum()
        .reset_index()
    )
    selected_year_decp_stats_regions = (
        selected_year_decp_stats.groupby(["codeRegionAcheteur"])["idMarche"]
        .sum()
        .reset_index()
    )

    if selected_scale == "Communes":
        topo = load.load_cities()
        stats = selected_year_decp_stats_cities
        chloropleth_layer = build_chloropleth_layer_for_cities(topo, stats)
        # chloropleth_layer = build_chloropleth_layer("objects.a_com2021_2154.geometries", "properties.codgeo", "codeCommuneAcheteur", topo, stats)
    elif selected_scale == "Départements":
        topo = load.load_departments()
        stats = selected_year_decp_stats_departments
        chloropleth_layer = build_chloropleth_layer_for_departments(topo, stats)
        # chloropleth_layer = build_chloropleth_layer("objects.a_dep2021_2154.geometries", "properties.dep", "departementAcheteur", topo, stats)
    elif selected_scale == "Régions":
        topo = load.load_regions()
        stats = selected_year_decp_stats_regions
        chloropleth_layer = build_chloropleth_layer_for_regions(topo, stats)
        # chloropleth_layer = build_chloropleth_layer("objects.a_reg2021_2154.geometries", "properties.reg", "codeRegionAcheteur", topo, stats)

    folium_map = folium.Map(
        location=[47, 2],
        zoom_start=6,
        tiles=conf.web.folium.tiles,
        attr=conf.web.folium.attribution,
        # crs=None #'EPSG4326' #'EPSG3857'
    )
    st.markdown(
        f"{len(stats)} {selected_scale.lower()} ont des marchés représentés dans les DECP au cours de l'année {selected_year}."
    )
    added_layer = chloropleth_layer.add_to(folium_map)
    # folium_map.fit_bounds(added_layer.get_bounds())
    folium_static(folium_map)
    # folium_map.save(f"map{selected_scale}.html")
    # st.dataframe(stats.sort_values(by="idMarche", ascending=False).head(10))
