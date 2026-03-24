# 🌱 Eco Agronomist IA - Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![uv](https://img.shields.io/badge/uv-de5b43?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-0077B6?style=for-the-badge&logo=pinecone&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFC700?style=for-the-badge&logo=huggingface&logoColor=black)
![MLflow](https://img.shields.io/badge/MLflow-000000?style=for-the-badge&logo=mlflow&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-00A9E0?style=for-the-badge&logo=ultralytics&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A2A?style=for-the-badge&logo=apachespark&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

Plateforme intelligente de diagnostic phytosanitaire, valorisation post-récolte et traçabilité agricole pour les cultures d'Agadir.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Structure du Projet](#structure-du-projet)
3. [Architecture et Phases](#architecture-et-phases)
4. [Configuration](#configuration)
5. [Installation](#installation)
6. [Utilisation](#utilisation)
7. [Phases de Développement](#phases-de-développement)

---

## Vue d'ensemble

**Eco Agronomist IA** est une solution complète pour :

- **Pôle Production** : Diagnostic phytosanitaire mobile (détection maladies & anomalies)
- **Pôle Valorisation** : Analyse qualité post-récolte et scoring fournisseur
- **Pôle Consommation** : Transparence et traçabilité pour le consommateur final

### Objectifs
- Détection automatique des maladies des cultures (YOLOv8)
- Détection des anomalies (calibre, défauts, pourriture)
- Système RAG pour ordonnances conformes ONSSA
- Traçabilité complète ferme → table

---

## 📂 Structure du Projet

```text
Projet-Eco-Agronomist-IA-Backend/
├── .github/workflows/ci-cd.yml         # CI/CD (GitHub Actions)
├── data/                                # Stockage Medallion (Raw, Bronze, Silver)
│   ├── raw/RAG/                         # Corpus ONSSA (PDF)
│   ├── bronze/                          # Ingestion initiale
│   └── silver/                          # Données nettoyées & ML Ready
├── data_processing/                     # Service : TRAITEMENT DE DONNÉES & AIRFLOW
│   ├── airflow/                         # Orchestration (DAGs & Tasks)
│   │   ├── dags/                        # data_pipeline.py, roboflow-prep-dag.py
│   │   └── tasks/                       # Ingestion, Spark, Kaggle Uploader, etc.
│   ├── Dockerfile.airflow               # Image Airflow + Spark
│   ├── rag_ingest.py                    # Ingestion documents RAG
│   └── requirements-spark.txt           # Dépendances Spark
├── src/                                 # Service : API & IA
│   ├── ai/
│   │   ├── ml/                          # Entraînement & Nettoyage (YOLOv8, notebooks)
│   │   └── rag/
│   │       └── engine.py                # Moteur RAG (Pinecone + Groq)
│   ├── api/
│   │   ├── main.py                      # Entrée FastAPI
│   │   └── v1/
│   │       ├── crud/                    # diagnostic_crud, lot_crud, user_crud, etc.
│   │       ├── routers/                 # auth, diagnostic, production, rag, etc.
│   │       ├── schemas/                 # Modèles Pydantic (LotRecolte, etc.)
│   │       ├── services/                # rag_service.py
│   │       ├── dependencies/            # DB, User
│   │       └── middleware/              # CORS
│   ├── core/
│   │   └── config.py                    # Configuration (load_dotenv)
│   ├── database/
│   │   ├── database.py                  # Session SQLAlchemy
│   │   └── models/                      # users.py, diagnostics_table.py, etc.
│   ├── Dockerfile.api                   # Image API + YOLO
│   └── requirements.txt
├── tests/                               # Tests Automatisés
│   ├── test_basic.py
│   ├── test_preprocessing.py
│   └── test_unit.py
├── notebook/                            # Expérimentations & Vizualisation
├── docs/                                # Conception, Modélisation, Planning
├── pyproject.toml                       # Dépendances (uv)
└── uv.lock
```

---
### 1. Configuration de Pinecone (Base Vectorielle)

Pour le système RAG, nous utilisons Pinecone pour stocker les embeddings.

#### Accès API
1. Créez un compte sur [Pinecone](https://www.pinecone.io/).
2. Récupérez votre `PINECONE_API_KEY` et le nom de votre index `PINECONE_INDEX_NAME`.
3. Assurez-vous d'utiliser une dimension de **384** (si vous utilisez `paraphrase-multilingual-MiniLM-L12-v2`).

#### Variables d'environnement
Ajoutez-les au fichier `.env` :
```bash
PINECONE_API_KEY=votre_cle_api
PINECONE_INDEX_NAME=nom_de_l_index
GROQ_API_KEY=votre_cle_api_groq
```

### 2. Stratégie de Tests (Qualité Logicielle)

Le dossier `tests/` dans chaque service permet de valider le code avant qu'il n'aille en production.

*   **Unit Tests (Tests Unitaires) :** Tester une fonction seule (ex: `image_processor.py` redimensionne-t-il bien en 640x640 ?).
*   **Integration Tests (Tests d'Intégration) :** Tester la communication entre l'API et la Base de données ou MLflow.
*   **ML Tests :** Vérifier que le modèle chargé depuis MLflow renvoie bien un format de dictionnaire valide.
*   **RAG Tests :** Vérifier que le moteur de recherche trouve bien les bons paragraphes dans les PDFs de l'ONSSA.

---

### 3. Pipeline CI/CD (Automatisation)

Le fichier `.github/workflows/ci-tests.yml` permet d'automatiser la vérification. Voici à quoi ressemble la logique :

```yaml
name: CI Eco-Agronomist

on: [push, pull_request]

jobs:
  test-api:
    runs-on: ubuntu-latest
    services:
      postgres: # Lance une DB de test
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
        ports: ["5432:5432"]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with: {python-version: "3.10"}
      
      - name: Install dependencies
        run: pip install -r services/api-inference-service/requirements.txt pytest
      
      - name: Run Pytest
        run: pytest services/api-inference-service/tests/
```

---

### 4. Résumé du Workflow de Développement

1.  **Data Processing :** Vous développez vos scripts Spark dans le service `data-factory`. Les tests vérifient que le passage Bronze -> Silver ne perd pas de données.
2.  **Entraînement :** Vous poussez vos scripts `ml/training` sur **Kaggle**. Le modèle est loggé sur **MLflow**.
3.  **Inférence :** Vous mettez à jour l'API. Le **CI/CD** lance les tests automatiquement. Si tous les tests passent (vert), l'image Docker est mise à jour.
4.  **Production :** L'agriculteur utilise le **Frontend**. Le Frontend appelle l'**API-service** qui est toujours testée et stable.


##  Architecture et Phases

### **PHASE 1 : Infrastructure & Fondations** ✅
- ✅ Initialisation dépôt + Docker
- ✅ Configuration PostgreSQL
- ✅ CI/CD GitHub Actions

### **PHASE 2 : Data Engineering & Automatisation** 🔄 PRIORITAIRE
| Tâche | Composant | Description |
|-------|-----------|-------------|
| **2.1** | Airflow DAG | Orchestration pipeline données |
| **2.2** | PySpark Filtering | Filtrer cultures Agadir |
| **2.3** | PySpark Preprocessing | Redimensionner 640x640 + labels YOLO |
| **2.4** | Kaggle + TensorFlow | Entraîner sur Kaggle GPU + MLflow tracking |

**Répertoire**: `src/airflow/`, `scripts/export_to_kaggle.py`, `notebooks/`

### **PHASE 3 : Moteur IA Central** 🤖
| Tâche | Modèle | Framework | MLflow |
|-------|--------|-----------|--------|
| **3.1** | Détection Maladies | YOLOv8 / TensorFlow | ✅ Tracking |
| **3.2** | Détection Anomalies | YOLOv8 / TensorFlow | ✅ Tracking |
| **3.3** | Système RAG | LLM + PDF | Ordonnances ONSSA |

**Répertoire**: `src/ml/training/`, `src/rag/`, `data/models/`

### **PHASE 4 : Features Métier - Production** 📱
**Détection Mobile** (Terrain)
- Intégration Modèle 1 (Maladies)
- Intégration Modèle 2 (Anomalies)
- Overlay temps réel + confiance
- RAG Ordonnance intelligente

**Endpoints API**:
```
POST /api/v1/detection/diseases
POST /api/v1/detection/anomalies
POST /api/v1/recommendations
```

### **PHASE 5 : Valorisation & Consommation** 🏭
**Plateforme Web - Station**
- Scan QR Code lots
- Rapport qualité automatique
- Scoring fournisseur
- Recommandations tri

---

## ⚙️ Configuration

### Variables d'environnement (`.env`)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/eco_agronomist
DATABASE_ECHO=false

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=eco-agronomist-ai

# Kaggle
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# RAG & AI
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...
GROQ_API_KEY=...

# Logging
LOG_LEVEL=INFO
```

---

## 🚀 Installation

### 1. Cloner le repository
```bash
git clone <repository-url>
cd Projet-Eco-Agronomist-IA-Backend
```

### 2. Installer `uv`
Ce projet utilise [uv](https://github.com/astral-sh/uv) pour la gestion des dépendances.
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Installer les dépendances
```bash
uv sync
```

### 4. Configuration Docker Compose

```bash
# Démarrer services (PostgreSQL, Airflow, MLflow)
docker-compose up -d

# Vérifier les services
docker-compose ps
```

### 5. Initialiser la base de données

```bash
python scripts/init_db.py
```

### 6. Initialiser MLflow

```bash
python scripts/setup_mlflow.py
```

---

## Utilisation

### Démarrer l'API FastAPI

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Docs API : `http://localhost:8000/docs`

### Lancer le DAG Airflow

```bash
python scripts/init_airflow.py

# Accès interface Airflow
# http://localhost:8080
```

### Entraîner les modèles

**Sur Kaggle** (GPU disponible) :
1. Uploader dataset via `scripts/export_to_kaggle.py`
2. Exécuter notebooks Kaggle :
   - `notebooks/disease_training_kaggle.ipynb`
   - `notebooks/anomaly_training_kaggle.ipynb`
3. Télécharger modèles + métriques MLflow

**Localement** (avec MLflow) :
```bash
python src/ml/training/disease_detector/train_yolo.py
python src/ml/training/anomaly_detector/train_yolo.py

# Consulter MLflow
mlflow ui --host 0.0.0.0 --port 5000
```

### Faire une prédiction

```python
from src.ml.inference.disease_predictor import DiseasePredictor

predictor = DiseasePredictor()
result = predictor.predict("path/to/image.jpg")
print(result)  # {"disease": "Bacterial_spot", "confidence": 0.92}
```

### Tester les endpoints API

```bash
# Détection maladie
curl -X POST "http://localhost:8000/api/v1/detection/diseases" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "..."}'

# Détection anomalie
curl -X POST "http://localhost:8000/api/v1/detection/anomalies" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "..."}'

# Recommandation RAG
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"disease": "Bacterial_spot", "crop": "pepper"}'
```

---

## 📊 Phases de Développement

### Timeline

```
PHASE 1 (Infrastructure)      [████████] ✅
        ↓
PHASE 2 (Data + Airflow)      [██████  ] 🔄 EN COURS
        ├── 2.1 Airflow DAG    [████    ]
        ├── 2.2 PySpark Filter [██      ]
        ├── 2.3 Preprocessing  [██      ]
        └── 2.4 Kaggle Training[        ]
        ↓
PHASE 3 (Moteur IA)           [        ] ⏳
        ├── 3.1 Disease Model  
        ├── 3.2 Anomaly Model  
        └── 3.3 RAG System     
        ↓
PHASE 4 (API Production)      [        ] ⏳
PHASE 5 (Valorisation)        [        ] ⏳
```

### Dépendances entre tâches

```
2.1 (Airflow DAG)
    ↓
2.2 (PySpark Filtering) → 2.3 (Preprocessing)
                             ↓
                         2.4 (Kaggle Export)
                             ↓
3.1 + 3.2 (Modèles YOLOv8 + MLflow)
    ↓
3.3 (RAG)
    ↓
4.1 - 4.4 (API Endpoints)
    ↓
5.1 - 5.3 (Plateforme Web)
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [PHASES.md](docs/PHASES.md) | Détail de chaque phase |
| [AIRFLOW_SETUP.md](docs/AIRFLOW_SETUP.md) | Configuration Airflow DAGs |
| [SPARK_PIPELINE.md](docs/SPARK_PIPELINE.md) | Pipelines PySpark |
| [TRAINING.md](docs/TRAINING.md) | Entraînement Kaggle + MLflow |
| [ML_MODELS.md](docs/ML_MODELS.md) | Documentation modèles |
| [RAG_SYSTEM.md](docs/RAG_SYSTEM.md) | Système RAG ONSSA |
| [API_SPEC.md](docs/API_SPEC.md) | Spécification API |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Déploiement production |

---

## 🧪 Tests

Nous recommandons d'utiliser `uv run python -m pytest` pour s'assurer que le répertoire racine est bien dans le `PYTHONPATH`.

```bash
# Lancer tous les tests (Recommandé)
uv run python -m pytest

# Tests spécifiques
uv run python -m pytest tests/test_unit.py
```

---

## 🐳 Déploiement Docker

```bash
# Construire image
docker build -t eco-agronomist-backend .

# Lancer conteneur
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e MLFLOW_TRACKING_URI="..." \
  eco-agronomist-backend

# Avec docker-compose
docker-compose -f docker-compose.yml up -d
```

---

## 📝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md)

1. Créer une branche (`git checkout -b feature/feature-name`)
2. Commiter (`git commit -am 'Add feature'`)
3. Pusher (`git push origin feature/feature-name`)
4. Créer Pull Request

---

## 📄 Licence

Voir [LICENSE](LICENSE)

---

## 👥 Équipe

**Projet**: Eco Agronomist IA  
**Rédigé par**: KHADIJA ELABBIOUI  
**Organisation**: SIMPLON MAGHREB  
**Localisation**: Agadir, Maroc  
**Version**: 1.0  
**Date**: 14 janvier 2026

---

## 📞 Support

Pour toute question ou problème :
- 📧 Email: support@eco-agronomist.ma
- 🐛 Issues: [GitHub Issues](../../issues)
- 💬 Discussions: [GitHub Discussions](../../discussions)

---

**Dernière mise à jour**: Février 2026