import json

import pandas

from decp_couverture import conf

pandas.set_option("display.max_columns", 500)


def load_data_from_csv_file(
    path: str,
    sep: str = ";",
    rows: int = None,
    columns: list = None,
    index_col: str = None,
    dtype: dict = None,
):
    return pandas.read_csv(
        path,
        sep=sep,
        nrows=rows,
        header=0,
        index_col=index_col,
        usecols=columns,
        dtype=dtype,
    )


def save_data_to_csv_file(
    dataframe: pandas.DataFrame,
    path: str,
    sep: str = ";",
    index: bool = True,
    float_format=None,
):
    dataframe.to_csv(path, sep=sep, index=index, float_format=float_format)


def open_json(path: str):
    """Charge un fichier JSON sous forme de dictionnaire

    Args:
        path (str): CHemin vers un fichier JSON (utf8)

    Returns:
        dict: Données du fichier
    """
    with open(path, "rb") as file_reader:
        return json.loads(file_reader.read().decode("utf-8"))


def load_decp(rows: int = None, columns: list = None):
    path = conf.download.decp.chemin
    sep = conf.download.decp.separateur_csv
    index_col = "id"
    if columns is not None and index_col not in columns:
        columns.append(index_col)
    # TODO : enforce dtype for all columns
    return load_data_from_csv_file(
        path,
        sep=sep,
        rows=rows,
        columns=columns,
        dtype={
            "codeRegionAcheteur": str,
            "anneeNotification": "Int32",
            "sirenAcheteur": str,
            "siretAcheteur": str,
            "idAcheteur": str,
            "sirenAcheteurValide": bool,
        },
    )


def load_sirens(rows: int = None, columns: list = None):
    path = conf.download.sirens.chemin
    sep = conf.download.sirens.separateur_csv
    index_col = "siret"
    if columns is not None and index_col not in columns:
        columns.append(index_col)
    return load_data_from_csv_file(
        path,
        sep=sep,
        rows=rows,
        # index_col=index_col,
        columns=columns,
        dtype={
            "siren": str,
            "siret": str,
            "nic": int,
            "codeCommuneEtablissement": str,
        },
    )


def load_cities():
    path = conf.download.contours.communes.chemin
    return open_json(path)


def load_departments():
    path = conf.download.contours.departements.chemin
    return open_json(path)


def load_regions():
    path = conf.download.contours.regions.chemin
    return open_json(path)
