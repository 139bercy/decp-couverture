import json

import pandas

from decp_couverture import conf

pandas.set_option("display.max_columns", 500)


def load_data_from_csv_file(
    path: str,
    sep: str = None,
    rows: int = None,
    columns: list = None,
    index_col: str = None,
    dtype: dict = None
):
    return pandas.read_csv(
        path, sep=sep, nrows=rows, header=0, index_col=index_col, usecols=columns, dtype=dtype
    )


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
    path = conf.download.chemin_decp
    sep = ";"  # equivalent to "%3B"
    index_col = "id"
    if columns is not None and index_col not in columns:
        columns.append(index_col)
    #TODO : enforce dtype for all columns
    return load_data_from_csv_file(
        path, sep=sep, rows=rows, index_col=index_col, columns=columns, dtype={"codeRegionAcheteur":str}
    )


def load_cities():
    path = conf.download.chemin_communes_topojson
    return open_json(path)


def load_departments():
    path = conf.download.chemin_departements_topojson
    return open_json(path)


def load_regions():
    path = conf.download.chemin_regions_topojson
    return open_json(path)
