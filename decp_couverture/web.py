from decp_couverture import download
from decp_couverture import load


def run():
    columns = [
        "idMarche",
        "source",
        "anneeNotification",
        "datePublicationDonnees",
        "idAcheteur",
        "sirenAcheteurValide",
        "codeRegionAcheteur",
        "libelleRegionAcheteur",
        "departementAcheteur",
        "libelleDepartementAcheteur",
        "codePostalAcheteur",
        "codeCommuneAcheteur",
        "geolocCommuneAcheteur",
    ]
    data = load.load_decp(columns=columns)
