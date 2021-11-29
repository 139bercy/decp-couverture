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
            "annee_marche": int,
            "nombre_marches": int,
            "nombre_sirens_decp": int,
            "nombre_sirens_insee": int,
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
    key_column: str,
    geo_data: dict,
    data_column: str,
    decp_stats: pandas.DataFrame,
    topojson_key=None,
    legend: str = None,
    tooltip_fields: list = None,
    tooltip_aliases: list = None
):
    """Construit une couche chloropleth pour Folium à partir de données géographiques (format topojson ou geojson).

    Args:
        key_on (str): [description]
        key_column (str): [description]
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
        columns=[key_column, data_column],
        fill_color="YlGn",  # "RdYlGn", #"YlGn",  #'YlOrRd',  #'YlGnBu',
        fill_opacity=0.7,
        line_weight=0,
        nan_fill_color="black",  # "#800000",
        nan_fill_opacity=0.3,
        highlight=True,
        legend_name=legend,
    )
    if tooltip_fields is not None:
        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            #style=('background-color: white; color: black;')
        ))
    return choropleth


def build_chloropleth_layer_for_cities(topo_cities, decp_stats, data_column, legend=None):
    return chloropleth_layer(
        "feature.properties.ID",
        "code_commune_acheteur",
        topo_cities,
        data_column,
        decp_stats,
        topojson_key="objects.poly",
        legend=legend,
        tooltip_fields=["ID"],
        tooltip_aliases=["Code commune"],
    )


def build_chloropleth_layer_for_departments(topo_departements, decp_stats, data_column, legend=None):
    return chloropleth_layer(
        "feature.properties.code",
        "code_departement_acheteur",
        topo_departements,
        data_column,
        decp_stats,
        legend=legend,
        tooltip_fields=["nom", "code"],
        tooltip_aliases=["Département", "Code département"],
    )


def build_chloropleth_layer_for_regions(topo_regions, decp_stats, data_column, legend=None):
    return chloropleth_layer(
        "feature.properties.code",
        "code_region_acheteur",
        topo_regions,
        data_column,
        decp_stats,
        legend=legend,
        tooltip_fields=["nom", "code"],
        tooltip_aliases=["Région", "Code région"],
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

    st.sidebar.markdown(
        f"*Données mises à jour le {last_coverage_artifact_datetime.strftime('%d/%m/%Y')}.*"
    )

    selected_year_decp_stats = coverage[coverage.annee_marche == selected_year]

    selected_year_decp_stats_cities = (
        selected_year_decp_stats.groupby(["code_commune_acheteur"])
        .agg(
            nombre_marches=("nombre_marches", "sum"),
            nombre_sirens_decp=("nombre_sirens_decp", "sum"),
            nombre_sirens_insee=("nombre_sirens_insee", "sum"),
        )
        .reset_index()
    )
    selected_year_decp_stats_cities[
        "sirens_couverts"
    ] = selected_year_decp_stats_cities.nombre_sirens_decp.fillna(
        1
    ) / selected_year_decp_stats_cities.nombre_sirens_insee.fillna(
        1
    )
    selected_year_decp_stats_cities["pourcentage_sirens_couverts"] = (
        (selected_year_decp_stats_cities.sirens_couverts * 100).round(0).astype(int)
    )
    selected_year_decp_stats_cities["pourcentage_sirens_couverts"] = selected_year_decp_stats_cities["pourcentage_sirens_couverts"].clip(lower=0, upper=100)
    del selected_year_decp_stats_cities["sirens_couverts"]
    del selected_year_decp_stats_cities["nombre_sirens_decp"]
    del selected_year_decp_stats_cities["nombre_sirens_insee"]
    selected_year_decp_stats_departments = (
        selected_year_decp_stats.groupby(["code_departement_acheteur"])
        .agg(
            nombre_marches=("nombre_marches", "sum"),
            nombre_sirens_decp=("nombre_sirens_decp", "sum"),
            nombre_sirens_insee=("nombre_sirens_insee", "sum"),
        )
        .reset_index()
    )
    selected_year_decp_stats_departments[
        "sirens_couverts"
    ] = selected_year_decp_stats_departments.nombre_sirens_decp.fillna(
        1
    ) / selected_year_decp_stats_departments.nombre_sirens_insee.fillna(
        1
    )
    selected_year_decp_stats_departments["pourcentage_sirens_couverts"] = (
        (selected_year_decp_stats_departments.sirens_couverts * 100)
        .round(0)
        .astype(int)
    )
    del selected_year_decp_stats_departments["sirens_couverts"]
    del selected_year_decp_stats_departments["nombre_sirens_decp"]
    del selected_year_decp_stats_departments["nombre_sirens_insee"]
    selected_year_decp_stats_regions = (
        selected_year_decp_stats.groupby(["code_region_acheteur"])
        .agg(
            nombre_marches=("nombre_marches", "sum"),
            nombre_sirens_decp=("nombre_sirens_decp", "sum"),
            nombre_sirens_insee=("nombre_sirens_insee", "sum"),
        )
        .reset_index()
    )
    selected_year_decp_stats_regions[
        "sirens_couverts"
    ] = selected_year_decp_stats_regions.nombre_sirens_decp.fillna(
        1
    ) / selected_year_decp_stats_regions.nombre_sirens_insee.fillna(
        1
    )
    selected_year_decp_stats_regions["pourcentage_sirens_couverts"] = (
        (selected_year_decp_stats_regions.sirens_couverts * 100).round(0).astype(int)
    )
    del selected_year_decp_stats_regions["sirens_couverts"]
    del selected_year_decp_stats_regions["nombre_sirens_decp"]
    del selected_year_decp_stats_regions["nombre_sirens_insee"]

    options_dict = {
        "Part des acheteurs publics représentés dans les DECP": "pourcentage_sirens_couverts",
        "Nombre de marchés recensés dans les DECP": "nombre_marches",
    }
    selected_option = st.radio("Indicateur à représenter:", options_dict.keys())
    selected_column = options_dict[selected_option]

    if selected_scale == "Communes":
        topo = load.load_cities()
        stats = selected_year_decp_stats_cities
        chloropleth_layer = build_chloropleth_layer_for_cities(
            topo, stats, selected_column, legend=selected_option
        )
        # chloropleth_layer = build_chloropleth_layer("objects.a_com2021_2154.geometries", "properties.codgeo", "codeCommuneAcheteur", topo, stats)
    elif selected_scale == "Départements":
        topo = load.load_departments()
        stats = selected_year_decp_stats_departments
        chloropleth_layer = build_chloropleth_layer_for_departments(
            topo, stats, selected_column, legend=selected_option
        )
        # chloropleth_layer = build_chloropleth_layer("objects.a_dep2021_2154.geometries", "properties.dep", "departementAcheteur", topo, stats)
    elif selected_scale == "Régions":
        topo = load.load_regions()
        stats = selected_year_decp_stats_regions
        chloropleth_layer = build_chloropleth_layer_for_regions(
            topo, stats, selected_column, legend=selected_option
        )
        # chloropleth_layer = build_chloropleth_layer("objects.a_reg2021_2154.geometries", "properties.reg", "codeRegionAcheteur", topo, stats)

    st.markdown(
        f"{len(stats)} {selected_scale.lower()} ont des marchés représentés dans les DECP au cours de l'année {selected_year}."
    )

    folium_map = init_map()

    added_layer = chloropleth_layer.add_to(folium_map)
    # folium_map.fit_bounds(added_layer.get_bounds())
    folium_static(folium_map)

    # col1, col2 = st.columns(2)
    # if col1.button("Générer un lien de téléchargement de la carte"):
    #     file_name = f"carteCouvertureDECP-{selected_year}-{selected_scale}.html"
    #     path = f"./data/{file_name}"
    #     folium_map.save(path)
    #     with open(path, "rb") as f:
    #         bytes = f.read()
    #         b64 = base64.b64encode(bytes).decode()
    #         href = f"<a href=\"data:file/html;base64,{b64}\" download='{file_name}'> {file_name} </a>"
    #     col2.markdown(f"{href}", unsafe_allow_html=True)

    col1, col2 = st.columns([2,3])
    col1.markdown(f"**{selected_scale} avec le plus de marchés:**")
    markdown_col1 = f"| Code | Nombre de marchés | \n | ------------- |:-------------:|"
    zones_most_markets = stats.sort_values(by="nombre_marches", ascending=False).head(5)
    for zone, num_markets, _ in zones_most_markets.values.tolist():
        markdown_col1 += f"\n | {zone} | {num_markets} marchés |"
    col1.markdown(markdown_col1)
    col2.markdown(f"**{selected_scale} avec le plus d'acheteurs publics représentés:**")
    zones_most_sirens = stats.sort_values(by="pourcentage_sirens_couverts", ascending=False).head(5)
    markdown_col2 = f"| Code | Acheteurs publics représentés | \n | ------------- |:-------------:|"
    for zone, _, covered_percentage in zones_most_sirens.values.tolist():
        markdown_col2 += f"\n | {zone} | {covered_percentage}% |"
    col2.markdown(markdown_col2)

    st.markdown("\n")
    st.markdown("*Le nombre d'acheteurs publics correspond au nombre d'entités référencées dans le répertoire Sirene, mis à disposition par l'[INSEE](https://www.insee.fr/fr/information/3591226) et disponible sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/), dont le code SIREN débute par [le chiffre 1 ou 2](https://www.insee.fr/fr/metadonnees/definition/c2047).*")