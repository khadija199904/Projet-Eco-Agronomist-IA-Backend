# 🌱 Eco Agronomist IA - Backend

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

##  Structure du Projet

```
Projet-Eco-Agronomist-IA-Backend/
├── 📁 .github/                         # CONFIGURATION CI/CD (GitHub Actions)
│   └── 📁 workflows/
│       ├── ci-tests.yml                # Tests auto à chaque Push/PR
│       └── cd-deploy.yml               # Déploiement auto (Docker Build & Push)
│
├── 📁 src/                                    # Service 1 : CODE SOURCE PRINCIPAL
│   ├── api/                                   # API FastAPI
│   │   ├── v1/
│   │   │   ├── endpoints/                     # Routes (Controllers)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   ├── detection_diseases.py
│   │   │   │   ├── detection_anomalies.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── scoring.py
│   │   │   │   ├── advisor.py                 # RAG
│   │   │   │   └── auth.py
│   │   │   │
│   │   │   ├── services/                      # Logique Métier
│   │   │   │   ├── __init__.py
│   │   │   │   ├── external/                  # APIs & Cloud
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── storage_service.py
│   │   │   │   │   ├── model_huggingface.py
│   │   │   │   │   └── mlflow_client.py
│   │   │   │   └── internal/                  # Orchestration interne
│   │   │   │       ├── __init__.py
│   │   │   │       ├── image_analysis.py
│   │   │   │       └── rag_orchestrator.py
│   │   │   │
│   │   │   ├── schemas/                       # Pydantic (Validation)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── detection.py
│   │   │   │   ├── scoring.py
│   │   │   │   ├── request.py
│   │   │   │   └── response.py
│   │   │   │
│   │   │   ├── dependencies/                  # Injection de dépendances
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth_deps.py
│   │   │   │   └── service_deps.py
│   │   │   │
│   │   │   ├── security/                      # Sécurité & JWT
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jwt.py
│   │   │   │   ├── password.py
│   │   │   │   └── access_control.py
│   │   │   │
│   │   │   └── middleware/                    # Intercepteurs
│   │   │       ├── __init__.py
│   │   │       ├── logging.py
│   │   │       └── cors.py
│   │   │
│   │   ├── main.py                            # Point d'entrée FastAPI
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── errors.py
│   │
│   │
│   ├── ml/                                    # MOTEUR IA
│   │   ├── training/                          # Scripts pour Kaggle
│   │   │   ├── disease_detector/
│   │   │   └── anomaly_detector/
│   │   ├── inference/                         # Utilisé par l'API (Production)
│   │   │   ├── disease_predictor.py           # Load model from MLflow
│   │   │   └── anomaly_predictor.py
│   │   └── preprocessing/
│   │       ├── image_processor.py             # Utils Spark/Inference
│   │       └── label_validator.py
│   │
│   ├── rag/                                   # PHASE 3 - SYSTÈME RAG
│   │   ├── retriever.py                       # Ingestion PDF
│   │   ├── generator.py                       # LLM Response
│   │   └── knowledge_base/                    # Docs ONSSA
│   │
│   ├── database/                              # COUCHE DONNÉES
│   │   ├── __init__.py
│   │   ├── database.py                        # Configuration & Engine
│   │   ├── models/                            # ORM Models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── supplier.py
│   │   │   ├── batch.py
│   │   │   └── detection_result.py
│   │   └── repository/                        # Design Pattern Repository
│   │       ├── __init__.py
│   │       ├── user_repository.py
│   │       └── detection_repository.py
│   ├── Dockerfile.api              # Image avec Python + Ultralytics (YOLO)
│   ├── requirements.txt
│   └── utils/                                # Utilitaires globaux
│
│                               
├── 📁  airflow/  
│   ├── Dockerfile.airflow          # Image avec Java 11 + PySpark
│   ├── requirements-spark.txt                             # Service 2 - ORCHESTRATION (Medallion)
│   ├── dags/
│   │   └── medallion_data_pipeline.py     # DAG Principal
│   └── tasks/
│       ├── bronze_ingestion.py            # Raw -> Bronze
│       ├── silver_transformation.py       # Bronze -> Silver (Spark)
│       ├── gold_finalization.py           # Silver -> Gold (Spark)
│       └── kaggle_uploader.py             # Export Gold to Kaggle
│
├── 📁 data/                                   # STOCKAGE MEDALLION (Local/S3)
│   ├── raw/                                   # Données brutes
│   ├── bronze/                                # Landing zone
│   ├── silver/                                # Données nettoyées (Agadir)
│   └── gold/                                  # Données ML Ready (Kaggle export)
│
├── 📁 config/                                 # CONFIGURATION
│   ├── __init__.py
│   ├── settings.py                            # Load .env (load_dotenv)
│   ├── mlflow_config.py
│   └── logging.yaml
│
├── 📁 notebooks/                              # EXPÉRIMENTATIONS
│   ├── disease_training_kaggle.ipynb
│   └── mlflow_experiments/
│
├── 📁 scripts/                                # SCRIPTS UTILITAIRES
│   ├── init_db.py
│   └── setup_mlflow.py
│

├── 📁 tests/                                 # Tests unitaires & intégration
│   ├── unit/
│   └── integration/
│
│
├── 📁 logs/                                  # Logs
│   ├── airflow/
│   └── api/
│                                 
├── 📄 .env.example                  # template Variables d'environnement
├── 📄 .gitignore
├── 📄 docker-compose.yml
└── 📄 README.md

```

---

Voici l'architecture complète, finalisée et prête pour la production. Elle intègre les **microservices**, la partie **IA/ML**, l'architecture **Medallion**, ainsi qu'une structure robuste pour les **Tests** et le **CI/CD**.

### 1. Structure Complète du Projet (Monorepo Microservices)

```text
Projet-Eco-Agronomist-IA-Backend/
│
├── 📁 .github/                         # CONFIGURATION CI/CD (GitHub Actions)
│   └── 📁 workflows/
│       ├── ci-tests.yml                # Tests auto à chaque Push/PR
│       └── cd-deploy.yml               # Déploiement auto (Docker Build & Push)
│
├── 📁 services/                        # DOSSIER DES MICROSERVICES
│   │
│   ├── 📁 data-processing-service/     # MICROSERVICE 1: AIRFLOW + SPARK
│   │   ├── Dockerfile.airflow          # Image avec Java 11 + PySpark
│   │   ├── requirements-spark.txt
│   │   ├── 📁 airflow/
│   │   │   ├── 📁 dags/                # Pipeline Medallion
│   │   │   └── 📁 tasks/               # Bronze, Silver, Gold, Kaggle
│   │   └── 📁 tests/                   # Tests spécifiques au traitement Spark
│   │
│   └── 📁 api-inference-service/       # MICROSERVICE 2: FASTAPI + ML + RAG
│       ├── Dockerfile.api              # Image avec Python + Ultralytics (YOLO)
│       ├── requirements.txt
│       ├── main.py                     # Entrée FastAPI
│       ├── 📁 src/
│       │   ├── 📁 api/                 # Endpoints, Services, Schemas
│       │   ├── 📁 ml/                  # Inference (MLflow) & Preprocessing
│       │   ├── 📁 rag/                 # Retrieval Augmented Generation
│       │   ├── 📁 database/            # Models & Repositories
│       │   └── 📁 security/            # JWT & RBAC
│       └── 📁 tests/                   # Tests API, Unitaires & Intégration
│
├── 📁 shared_config/                   # CONFIGURATION PARTAGÉE
│   ├── settings.py                     # Singleton load_dotenv
│   └── logging.yaml
│
├── 📁 notebooks/                #  LES NOTEBOOKS KAGGLE 
│   ├── disease_training.ipynb   # Notebook pour l'entraînement des maladies
│   ├── anomaly_training.ipynb   # Notebook pour l'entraînement des anomalies
│   └── experiments/             # Tests de modèles, visualisations, etc.
│
├── 📁 data/                                   # STOCKAGE MEDALLION                                
│   ├── bronze/                                # Données brutes
│   ├── silver/                                # Données nettoyées (Agadir)
│   └── gold/                                  # Données ML Ready (Kaggle export)/
│
├── 📁 scripts/                         # SCRIPTS DE MAINTENANCE GLOBAL
│   ├── init_db.py
│   └── seed_data.py
│
├── 📄 .env.example                     # Modèle pour l'équipe
├── 📄 .gitignore                       # Exclut data/, .env, logs/, __pycache__/
├── 📄 docker-compose.yml               # Orchestrateur local
├── 📄 pytest.ini                       # Configuration des tests
└── 📄 README.md
```

---

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

# Airflow
AIRFLOW_HOME=/home/airflow
AIRFLOW__CORE__DAGS_FOLDER=/src/airflow/dags

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

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances ML (TensorFlow, YOLOv8, MLflow)
pip install -r requirements-ml.txt

# Dépendances Airflow (optionnel)
pip install -r requirements-airflow.txt

# Dépendances PySpark (optionnel)
pip install -r requirements-spark.txt

# Dépendances développement
pip install -r requirements-dev.txt
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

```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests intégration
pytest tests/integration/ -v

# Avec couverture
pytest --cov=src/ tests/
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