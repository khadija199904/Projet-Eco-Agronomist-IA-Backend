async def generate_plant_advice(pathologies: list, culture: str = None):
    """
    RÔLE : Intelligence métier et conseils ONSSA.
    Inclut la culture pour des conseils plus précis.
    """
    if not pathologies:
        return "Aucune pathologie détectée. Maintenez une irrigation régulière et surveillez l'apparition de taches."

    # Simulation d'appel à votre moteur RAG (LangChain / OpenAI / Llama Index)
    # prompt = f"En tant qu'expert agronome, donnez des conseils ONSSA pour traiter {', '.join(pathologies)} sur une culture de {culture or 'plante'}."
    
    # Pour la démo, on utilise un mapping simple
    advices_map = {
        "Septoriose": f"Pour votre culture de {culture or 'plante'}, utilisez un fongicide homologué contre la septoriose et évitez l'irrigation par aspersion.",
        "Mildiou": f"Le mildiou sur {culture or 'plante'} nécessite un traitement préventif à base de cuivre et une bonne aération.",
        "Sain": "Votre plante est en bonne santé. Continuez le suivi régulier."
    }
    
    main_disease = pathologies[0] if pathologies else "Sain"
    advice = advices_map.get(main_disease, f"Surveillez l'évolution de votre {culture or 'plante'} et consultez un expert si les symptômes de {main_disease} persistent.")

    return advice