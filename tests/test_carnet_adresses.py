import pytest

from pharmacy_pos.carnet_adresses import (
    ajouter_contact,
    afficher_tous_les_contacts,
    rechercher_contact,
    supprimer_contact,
)


def test_ajouter_et_rechercher_contact() -> None:
    carnet = {}
    ajouter_contact(carnet, "Alice", "0611223344", "alice@example.com")

    assert rechercher_contact(carnet, "Alice") == ("0611223344", "alice@example.com")


def test_supprimer_contact() -> None:
    carnet = {"Bob": ("0699887766", "bob@example.com")}

    assert supprimer_contact(carnet, "Bob") is True
    assert rechercher_contact(carnet, "Bob") is None
    assert supprimer_contact(carnet, "Bob") is False


def test_afficher_tous_les_contacts_trie_par_nom() -> None:
    carnet = {
        "Zoé": ("0102030405", "zoe@example.com"),
        "Alice": ("0611223344", "alice@example.com"),
    }

    lignes = afficher_tous_les_contacts(carnet)

    assert lignes == [
        "Alice -> Téléphone: 0611223344, Email: alice@example.com",
        "Zoé -> Téléphone: 0102030405, Email: zoe@example.com",
    ]


def test_validation_email_invalide() -> None:
    with pytest.raises(ValueError):
        ajouter_contact({}, "Alice", "0611223344", "alice-at-example.com")


def test_validation_nom_vide() -> None:
    with pytest.raises(ValueError):
        ajouter_contact({}, "   ", "0611223344", "alice@example.com")
