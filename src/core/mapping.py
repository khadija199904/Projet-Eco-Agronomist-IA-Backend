# src/core/mapping.py

# Mapping pour l'affichage court sur les photos (UI/UX)
SHORT_CODE_MAP = {
    "Corn leaf blight": "CLB",
    "Corn rust leaf": "CRL",
    "Tomato leaf late blight": "TLLB",
    "Tomato mold leaf": "TML",
    "Tomato leaf yellow virus": "TLYV",
    "Blueberry leaf": "BL",
    "Tomato leaf mosaic virus": "TLMV",
    "Tomato leaf bacterial spot": "TLBS",
    "Squash Powdery mildew leaf": "SPML",
    "Corn Gray leaf spot": "CGLS",
    "Tomato Early blight leaf": "TEBL",
    "Tomato Septoria leaf spot": "TSLS",
    "Tomato leaf": "TOM", 
    "Bell_pepper leaf spot": "BPLS",
    "Bell_pepper leaf": "BP",
    "Tomato two spotted spider mites leaf": "TSSM",
    "Nutrient Deficiencies": "ND",
    "White bugs": "WB"
}

# Mapping pour les traductions et le RAG
TARGETS = [
    {"en": "Corn leaf blight", "fr": "Helminthosporiose"},
    {"en": "Corn rust leaf", "fr": "Rouille"},
    {"en": "Tomato leaf late blight", "fr": "Mildiou"},
    {"en": "Tomato mold leaf", "fr": "Cladosporiose"},
    {"en": "Tomato leaf yellow virus", "fr": "Virus"},
    {"en": "Blueberry leaf", "fr": "Myrtille (Sain)"},
    {"en": "Tomato leaf mosaic virus", "fr": "Mosaïque"},
    {"en": "Tomato leaf bacterial spot", "fr": "Gale bactérienne"},
    {"en": "Squash Powdery mildew leaf", "fr": "Oïdium"},
    {"en": "Corn Gray leaf spot", "fr": "Cercosporiose"},
    {"en": "Tomato Early blight leaf", "fr": "Alternariose"},
    {"en": "Tomato Septoria leaf spot", "fr": "Septoriose"},
    {"en": "Tomato leaf", "fr": "Tomate( sain)"}, 
    {"en": "Bell_pepper leaf spot", "fr": "Cercosporiose"},
    {"en": "Bell_pepper leaf", "fr": "Poivron (sain)"},
    {"en": "Tomato two spotted spider mites leaf", "fr": "Acariens"},
    {"en": "Nutrient Deficiencies", "fr": "Carence"},
    {"en": "White bugs", "fr": "Aleurodes"}
]

TRANSLATION_MAP = {t["en"]: t["fr"] for t in TARGETS}

CROP_MAP = {
    "Corn": "Maïs",
    "Tomato": "Tomate",
    "Blueberry": "Myrtille",
    "Squash": "Courge",
    "Bell_pepper": "Poivron"
}