import pandas

from decp_couverture import conf

pandas.set_option("display.max_columns", 500)


def load_data_from_csv_file(
    path: str,
    sep: str = None,
    rows: int = None,
    columns: list = None,
    index_col: str = None,
):
    return pandas.read_csv(
        path, sep=sep, nrows=rows, header=0, index_col=index_col, usecols=columns
    )


def load_decp(rows: int = None, columns: list = None):
    path = conf.download.chemin_decp
    sep = ";"  # equivalent to "%3B"
    index_col = "id"
    if columns is not None and index_col not in columns:
        columns.append(index_col)
    return load_data_from_csv_file(
        path, sep=sep, rows=rows, index_col=index_col, columns=columns
    )
