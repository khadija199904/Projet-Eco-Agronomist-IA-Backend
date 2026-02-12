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
│
├── 📁 src/                                    # Code source principal
│   ├── api/                                  # API FastAPI (Phase 4)
│   │   ├── v1/endpoints/
│   │   │   ├── detection_diseases.py         # Modèle 1 - Maladies
│   │   │   ├── detection_anomalies.py        # Modèle 2 - Anomalies
│   │   │   ├── batch_quality.py              # Qualité lots
│   │   │   ├── supplier_scoring.py           # Scoring fournisseur
│   │   │   └── recommendation.py             # RAG - Ordonnance
│   │   └── schemas/                          # Modèles Pydantic
│   │
│   ├── airflow/                              # Orchestration (Phase 2)
│   │   ├── dags/
│   │   │   ├── data_preparation_dag.py       # Pipeline données
│   │   │   └── training_dag.py               # Pipeline entraînement
│   │   └── tasks/
│   │       ├── spark_filtering.py            # Filtrage Agadir
│   │       ├── spark_preprocessing.py        # Prétraitement 640x640
│   │       ├── kaggle_export.py              # Export Kaggle
│   │       └── training_runner.py            # Lancer entraînement
│   │
│   ├── ml/                                   # Moteur IA (Phase 3)
│   │   ├── training/
│   │   │   ├── disease_detector/             # YOLOv8 Maladies + MLflow
│   │   │   └── anomaly_detector/             # YOLOv8 Anomalies + MLflow
│   │   ├── inference/
│   │   │   ├── disease_predictor.py
│   │   │   └── anomaly_predictor.py
│   │   ├── preprocessing/
│   │   │   ├── image_processor.py            # Redimensionnement
│   │   │   └── label_validator.py            # Validation YOLO
│   │   └── models/                           # Artefacts MLflow
│   │
│   ├── rag/                                  # Système RAG (Phase 3)
│   │   ├── retriever.py                      # Ingestion PDF
│   │   ├── generator.py                      # Génération réponses
│   │   └── knowledge_base/                   # Réglementations ONSSA
│   │
│   ├── database/                             # Couche données
│   │   ├── database.py
│   │   ├── models/                           # ORM models
│   │   └── repository/
│   │
│   └── utils/                                # Utilitaires globaux
│
├── 📁 data/                                  # Données
│   ├── raw/                                  # Données brutes
│   │   └── pepper.v1i.folder/                # Dataset Agadir
│   ├── processed/                            # Après prétraitement
│   │   ├── train_640x640/
│   │   ├── valid_640x640/
│   │   └── test_640x640/
│   ├── models/                               # Modèles MLflow
│   └── kaggle_exports/                       # Exports Kaggle
│
├── 📁 notebooks/                             # Kaggle & Expérimentations
│   ├── disease_training_kaggle.ipynb         # TensorFlow GPU Kaggle
│   ├── anomaly_training_kaggle.ipynb         # TensorFlow GPU Kaggle
│   └── mlflow_experiments/                   # Tracking MLflow
│
├── 📁 tests/                                 # Tests unitaires & intégration
│   ├── unit/
│   └── integration/
│
├── 📁 docs/                                  # Documentation
│   ├── PHASES.md                             # Détail phases
│   ├── AIRFLOW_SETUP.md                      # Config Airflow
│   ├── SPARK_PIPELINE.md                     # PySpark pipelines
│   ├── TRAINING.md                           # Entraînement Kaggle + MLflow
│   ├── ML_MODELS.md                          # Modèles Vision
│   ├── RAG_SYSTEM.md                         # Système RAG
│   ├── API_SPEC.md                           # Documentation API
│   └── DEPLOYMENT.md
│
├── 📁 scripts/                               # Scripts utilitaires
│   ├── export_to_kaggle.py                   # Exporter données Kaggle
│   ├── setup_mlflow.py                       # Initialiser MLflow
│   ├── init_airflow.py                       # Initialiser Airflow
│   └── init_db.py
│
├── 📁 config/                                # Configuration
│   ├── settings.py
│   ├── mlflow_config.py                      # MLflow tracking
│   ├── kaggle_config.py                      # Kaggle API
│   └── logging.yaml
│
├── 📁 logs/                                  # Logs
│   ├── airflow/
│   ├── mlflow/
│   └── api/
│
├── 📄 Configuration principale
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-airflow.txt
│   ├── requirements-spark.txt
│   ├── requirements-ml.txt                   # TensorFlow, YOLOv8, MLflow
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .env.example
│
└── 📄 Documentation
    ├── Jira_Planning_EcoAgronomist.md        # Planification Jira
    ├── project_description.txt               # Cahier des charges
    └── LICENSE
```

---

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