import streamlit as st
from streamlit_folium import folium_static
import folium

from decp_couverture import download
from decp_couverture import load
from decp_couverture import conf


def build_chloropleth_layer_for_cities(topo_cities, decp_stats):
    decp_stats = decp_stats.dropna()
    choropleth = folium.Choropleth(
        geo_data=topo_cities,
        topojson="objects.poly",
        key_on="feature.properties.ID",
        data=decp_stats,
        columns=["codeCommuneAcheteur", "idMarche"],
        fill_color="YlGn",  #'YlOrRd',  #'YlGnBu',
        fill_opacity=0.6,
        line_opacity=0.5,
        line_weight=0,
        nan_fill_color="black",
        nan_fill_opacity=0.1,
        highlight=True,
        legend_name="Nombre de marchés recensés dans les DECP",
    )
    #choropleth = folium.TopoJson(topo_cities, "objects.poly")
    return choropleth


def build_chloropleth_layer_for_departments(topo_departements, decp_stats):
    decp_stats = decp_stats.dropna()
    choropleth = folium.Choropleth(
        geo_data=topo_departements,
        # topojson="features",
        key_on="feature.properties.code",
        data=decp_stats,
        columns=["departementAcheteur", "idMarche"],
        fill_color="YlGn",  #'YlOrRd',  #'YlGnBu',
        fill_opacity=0.6,
        line_opacity=0.5,
        line_weight=0,
        nan_fill_color="black",
        nan_fill_opacity=0.1,
        highlight=True,
        legend_name="Nombre de marchés recensés dans les DECP",
    )
    #choropleth = folium.GeoJson(topo_departements)
    return choropleth


def build_chloropleth_layer_for_regions(topo_regions, decp_stats):
    decp_stats = decp_stats.dropna()
    choropleth = folium.Choropleth(
        geo_data=topo_regions,
        # topojson="objects.FR.geometries",
        key_on="feature.properties.code",
        data=decp_stats,
        columns=["codeRegionAcheteur", "idMarche"],
        fill_color="YlGn",  #'YlOrRd',  #'YlGnBu',
        fill_opacity=0.6,
        line_opacity=0.5,
        line_weight=0,
        nan_fill_color="black",
        nan_fill_opacity=0.1,
        highlight=True,
        legend_name="Nombre de marchés recensés dans les DECP",
    )
    #choropleth = folium.GeoJson(topo_regions)
    return choropleth


def run():

    decp_columns = [
        "idMarche",
        # "nomAcheteur",
        # "source",
        "anneeNotification",
        # "datePublicationDonnees",
        #"idAcheteur",
        # "sirenAcheteurValide",
        "codeRegionAcheteur",
        #"libelleRegionAcheteur",
        "departementAcheteur",
        #"libelleDepartementAcheteur",
        #"codePostalAcheteur",
        "codeCommuneAcheteur",
        # "geolocCommuneAcheteur",
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
    elif selected_scale == "Départements":
        topo = load.load_departments()
        stats = selected_year_decp_stats_departments
        chloropleth_layer = build_chloropleth_layer_for_departments(topo, stats)
    elif selected_scale == "Régions":
        topo = load.load_regions()
        stats = selected_year_decp_stats_regions
        chloropleth_layer = build_chloropleth_layer_for_regions(topo, stats)

    mapbox_access_token = "pk.eyJ1IjoiaXN0b3BvcG9raSIsImEiOiJjaW12eWw2ZHMwMGFxdzVtMWZ5NHcwOHJ4In0.VvZvyvK0UaxbFiAtak7aVw"
    mapbox_attribution = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors <a href="https://spdx.org/licenses/ODbL-1.0.html">ODbL</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>'
    folium_map = folium.Map(
        location=[47, 2],
        zoom_start=6,
        tiles="https://api.mapbox.com/styles/v1/istopopoki/ckg98kpoc010h19qusi9kxcct/tiles/256/{z}/{x}/{y}?access_token="
        + mapbox_access_token,
        attr=mapbox_attribution,
        tooltip = 'This tooltip will appear on hover',
        crs='EPSG3857'
    )
    st.markdown(f"{len(stats)} {selected_scale.lower()} acheteurs.ses représenté.e.s dans les DECP au cours de l'année {selected_year}.")
    added_layer = chloropleth_layer.add_to(folium_map)
    #folium_map.fit_bounds(added_layer.get_bounds())
    folium_static(folium_map)
    #folium_map.save(f"map{selected_scale}.html")
    #st.dataframe(stats.sort_values(by="idMarche", ascending=False).head(10))
