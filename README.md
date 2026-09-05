# 🌾 FasalRakshak: Multilingual AI Agricultural Advisory & Crop Disease Diagnosis

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FasalRakshak** (फसल रक्षक) is an enterprise-grade, deep-learning-powered plant pathology diagnostic and agricultural extension advisory platform. Tailored for Indian smallholders and global crop protection, it integrates high-resolution **EfficientNet-B4** computer vision, **Grad-CAM** visual explainability, **RAG-grounded agronomic remedies**, and **high-fidelity regional neural voice synthesis** across **10 Indian regional languages + English**.

---

## 🌟 Key Capabilities

- **Deep Learning Vision Pipeline**:
  - EfficientNet-B4 backbone with custom classification head and test-time augmentation (TTA).
  - Diagnostic coverage across **38 crop and disease classes** spanning 14 major staple crops.
  - Automated Laplacian blur detection to guard against unclear field photographs.
- **Grad-CAM Visual Explainability**:
  - Heatmap overlays highlighting infected leaf areas to provide transparent, trustworthy diagnoses.
- **Multilingual Agronomic Advisory Engine**:
  - Verified organic, chemical, and preventive treatment regimens grounded in authentic **ICAR** (Indian Council of Agricultural Research) and **CIBRC** guidelines.
  - Complete native localization in **10 Indian languages** (Hindi, Khortha, Nagpuri, Bhojpuri, Bengali, Marathi, Telugu, Tamil, Gujarati, Punjabi) plus English.
- **Human-Realistic Regional Voice Assistant**:
  - Neural text-to-speech powered by **Sarvam AI `bulbul:v3`** regional voices.
  - Zero-dependency automatic offline fallback to **gTTS**.
- **AgroBot Conversational Assistant**:
  - Context-aware agricultural assistant powered by Google Gemini and ICAR knowledge retrieval.
- **Downloadable PDF Prescriptions**:
  - One-click generated clinical-grade crop health prescriptions for farmers and extension officers.

---

## 🌾 Supported Crops & Disease Classes (38 Classes)

| Crop | Classes Covered |
|---|---|
| **Apple** | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| **Blueberry** | Healthy |
| **Cherry** | Powdery Mildew, Healthy |
| **Corn (Maize)** | Cercospora Leaf Spot (Gray Spot), Common Rust, Northern Leaf Blight, Healthy |
| **Grape** | Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis Spot), Healthy |
| **Orange** | Citrus Greening (Huanglongbing) |
| **Peach** | Bacterial Spot, Healthy |
| **Pepper (Bell)** | Bacterial Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Raspberry** | Healthy |
| **Soybean** | Healthy |
| **Squash** | Powdery Mildew |
| **Strawberry** | Leaf Scorch, Healthy |
| **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mite, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |

---

## 📁 Project Structure

```text
FasalRakshak/
├── app.py                     # Streamlit interactive web application
├── api.py                     # FastAPI RESTful backend endpoints
├── config.py                  # Global configurations, paths, and class definitions
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Pre-configured Git exclusion rules
├── README.md                  # Comprehensive system documentation
├── data/
│   ├── sample_leaves/         # Botanical reference test images for all 38 classes
│   ├── advisory_db.json       # Pre-computed multi-lingual treatment database
│   └── icar_agri_knowledge_base.json # Grounded agronomic RAG knowledge base
├── models/
│   ├── fasal_rakshak_model.pth # Trained EfficientNet-B4 PyTorch model weights
│   ├── evaluation_report.json # Test split accuracy & per-class precision/recall
│   └── training_history.json  # Epoch metrics (loss, accuracy, duration)
├── src/
│   ├── model.py               # FasalRakshakNet neural architecture
│   ├── dataset.py             # CropLeafDataset loader & augmentation transforms
│   ├── inference.py           # Single-image prediction & TTA pipeline
│   ├── gradcam.py             # Grad-CAM heatmap visualization
│   ├── advisory.py            # Multilingual Advisory Engine & Sarvam/gTTS voice
│   ├── rag_engine.py          # TF-IDF RAG retrieval over ICAR extension guidelines
│   ├── inworld_voice.py       # Sarvam AI voice engine with caching
│   ├── llm.py                 # Gemini AgroBot conversational assistant
│   └── pdf_generator.py       # Clinical PDF prescription generator
├── scripts/
│   ├── download_plant_village.py # Automated PlantVillage dataset downloader
│   └── check_dataset.py       # Dataset verification & class validation tool
└── tests/
    ├── test_pipeline.py       # End-to-end unit and integration test suite
    └── test_agri_chat.py      # AgroBot chat integration test
`

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or 3.12 (Python 3.14 compatible)
- Recommended: Virtual environment (env or conda)

### 2. Clone & Environment Setup
`ash
git clone https://github.com/yourusername/FasalRakshak.git
cd FasalRakshak

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
`

### 3. Configure API Keys
Copy the example environment file and insert your API keys:
`ash
cp .env.example .env
`
Edit .env:
`env
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
`
*(Note: If SARVAM_API_KEY is omitted, the voice assistant automatically falls back to offline gTTS seamlessly.)*

---

## 💻 Running the Application

### Option A: Interactive Streamlit Dashboard
Launch the web interface for farmers and field workers:
`ash
streamlit run app.py
`
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Option B: FastAPI Backend Server
Launch the RESTful API server for mobile, edge, and third-party integrations:
`ash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
`
- Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI Specification: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API status and supported capabilities |
| POST | /api/predict | Upload a leaf image to receive diagnosis, confidence, and treatment |
| POST | /api/sarvam-voice | Synthesize regional Indian neural voice audio |
| POST | /api/chat-advisory | Conversational query to AgroBot AI |
| POST | /api/generate-prescription | Generate downloadable PDF prescription report |

---

## 🧪 Testing

Run the automated test suite to verify pipeline integrity:
`ash
pytest tests/ -v
`

---

## 🌍 UN Sustainable Development Goals (SDG) Alignment

- **SDG 2: Zero Hunger**: Early detection minimizes pre-harvest crop loss and preserves rural yield.
- **SDG 12: Responsible Consumption**: Precise chemical dosage calculations curb pesticide runoff into aquifers.
- **SDG 15: Life on Land**: Organic biological controls (*Trichoderma*, Neem extract) preserve beneficial pollinators and soil microbiome health.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
