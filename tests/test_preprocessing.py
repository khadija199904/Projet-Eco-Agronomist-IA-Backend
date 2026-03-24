import pytest
from data_processing.rag_ingest import split_fiches

def test_split_fiches_simple():
    """
    Test que la fonction split_fiches découpe bien le texte en chunks
    en se basant sur le délimiteur FICHE_TRAITEMENT.
    """
    sample_text = """
    Document ONSSA
    ---FICHE_TRAITEMENT: Produit A
    Ceci est une description longue pour passer le filtre de 50 caractères minimum.
    ---FICHE_TRAITEMENT: Produit B
    Une autre description très longue également pour simuler une fiche réelle de traitement phytosanitaire.
    """
    
    fiches = split_fiches(sample_text)
    
    
    assert len(fiches) == 2
    assert "Produit A" in fiches[0]
    assert "Produit B" in fiches[1]
    assert fiches[0].startswith("FICHE_TRAITEMENT:")

def test_split_fiches_filter_short():
    """
    Vérifie que les fiches trop courtes (moins de 50 caract.) sont ignorées.
    """
    short_text = "---FICHE_TRAITEMENT: trop court"
    fiches = split_fiches(short_text)
    
    assert len(fiches) == 0
