import os
import json

import requests

from decp_couverture import conf


def load_json_from_url(url: str, stream: bool = True, auth=None, headers=None):
    """Charge un fichier JSON depuis une URL.

    Args:
        url (str): URL du fichier à télécharger
        path (str): Chemin vers un fichier local
        stream (bool, optional): Si la donnée doit être streamée (recommandé pour les fichiers volumineux). Defaults to True.

    Returns:
        repsone (dict) : JSON chargé sous forme d'un dictionnaire
    """
    return requests.get(
        url,
        allow_redirects=True,
        verify=True,
        stream=stream,
        auth=auth,
        headers=headers,
    ).json()


def download_data_from_url_to_file(
    url: str, path: str, stream: bool = True, auth=None, headers=None
):
    """Télécharge un fichier de données depuis une URL.

    Args:
        url (str): URL du fichier à télécharger
        path (str): Chemin vers un fichier local
        stream (bool, optional): Si la donnée doit être streamée (recommandé pour les fichiers volumineux). Defaults to True.
    """
    response = requests.get(
        url,
        allow_redirects=True,
        verify=True,
        stream=stream,
        auth=auth,
        headers=headers,
    )
    with open(path, "wb") as file_writer:
        if stream:
            for chunk in response.iter_content(chunk_size=4096):
                file_writer.write(chunk)
        else:
            file_writer.write(response.content)


def save_json(data: dict, path: str):
    """Stocke un dictionnaire sous forme de fichier JSON

    Args:
        data (dict): Dictionnaire à stocker
        path (str): Chemin vers le fichier (utf8)
    """
    with open(path, "w", encoding="utf-8") as file_writer:
        json.dump(data, file_writer, ensure_ascii=False, indent=2)


def download_decp(rows: int = None):
    """Télécharge les DECP sur le disque.

    Args:
        rows (int, optional): Nombre de lignes à télécharger. Defaults to None.
    """
    path = conf.download.decp.chemin
    url = conf.download.decp.url
    if rows is not None:
        url += f"&rows={rows}"
    download_data_from_url_to_file(url, path, stream=True)


def get_sirene_auth_header():
    """Obtient un dictionnaire d'authentification pour l'API INSEE Sirene.

    Returns:
        dict: Dictionnaire de header à utiliser lors des appels API
    """
    bearer = os.environ["SIRENE_API_BEARER"]
    headers = {"Authorization": f"Bearer {bearer}"}
    return headers


def download_sirens():
    """Télécharge la base Sirene sur le disque.
    """
    url = conf.download.sirens.url
    path = conf.download.sirens.chemin
    download_data_from_url_to_file(url, path, stream=True)


def download_contours():
    """Télécharge les contours de cartes sur le disque.
    """
    path = conf.download.contours.communes.chemin
    url = conf.download.contours.communes.url
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.contours.departements.chemin
    url = conf.download.contours.departements.url
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.contours.regions.chemin
    url = conf.download.contours.regions.url
    download_data_from_url_to_file(url, path, stream=True)
