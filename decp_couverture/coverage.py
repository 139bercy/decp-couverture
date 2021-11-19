from decp_couverture import load
from decp_couverture import conf


def run():
    """Calcule des statistiques de couverture par commune, département, région.
    Sauvegarde les résultats sur le disque.
    """
    decp_columns = [
        conf.coverage.noms_colonnes.id_marche,
        conf.coverage.noms_colonnes.code_commune_acheteur,
        conf.coverage.noms_colonnes.code_departement_acheteur,
        conf.coverage.noms_colonnes.code_region_acheteur,
        conf.coverage.noms_colonnes.annee_marche,
    ]
    decp = load.load_decp(columns=decp_columns)
    decp = decp.rename(
        columns={
            conf.coverage.noms_colonnes.id_marche: "id_marche",
            conf.coverage.noms_colonnes.code_commune_acheteur: "code_commune_acheteur",
            conf.coverage.noms_colonnes.code_departement_acheteur: "code_departement_acheteur",
            conf.coverage.noms_colonnes.code_region_acheteur: "code_region_acheteur",
            conf.coverage.noms_colonnes.annee_marche: "annee_marche",
        }
    )
    coverage_stats = decp.groupby(
        [
            "annee_marche",
            "code_region_acheteur",
            "code_departement_acheteur",
            "code_commune_acheteur",
        ]
    )["id_marche"].nunique()
    coverage_stats = coverage_stats.reset_index()
    coverage_stats = coverage_stats.rename(columns={"id_marche": "nombre_marches"})
    path = conf.coverage.chemin
    print(coverage_stats.dtypes)
    load.save_data_to_csv_file(coverage_stats, path, index=False)
