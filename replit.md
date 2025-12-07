# OJAS - AI Co-Pilot for Rural Healthcare

## Project Overview
OJAS is an AI-powered triage assistant for ASHA workers in rural India. The application helps healthcare workers perform patient assessments using multimodal AI analysis, with full offline capability for areas with poor connectivity.

## Project Structure
```
/
├── app.py              # Main Streamlit application
├── .env.example        # Environment variable template
├── README.md           # User documentation
├── cases.csv           # CSV storage for case history (auto-created)
├── .streamlit/
│   └── config.toml     # Streamlit configuration
└── pyproject.toml      # Python dependencies
```

## Key Features
1. **Login System**: Demo credentials (asha/demo123)
2. **Text Input**: Describe symptoms via text
3. **Voice Input**: Record symptoms using Whisper transcription (online only)
4. **Image Upload**: Upload symptom photos for vision analysis
5. **AI Triage**: GPT-5 multimodal analysis with structured output
6. **Offline Mode**: Pre-written triage responses for 8+ common conditions
7. **Visual Pictograms**: DALL-E 3 generated instruction images (online only)
8. **Audio Instructions**: TTS for patient guidance (online only)
9. **Case History**: Searchable/filterable case records with offline tracking

## Offline Mode
The app works completely offline with these features:
- Toggle "Offline/Demo Mode" to enable
- Pre-written responses for: fever, rash, cough/cold, diarrhea, wounds, chest pain, pregnancy, headaches
- All cases saved locally with offline_mode flag
- Cases can be reviewed and synced when connectivity returns

## OpenAI APIs Used
- GPT-5 with Vision (multimodal triage) - online only
- Whisper (voice transcription) - online only
- DALL-E 3 (pictogram generation) - online only
- TTS (audio instructions) - online only

## Running the Application
```bash
streamlit run app.py --server.port 5000
```

## Environment Variables
- `OPENAI_API_KEY`: Required for online AI features (optional for offline mode)

## Data Storage
- Cases stored in `cases.csv` with columns:
  - timestamp, user, symptoms, triage, likely_condition
  - next_steps, danger_signs, patient_instructions
  - had_image, had_voice, offline_mode

## Recent Changes
- Added Offline/Demo Mode for use without internet
- Pre-written triage database for 8+ common conditions
- Voice input with Whisper transcription (online)
- DALL-E 3 pictogram generation (online)
- Text-to-Speech audio instructions (online)
- Comprehensive case history with search and filtering
- Offline mode tracking in case history
