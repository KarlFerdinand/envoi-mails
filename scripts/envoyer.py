"""Envoie un mail HTML déposé dans outbox/ via Gmail (SMTP + mot de passe d'application).

Usage : python scripts/envoyer.py outbox/tendances-2026-11-04.html [--dry-run]
- Objet : balise <title> du fichier.
- Destinataires : <meta name="to" content="a@x, b@y"> (par défaut Ivan).
  Seules les adresses de LISTE_AUTORISEE sont acceptées : un fichier déposé
  ne peut jamais envoyer un mail à quelqu'un d'autre.
"""
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from html import unescape
from pathlib import Path

LISTE_AUTORISEE = {"ivan.vollet@gmail.com", "hoe.ivan@gmail.com"}
PAR_DEFAUT = ["ivan.vollet@gmail.com"]
NOM_EXPEDITEUR = "Claude pour Ivan"
OBJET_PAR_DEFAUT = "Message automatique"
TAILLE_MAX = 500_000  # octets


def lire_objet(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if not m:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not m:
        return OBJET_PAR_DEFAUT
    texte = re.sub(r"<[^>]+>", "", m.group(1))
    return " ".join(unescape(texte).split())[:200] or OBJET_PAR_DEFAUT


def lire_destinataires(html: str) -> list[str]:
    m = re.search(r'<meta\s+name="to"\s+content="([^"]*)"', html, re.I)
    if not m:
        return PAR_DEFAUT
    adresses = [a.strip().lower() for a in m.group(1).split(",") if a.strip()]
    interdites = [a for a in adresses if a not in LISTE_AUTORISEE]
    if interdites or not adresses:
        sys.exit(f"Refusé : destinataire(s) non autorisé(s) {interdites}")
    return adresses


def version_texte(html: str) -> str:
    t = re.sub(r"(?is)<(script|style|title|head).*?</\1>", "", html)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|tr)>", "\n", t)
    t = re.sub(r"(?i)<li[^>]*>", "• ", t)
    t = re.sub(r"<[^>]+>", "", t)
    lignes = [" ".join(unescape(l).split()) for l in t.splitlines()]
    return "\n".join(l for l in lignes if l)


def construire(chemin: Path, expediteur: str) -> EmailMessage:
    brut = chemin.read_bytes()
    if len(brut) > TAILLE_MAX:
        sys.exit(f"Fichier trop gros ({len(brut)} octets) : {chemin}")
    html = brut.decode("utf-8")
    msg = EmailMessage()
    msg["Subject"] = lire_objet(html)
    msg["From"] = f"{NOM_EXPEDITEUR} <{expediteur}>"
    msg["To"] = ", ".join(lire_destinataires(html))
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    msg.set_content(version_texte(html))
    msg.add_alternative(html, subtype="html")
    return msg


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1:
        sys.exit("Usage : envoyer.py outbox/FICHIER.html [--dry-run]")
    chemin = Path(args[0])
    if chemin.parent.name != "outbox" or chemin.suffix != ".html":
        sys.exit(f"Refusé : seuls les fichiers outbox/*.html sont envoyés ({chemin})")
    expediteur = os.environ.get("GMAIL_USER", "expediteur@example.com")
    msg = construire(chemin, expediteur)
    if dry:
        print(f"[dry-run] À : {msg['To']} | Objet : {msg['Subject']}")
        print(version_texte(chemin.read_text('utf-8'))[:600])
        return
    mdp = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as s:
        s.login(expediteur, mdp)
        s.send_message(msg)
    print(f"Envoyé à {msg['To']} : {msg['Subject']}")


if __name__ == "__main__":
    main()
