import base64
import weakref

import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas

from decp_couverture import download
from decp_couverture import load
from decp_couverture import artifacts
from decp_couverture import conf


@st.cache(ttl=864000)
def cached__download_contours():
    """Proxy de la fonction artifacts.get_last_artifact avec cache de 10j"""
    download.download_contours()


@st.cache(ttl=43200)
def cached__get_last_artifact(artifact_name: str):
    """Proxy de la fonction artifacts.get_last_artifact avec cache de 12h"""
    return artifacts.get_last_artifact(artifact_name)


@st.cache(ttl=None)
def cached__get_coverage(coverage_artifact_url: str):
    """Obtient les dernières statistiques de couverture disponibles sur github.com

    Args:
        coverage_artifact_url (str): URL de l'artifact à charger

    Returns:
        pandas.DataFrame: Statistiques de couverture par région, département, commune, année.
    """
    auth = artifacts.get_github_auth()
    download.download_data_from_url_to_file(
        coverage_artifact_url, "data/coverage.zip", stream=False, auth=auth
    )
    coverage = load.load_data_from_csv_file(
        "data/coverage.zip",
        dtype={
            "code_region_acheteur": str,
            "code_departement_acheteur": str,
            "code_commune_acheteur": str,
        },
    )
    return coverage


@st.cache(ttl=43200)
def cached__load_cities():
    """Proxy de la fonction load.load_cities avec cache de 12h"""
    return load.load_cities()


@st.cache(ttl=43200)
def cached__load_departments():
    """Proxy de la fonction load.load_cities avec cache de 12h"""
    return load.load_departments()


@st.cache(ttl=43200)
def cached__load_regions():
    """Proxy de la fonction load.load_regions avec cache de 12h"""
    return load.load_regions()


# @st.cache(ttl=86400)
def contours_layer_topojson(geo_data, topojson_key):
    """Construit une couche de contours pour Folium à partir d'un topojson.

    Args:
        geo_data (dict): Données géographiques (format topojson)
        topojson_key (str): Clé topojson

    Returns:
        folium.TopoJson: Couche affichant les objets des données géographiques
    """
    return folium.TopoJson(geo_data, topojson_key)


# @st.cache(ttl=86400)
def contours_layer_geojson(geo_data):
    """Construit une couche de contours pour Folium à partir d'un geojson.

    Args:
        geo_data (dict): Données géographiques (format geojson)

    Returns:
        folium.GeoJson: Couche affichant les objets des données géographiques
    """
    return folium.GeoJson(geo_data)


# @st.cache(ttl=86400)
def chloropleth_layer(
    key_on: str,
    column: str,
    geo_data: dict,
    decp_stats: pandas.DataFrame,
    topojson_key=None,
):
    """Construit une couche chloropleth pour Folium à partir de données géographiques (format topojson ou geojson).

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
        columns=[column, "nombre_marches"],
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
        "code_commune_acheteur",
        topo_cities,
        decp_stats,
        topojson_key="objects.poly",
    )


def build_chloropleth_layer_for_departments(topo_departements, decp_stats):
    return chloropleth_layer(
        "feature.properties.code",
        "code_departement_acheteur",
        topo_departements,
        decp_stats,
    )


def build_chloropleth_layer_for_regions(topo_regions, decp_stats):
    return chloropleth_layer(
        "feature.properties.code", "code_region_acheteur", topo_regions, decp_stats
    )


# @st.cache(ttl=86400)
def init_map():
    """Initialise une carte folium.

    Returns:
        folium.Map
    """
    return folium.Map(
        location=[47, 2],
        zoom_start=6,
        tiles=conf.web.folium.tiles,
        attr=conf.web.folium.attribution,
        # crs=None #'EPSG4326' #'EPSG3857'
    )


def run():

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

    cached__download_contours()
    (
        last_coverage_artifact_datetime,
        last_coverage_artifact_url,
    ) = cached__get_last_artifact("coverage.csv")
    coverage = cached__get_coverage(last_coverage_artifact_url)

    selected_year_decp_stats = coverage[coverage.annee_marche == selected_year]

    selected_year_decp_stats_cities = (
        selected_year_decp_stats.groupby(["code_commune_acheteur"])["nombre_marches"]
        .sum()
        .reset_index()
    )
    selected_year_decp_stats_departments = (
        selected_year_decp_stats.groupby(["code_departement_acheteur"])[
            "nombre_marches"
        ]
        .sum()
        .reset_index()
    )
    selected_year_decp_stats_regions = (
        selected_year_decp_stats.groupby(["code_region_acheteur"])["nombre_marches"]
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

    folium_map = init_map()

    st.markdown(
        f"{len(stats)} {selected_scale.lower()} ont des marchés représentés dans les DECP au cours de l'année {selected_year}."
    )
    added_layer = chloropleth_layer.add_to(folium_map)
    # folium_map.fit_bounds(added_layer.get_bounds())
    folium_static(folium_map)

    # st.markdown("Zones les plus représentées")
    # hottest_zones = stats.sort_values(by="nombre_marches", ascending=False).head(5)
    # st.dataframe(hottest_zones)

    col1, col2 = st.columns(2)
    if col1.button("Générer un lien de téléchargement de la carte"):
        file_name = f"carteCouvertureDECP-{selected_year}-{selected_scale}.html"
        path = f"./data/{file_name}"
        folium_map.save(path)
        with open(path, "rb") as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f"<a href=\"data:file/html;base64,{b64}\" download='{file_name}'> {file_name} </a>"
        col2.markdown(f"{href}", unsafe_allow_html=True)
