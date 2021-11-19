import requests

from decp_couverture import conf


def download_data_from_url_to_file(url: str, path: str, stream: bool = True, auth=None):
    """Télécharge un fichier de données depuis une URL.

    Args:
        url (str): URL du fichier à télécharger
        path (str): Chemin vers un fichier local
        stream (bool, optional): Si la donnée doit être streamée (recommandé pour les fichiers volumineux). Defaults to True.
    """
    response = requests.get(
        url, allow_redirects=True, verify=True, stream=stream, auth=auth
    )
    with open(path, "wb") as file_writer:
        if stream:
            for chunk in response.iter_content(chunk_size=4096):
                file_writer.write(chunk)
        else:
            file_writer.write(response.content)


def download_decp(rows: int = None):
    path = conf.download.decp.chemin
    url = conf.download.decp.url
    if rows is not None:
        url += f"&rows={rows}"
    download_data_from_url_to_file(url, path, stream=True)


def download_contours():
    path = conf.download.contours.communes.chemin
    url = conf.download.contours.communes.url
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.contours.departements.chemin
    url = conf.download.contours.departements.url
    download_data_from_url_to_file(url, path, stream=True)
    path = conf.download.contours.regions.chemin
    url = conf.download.contours.regions.url
    download_data_from_url_to_file(url, path, stream=True)
