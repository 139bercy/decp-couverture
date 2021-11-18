import requests

from decp_couverture import conf


def download_data_from_url_to_file(url: str, path: str, stream: bool = True):
    """Télécharge un fichier de données depuis une URL.

    Args:
        url (str): URL du fichier à télécharger
        path (str): Chemin vers un fichier local
        stream (bool, optional): Si la donnée doit être streamée (recommandé pour les fichiers volumineux). Defaults to True.
    """
    response = requests.get(url, allow_redirects=True, verify=True, stream=stream)
    with open(path, "wb") as file_writer:
        if stream:
            for chunk in response.iter_content(chunk_size=4096):
                file_writer.write(chunk)
        else:
            file_writer.write(response.content)


def download_decp(rows: int = None):
    path = conf.download.chemin_decp
    url = conf.download.base_url_decp
    url += "?format=csv&timezone=Europe/Paris&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    if rows is not None:
        url += f"&rows={rows}"
    download_data_from_url_to_file(url, path, stream=True)


def download_contours():
    path = conf.download.chemin_communes_topojson
    url = conf.download.url_communes_topojson
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.chemin_departements_topojson
    url = conf.download.url_departements_topojson
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.chemin_regions_topojson
    url = conf.download.url_regions_topojson
    download_data_from_url_to_file(url, path, stream=True)
