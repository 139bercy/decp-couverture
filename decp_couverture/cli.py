""" Ce module contient les fonctions nécessaires à l'utilisation en ligne de commande du projet.
"""

import argparse
import sys

import streamlit.cli

from decp_couverture import web
from decp_couverture import download


def command_download(args=None):
    """Télécharge les DECP augmentées et les contours"""
    if not args.contours_only:
        download.download_decp(rows=args.rows)
    if not args.decp_only:
        download.download_contours()


def command_web(args=None):
    """Lance l'application web de présentation de la couverture"""
    sys.argv = ["0", "run", "./streamlit_app.py"]
    streamlit.cli.main()


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command")
    download_command = subparser.add_parser(
        "download",
        help="télécharger les DECP (.csv depuis economie.gouv.fr) et les contours de cartes",
    )
    download_command.add_argument(
        "--rows",
        required=False,
        help="nombre de lignes de DECP à télécharger",
        type=int,
    )
    download_command.add_argument(
        "--decp-only",
        required=False,
        help="télécharger uniquement les DECP",
        action="store_true",
    )
    download_command.add_argument(
        "--contours-only",
        required=False,
        help="télécharger uniquement les contours (communes, départements, régions)",
        action="store_true",
    )
    web_command = subparser.add_parser(
        "web", help="lancer l'application web de présentation de la couverture"
    )
    return parser


def run(args=None):
    """Point d'entrée du CLI.

    Args:
        args : Liste d'arguments envoyée par la ligne de commande.
    """
    parser = get_parser()
    args = parser.parse_args(args)
    if args.command == "download":
        command_download(args)
    elif args.command == "web":
        command_web(args)
