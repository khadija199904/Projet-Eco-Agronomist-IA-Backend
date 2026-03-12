async def generate_plant_advice(pathologies: list):
    """
    RÔLE : Intelligence métier et conseils ONSSA.
    """
    if not pathologies:
        return "Aucune pathologie détectée. Maintenez une irrigation régulière et surveillez l'apparition de taches."

    # Simulation d'appel à votre moteur RAG (LangChain / OpenAI / Llama Index)
    # prompt = f"Quels sont les traitements ONSSA pour : {', '.join(pathologies)} ?"
    # response = await rag_engine.query(prompt)
    advices_map = {"Tomato Septoria leaf spot": "Utilisez un fongicide à base de cuivre et retirez les feuilles infectées."}
    advice = advices_map.get(disease, "Surveillez l'évolution de la plante.")
    # return f"Conseil RAG : Pour traiter {', '.join(pathologies)}, utilisez..."

    return advice