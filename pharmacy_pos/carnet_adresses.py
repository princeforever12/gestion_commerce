"""Carnet d'adresses pédagogique avec dictionnaire.

Exigence du projet:
- Les clés sont les noms (str)
- Les valeurs sont des tuples (telephone, email)

Le module expose les opérations CRUD demandées:
- ajouter_contact
- supprimer_contact
- rechercher_contact
- afficher_tous_les_contacts
"""

from __future__ import annotations

import re

Contact = tuple[str, str]
Carnet = dict[str, Contact]

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TEL_RE = re.compile(r"^[0-9+()\-\s]{6,20}$")


def _valider_nom(nom: str) -> str:
    nom_normalise = nom.strip()
    if not nom_normalise:
        raise ValueError("Le nom ne peut pas être vide.")
    return nom_normalise


def _valider_email(email: str) -> str:
    email_normalise = email.strip().lower()
    if not _EMAIL_RE.match(email_normalise):
        raise ValueError("Format d'email invalide.")
    return email_normalise


def _valider_telephone(telephone: str) -> str:
    telephone_normalise = telephone.strip()
    if not _TEL_RE.match(telephone_normalise):
        raise ValueError("Format de téléphone invalide.")
    return telephone_normalise


def ajouter_contact(carnet: Carnet, nom: str, telephone: str, email: str) -> None:
    """Ajoute ou met à jour un contact après validation des champs."""
    nom_valide = _valider_nom(nom)
    telephone_valide = _valider_telephone(telephone)
    email_valide = _valider_email(email)
    carnet[nom_valide] = (telephone_valide, email_valide)


def supprimer_contact(carnet: Carnet, nom: str) -> bool:
    """Supprime un contact; retourne True si supprimé, sinon False."""
    nom_valide = _valider_nom(nom)
    if nom_valide in carnet:
        del carnet[nom_valide]
        return True
    return False


def rechercher_contact(carnet: Carnet, nom: str) -> Contact | None:
    """Recherche un contact par nom exact et retourne (telephone, email) ou None."""
    nom_valide = _valider_nom(nom)
    return carnet.get(nom_valide)


def afficher_tous_les_contacts(carnet: Carnet) -> list[str]:
    """Retourne une liste de lignes lisibles triées par nom."""
    lignes: list[str] = []
    for nom in sorted(carnet):
        telephone, email = carnet[nom]
        lignes.append(f"{nom} -> Téléphone: {telephone}, Email: {email}")
    return lignes


def _demo_console() -> None:
    """Petite démo console pour illustrer les fonctions du projet."""
    carnet: Carnet = {}

    ajouter_contact(carnet, "Alice", "06 11 22 33 44", "alice@example.com")
    ajouter_contact(carnet, "Bob", "+33 6 99 88 77 66", "bob@example.com")

    print("\n=== Tous les contacts ===")
    for ligne in afficher_tous_les_contacts(carnet):
        print(ligne)

    print("\n=== Recherche: Alice ===")
    contact = rechercher_contact(carnet, "Alice")
    if contact:
        print(f"Alice: téléphone={contact[0]}, email={contact[1]}")

    print("\n=== Suppression: Bob ===")
    print("Supprimé" if supprimer_contact(carnet, "Bob") else "Introuvable")

    print("\n=== Carnet final ===")
    for ligne in afficher_tous_les_contacts(carnet):
        print(ligne)


if __name__ == "__main__":
    _demo_console()
