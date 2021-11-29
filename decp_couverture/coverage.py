from decp_couverture import load
from decp_couverture import conf


def filter_public_sirens(dataframe, column_siren):
    dataframe = dataframe[
        dataframe[column_siren].str.startswith("1")
        | dataframe[column_siren].str.startswith("2")
    ]
    return dataframe


def run(rows: int = None):
    """Calcule des statistiques de couverture par commune, département, région.
    Sauvegarde les résultats sur le disque.
    """
    decp_columns = [
        conf.coverage.noms_colonnes_decp.id_marche,
        conf.coverage.noms_colonnes_decp.code_commune_acheteur,
        conf.coverage.noms_colonnes_decp.code_departement_acheteur,
        conf.coverage.noms_colonnes_decp.code_region_acheteur,
        conf.coverage.noms_colonnes_decp.annee_marche,
        conf.coverage.noms_colonnes_decp.siren_acheteur,
        "sirenAcheteurValide",
    ]
    decp = load.load_decp(columns=decp_columns, rows=rows)
    decp = decp.rename(
        columns={
            conf.coverage.noms_colonnes_decp.id_marche: "id_marche",
            conf.coverage.noms_colonnes_decp.code_commune_acheteur: "code_commune_acheteur",
            conf.coverage.noms_colonnes_decp.code_departement_acheteur: "code_departement_acheteur",
            conf.coverage.noms_colonnes_decp.code_region_acheteur: "code_region_acheteur",
            conf.coverage.noms_colonnes_decp.annee_marche: "annee_marche",
            conf.coverage.noms_colonnes_decp.siren_acheteur: "siren_acheteur",
        }
    )
    num_marches_tous_siren = len(decp)
    decp = decp[decp["sirenAcheteurValide"] == True]
    num_marches_siren_valide = len(decp)
    print(
        f"Nombre de marchés réduit de {num_marches_tous_siren} à {num_marches_siren_valide} en éliminant les SIREN invalides"
    )
    # Assurer que la colonne contient un SIREN (9 caractères)
    decp.siren_acheteur = decp.siren_acheteur.str[:9]
    decp = filter_public_sirens(decp, "siren_acheteur")
    num_marches_siren_publiques = len(decp)
    print(
        f"Nombre de marchés réduit de {num_marches_tous_siren} à {num_marches_siren_publiques} en conservant les SIREN publiques (1* ou 2*)"
    )

    coverage_stats = decp.groupby(
        [
            "annee_marche",
            "code_region_acheteur",
            "code_departement_acheteur",
            "code_commune_acheteur",
        ]
    ).agg(
        nombre_marches=("id_marche", "nunique"),
        nombre_sirens_decp=("siren_acheteur", "nunique"),
    )
    coverage_stats = coverage_stats.reset_index()

    sirens_columns = [
        conf.coverage.noms_colonnes_sirens.siren_acheteur,
        conf.coverage.noms_colonnes_sirens.siret_acheteur,
        conf.coverage.noms_colonnes_sirens.code_commune_acheteur,
    ]
    sirens = load.load_sirens(columns=sirens_columns, rows=rows)
    sirens = sirens.rename(
        columns={
            conf.coverage.noms_colonnes_sirens.siren_acheteur: "siren_acheteur",
            conf.coverage.noms_colonnes_sirens.siret_acheteur: "siret_acheteur",
            conf.coverage.noms_colonnes_sirens.code_commune_acheteur: "code_commune_acheteur",
        }
    )
    num_tous_sirens = len(sirens)
    sirens = filter_public_sirens(sirens, "siren_acheteur")
    num_sirens_publiques = len(sirens)
    print(
        f"Nombre de SIRENs réduit de {num_tous_sirens} à {num_sirens_publiques} en conservant les SIREN publiques (1* ou 2*)"
    )

    sirens_stats = sirens.groupby(["code_commune_acheteur",]).agg(
        nombre_sirens_insee=("siren_acheteur", "nunique"),
        # nombre_sirets_insee=('siret_acheteur', 'nunique')
    )
    coverage_stats = coverage_stats.merge(
        sirens_stats, how="left", left_on="code_commune_acheteur", right_index=True
    )
    path = conf.coverage.chemin
    load.save_data_to_csv_file(coverage_stats, path, index=False, float_format="%.2f")
