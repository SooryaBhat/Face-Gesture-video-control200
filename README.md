# OJAS - AI Co-Pilot for Rural Healthcare

OJAS (meaning "life force" in Sanskrit) is an AI-powered triage assistant designed to support ASHA workers in rural India. This Streamlit web application helps healthcare workers perform preliminary patient assessments using AI.

## Features

### Core Features
- **Simple Login System**: Secure access for healthcare workers
- **Symptom Text Input**: Describe patient symptoms in detail
- **Voice Input**: Record symptoms in any language using OpenAI Whisper transcription
- **Image Upload**: Upload photos of visible symptoms (rashes, wounds, etc.)
- **AI-Powered Triage**: Uses OpenAI GPT with vision to analyze symptoms and images
- **Structured Results**: Get color-coded triage levels (Green/Yellow/Red), likely conditions, next steps, danger signs, and patient instructions

### Offline Mode
- **Works Without Internet**: Toggle "Offline/Demo Mode" to use the app in areas with no connectivity
- **Pre-written Triage Responses**: Uses a database of common conditions (fever, rash, cough, diarrhea, wounds, etc.)
- **Local Data Storage**: All cases are saved locally and can be reviewed when back online
- **Optimized for Rural Areas**: Designed for low-bandwidth and offline-first usage

### Multimedia Features
- **Visual Pictograms**: Generate DALL-E 3 visual instruction guides for patients with low literacy
- **Audio Instructions**: Text-to-Speech audio instructions for patients

### Case Management
- **Case History View**: Comprehensive view of all recorded cases
- **Search & Filter**: Search by symptoms/conditions, filter by triage level and date range
- **Case Statistics**: View counts of Green/Yellow/Red cases
- **Offline Case Tracking**: Cases recorded offline are marked and preserved

## Triage Levels

- **Green**: Monitor at home - self-care is sufficient
- **Yellow**: Refer to nearest clinic within 24-48 hours
- **Red**: Urgent referral to hospital immediately

## Installation

### On Replit

1. The app is pre-configured to run on Replit
2. Add your OpenAI API key to the Secrets tab with the key `OPENAI_API_KEY`
3. Click "Run" to start the application
4. For offline usage, enable "Offline/Demo Mode" toggle

### Local Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install streamlit openai python-dotenv pandas streamlit-audiorec
   ```
3. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
4. Add your OpenAI API key to the `.env` file
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Demo Credentials

- **Username**: `asha`
- **Password**: `demo123`

## Usage

### Online Mode (with Internet)
1. Log in with the demo credentials
2. Choose input method: Text Input or Voice Recording
3. Enter/record patient symptoms
4. Optionally upload an image of visible symptoms
5. Click "Analyze & Get Triage" to get AI-powered assessment
6. Review the triage result, next steps, and patient instructions
7. Generate visual pictogram or audio instructions for the patient
8. View recent cases in the table at the bottom
9. Click "View Case History" for comprehensive case management

### Offline Mode (without Internet)
1. Log in with the demo credentials
2. Enable "Offline/Demo Mode" toggle at the top
3. Enter patient symptoms via text input
4. Optionally upload an image
5. Click "Analyze & Get Triage (Offline)"
6. Get pre-written triage guidance based on symptom keywords
7. Cases are saved locally for later review

## OpenAI APIs Used

- **GPT-5 Vision**: Multimodal analysis of symptoms and images
- **Whisper**: Voice-to-text transcription in any language
- **DALL-E 3**: Visual pictogram generation for patient education
- **TTS**: Text-to-Speech for audio instructions

## Offline Mode Conditions Covered

The offline mode includes pre-written responses for common conditions:
- Fever / Viral infections
- Skin rashes / Allergies
- Cough / Cold / Respiratory infections
- Diarrhea / Gastroenteritis
- Wounds / Injuries
- Chest pain (Urgent)
- Pregnancy monitoring
- Headaches / Migraines

## Data Privacy

- All patient data is stored locally in a CSV file
- No data is sent to external servers except for OpenAI API calls (when online)
- Offline mode keeps all data completely local
- For production use, implement proper encryption and DPDPA compliance

## Technology Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-5 Vision, Whisper, DALL-E 3, TTS
- **Data Storage**: CSV files (local persistence)
- **Voice Recording**: streamlit-audiorec
- **Language**: Python

## License

This project is for educational and demonstration purposes.

---

*"Ojas means 'life force' in Sanskrit. Our mission is to ensure that no life in rural India is lost simply because care was too far away."*
