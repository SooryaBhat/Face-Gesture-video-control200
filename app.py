import os
import base64
import json
import random
import tempfile
from datetime import datetime

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from st_audiorec import st_audiorec

load_dotenv()

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_MODEL = "gpt-5"

CASES_CSV = "cases.csv"
VALID_USERNAME = "asha"
VALID_PASSWORD = "demo123"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

DEMO_TRIAGE_RESPONSES = [
    {
        "keywords": ["fever", "temperature", "hot", "bukhar"],
        "response": {
            "triage": "Yellow",
            "likely_condition": "Viral Fever / Flu",
            "next_steps": [
                "Give paracetamol for fever (as per weight)",
                "Ensure adequate fluid intake",
                "Monitor temperature every 4 hours",
                "Refer to PHC if fever persists beyond 3 days"
            ],
            "danger_signs": [
                "High fever above 103°F that doesn't respond to medicine",
                "Difficulty breathing or chest pain",
                "Severe headache with stiff neck",
                "Rash that doesn't fade when pressed"
            ],
            "patient_instruction_text": "Give the patient plenty of water and rest. Use a wet cloth on forehead to cool down. Give fever medicine as directed. If fever stays high for more than 3 days, go to the health center."
        }
    },
    {
        "keywords": ["rash", "itchy", "skin", "red spots", "allergy"],
        "response": {
            "triage": "Green",
            "likely_condition": "Allergic Skin Reaction / Contact Dermatitis",
            "next_steps": [
                "Keep the affected area clean and dry",
                "Apply calamine lotion if available",
                "Avoid scratching the area",
                "Identify and remove the allergen if possible"
            ],
            "danger_signs": [
                "Rash spreading rapidly across body",
                "Swelling of face, lips, or tongue",
                "Difficulty breathing",
                "Fever accompanying the rash"
            ],
            "patient_instruction_text": "Keep the skin clean and dry. Do not scratch. Apply calamine lotion to reduce itching. If the rash spreads quickly or there is swelling or breathing trouble, go to hospital immediately."
        }
    },
    {
        "keywords": ["cough", "cold", "sore throat", "runny nose", "khansi"],
        "response": {
            "triage": "Green",
            "likely_condition": "Common Cold / Upper Respiratory Infection",
            "next_steps": [
                "Rest and drink warm fluids",
                "Gargle with warm salt water for sore throat",
                "Use steam inhalation for congestion",
                "Monitor for worsening symptoms"
            ],
            "danger_signs": [
                "Cough lasting more than 2 weeks",
                "Blood in sputum",
                "High fever with chills",
                "Severe difficulty breathing"
            ],
            "patient_instruction_text": "Drink warm water and rest well. Gargle with salt water 3 times a day. Breathe in steam from hot water carefully. If cough lasts more than 2 weeks or there is blood, visit the health center."
        }
    },
    {
        "keywords": ["diarrhea", "loose motion", "vomiting", "dehydration", "dast"],
        "response": {
            "triage": "Yellow",
            "likely_condition": "Acute Gastroenteritis / Diarrheal Disease",
            "next_steps": [
                "Start ORS immediately",
                "Continue breastfeeding for infants",
                "Give zinc supplements for children",
                "Monitor for signs of dehydration"
            ],
            "danger_signs": [
                "Blood or mucus in stool",
                "Unable to drink or keep fluids down",
                "Sunken eyes and very dry mouth",
                "No urination for 6+ hours"
            ],
            "patient_instruction_text": "Give ORS solution after every loose motion. For children, continue giving breast milk or food. If patient cannot drink, has blood in stool, or very dry mouth with no tears, go to hospital urgently."
        }
    },
    {
        "keywords": ["wound", "cut", "injury", "bleeding", "chot"],
        "response": {
            "triage": "Yellow",
            "likely_condition": "Open Wound / Laceration",
            "next_steps": [
                "Clean wound with clean water",
                "Apply pressure to stop bleeding",
                "Cover with clean bandage",
                "Check tetanus vaccination status"
            ],
            "danger_signs": [
                "Bleeding that won't stop after 10 minutes of pressure",
                "Deep wound exposing muscle or bone",
                "Signs of infection (pus, increasing redness, fever)",
                "Wound from animal bite"
            ],
            "patient_instruction_text": "Clean the wound with clean water. Press firmly with clean cloth to stop bleeding. Cover with bandage. If bleeding continues, wound is deep, or from animal bite, go to hospital for stitches and tetanus injection."
        }
    },
    {
        "keywords": ["chest pain", "heart", "breathless", "dil"],
        "response": {
            "triage": "Red",
            "likely_condition": "Possible Cardiac Event - URGENT",
            "next_steps": [
                "Keep patient calm and seated",
                "Loosen tight clothing",
                "Call emergency services immediately",
                "Transport to nearest hospital urgently"
            ],
            "danger_signs": [
                "Crushing chest pain spreading to arm or jaw",
                "Severe shortness of breath",
                "Cold sweat with nausea",
                "Loss of consciousness"
            ],
            "patient_instruction_text": "THIS IS URGENT. Keep patient calm and seated. Do not let them walk. Loosen any tight clothes. Take to hospital IMMEDIATELY. Call ambulance if available. Time is critical."
        }
    },
    {
        "keywords": ["pregnant", "pregnancy", "baby", "delivery", "garbh"],
        "response": {
            "triage": "Yellow",
            "likely_condition": "Pregnancy - Requires Monitoring",
            "next_steps": [
                "Check for danger signs of pregnancy",
                "Ensure regular antenatal checkups",
                "Monitor fetal movements",
                "Prepare birth plan and emergency transport"
            ],
            "danger_signs": [
                "Severe abdominal pain",
                "Vaginal bleeding",
                "Severe headache or blurred vision",
                "Reduced or no fetal movement",
                "Swelling of face and hands with headache"
            ],
            "patient_instruction_text": "Pregnant women should have regular checkups. Eat well and take iron tablets. Count baby movements daily. If there is bleeding, severe pain, bad headache, or baby stops moving, go to hospital immediately."
        }
    },
    {
        "keywords": ["headache", "migraine", "sir dard"],
        "response": {
            "triage": "Green",
            "likely_condition": "Tension Headache / Migraine",
            "next_steps": [
                "Rest in a quiet, dark room",
                "Apply cold compress to forehead",
                "Give paracetamol for pain relief",
                "Ensure adequate hydration"
            ],
            "danger_signs": [
                "Worst headache of life - sudden onset",
                "Headache with stiff neck and fever",
                "Confusion or difficulty speaking",
                "Headache after head injury"
            ],
            "patient_instruction_text": "Rest in a quiet dark room. Put cold cloth on forehead. Drink water. Take pain medicine if needed. If headache is very severe, sudden, or comes with fever and stiff neck, go to hospital immediately."
        }
    }
]

DEFAULT_DEMO_RESPONSE = {
    "triage": "Yellow",
    "likely_condition": "Condition requires clinical evaluation",
    "next_steps": [
        "Document all symptoms carefully",
        "Monitor patient condition",
        "Refer to Primary Health Center for evaluation",
        "Follow up within 24-48 hours"
    ],
    "danger_signs": [
        "High fever that doesn't respond to treatment",
        "Difficulty breathing",
        "Severe pain or discomfort",
        "Altered consciousness or confusion"
    ],
    "patient_instruction_text": "Your symptoms need to be checked by a doctor at the health center. Please go within 1-2 days. Watch for danger signs like high fever, breathing trouble, or severe pain - if these happen, go immediately."
}

DEMO_PICTOGRAM_MESSAGE = "In offline mode, visual pictograms cannot be generated. When online, DALL-E 3 will create custom visual instructions for the patient."

DEMO_AUDIO_MESSAGE = "Offline mode: Audio instructions are not available without internet. When connected, Text-to-Speech will provide spoken instructions in the patient's language."


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "assessment"
    if "last_triage_result" not in st.session_state:
        st.session_state.last_triage_result = None
    if "last_pictogram_url" not in st.session_state:
        st.session_state.last_pictogram_url = None
    if "last_audio_instructions" not in st.session_state:
        st.session_state.last_audio_instructions = None
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False


def get_demo_triage_response(symptoms: str) -> dict:
    """Get a pre-written triage response based on symptom keywords"""
    symptoms_lower = symptoms.lower() if symptoms else ""
    
    for demo in DEMO_TRIAGE_RESPONSES:
        for keyword in demo["keywords"]:
            if keyword in symptoms_lower:
                return demo["response"].copy()
    
    return DEFAULT_DEMO_RESPONSE.copy()


def login_screen():
    st.title("OJAS - AI Co-Pilot for Rural Healthcare")
    st.markdown("**Empowering ASHA workers with AI-powered health triage**")
    st.divider()
    
    st.subheader("Login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", type="primary"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")
            st.info("For demo: username = **asha**, password = **demo123**")


def encode_image_to_base64(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio using OpenAI Whisper"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    finally:
        os.unlink(tmp_file_path)


def generate_pictogram(patient_instructions: str, condition: str) -> str:
    """Generate a simple visual pictogram using DALL-E 3"""
    prompt = f"""Create a simple, clear medical pictogram instruction image for rural healthcare in India.
The image should be:
- Simple line art or icon style
- Easy to understand without reading text
- Culturally appropriate for rural India
- Show: {patient_instructions[:200]}
- Related to condition: {condition}
- Use soft, calming colors
- No complex medical terminology
- Style: Simple infographic with clear visual steps"""

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard"
    )
    return response.data[0].url


def generate_audio_instructions(instructions: str, language: str = "hi") -> bytes:
    """Generate audio instructions using OpenAI TTS"""
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=instructions
    )
    audio_bytes = b""
    for chunk in response.iter_bytes():
        audio_bytes += chunk
    return audio_bytes


def call_gpt_vision(symptom_text: str, encoded_image: str | None) -> dict:
    system_prompt = """You are an experienced medical triage assistant helping rural healthcare workers (ASHA workers) in India. 
    
Analyze the patient symptoms provided (text and/or image) and provide a structured triage assessment.

You MUST respond with valid JSON in exactly this format:
{
    "triage": "Green" or "Yellow" or "Red",
    "likely_condition": "string describing the most likely condition",
    "next_steps": ["step 1", "step 2", "step 3"],
    "danger_signs": ["sign 1", "sign 2"],
    "patient_instruction_text": "Simple, clear instructions for the patient in everyday language"
}

Triage levels:
- Green: Monitor at home, self-care sufficient
- Yellow: Refer to nearest clinic within 24-48 hours
- Red: Urgent referral to hospital immediately

Be thorough but concise. Focus on practical, actionable advice suitable for rural healthcare settings."""

    messages = [{"role": "system", "content": system_prompt}]
    
    user_content = []
    
    if symptom_text and symptom_text.strip():
        user_content.append({
            "type": "text",
            "text": f"Patient symptoms: {symptom_text}"
        })
    
    if encoded_image:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
        })
        if not symptom_text or not symptom_text.strip():
            user_content.insert(0, {
                "type": "text",
                "text": "Please analyze this medical image and provide a triage assessment."
            })
    
    messages.append({"role": "user", "content": user_content})
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        max_completion_tokens=2048
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


def save_case_to_csv(username: str, symptoms: str, triage_result: dict, had_image: bool, had_voice: bool = False, offline_mode: bool = False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_case = {
        "timestamp": timestamp,
        "user": username,
        "symptoms": symptoms[:200] if symptoms else "Image only",
        "triage": triage_result.get("triage", "Unknown"),
        "likely_condition": triage_result.get("likely_condition", "Unknown"),
        "next_steps": json.dumps(triage_result.get("next_steps", [])),
        "danger_signs": json.dumps(triage_result.get("danger_signs", [])),
        "patient_instructions": triage_result.get("patient_instruction_text", ""),
        "had_image": had_image,
        "had_voice": had_voice,
        "offline_mode": offline_mode
    }
    
    if os.path.exists(CASES_CSV):
        df = pd.read_csv(CASES_CSV)
        df = pd.concat([df, pd.DataFrame([new_case])], ignore_index=True)
    else:
        df = pd.DataFrame([new_case])
    
    df.to_csv(CASES_CSV, index=False)


def load_recent_cases(n: int = 5) -> pd.DataFrame:
    if os.path.exists(CASES_CSV):
        df = pd.read_csv(CASES_CSV)
        return df.tail(n).iloc[::-1]
    return pd.DataFrame()


def load_all_cases() -> pd.DataFrame:
    if os.path.exists(CASES_CSV):
        return pd.read_csv(CASES_CSV)
    return pd.DataFrame()


def get_triage_color(triage: str) -> str:
    colors = {
        "Green": "#28a745",
        "Yellow": "#ffc107", 
        "Red": "#dc3545"
    }
    return colors.get(triage, "#6c757d")


def display_triage_result(result: dict, show_multimedia: bool = True, is_offline: bool = False):
    triage = result.get("triage", "Unknown")
    color = get_triage_color(triage)
    
    st.markdown(f"""
    <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">Triage Level: {triage}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Likely Condition")
        st.info(result.get("likely_condition", "Not determined"))
        
        st.markdown("### Next Steps")
        next_steps = result.get("next_steps", [])
        for i, step in enumerate(next_steps, 1):
            st.write(f"{i}. {step}")
    
    with col2:
        st.markdown("### Danger Signs to Watch")
        danger_signs = result.get("danger_signs", [])
        for sign in danger_signs:
            st.warning(sign)
    
    st.divider()
    st.markdown("### Patient Instructions")
    st.success(result.get("patient_instruction_text", "No specific instructions available."))
    
    if show_multimedia:
        st.divider()
        col_pic, col_audio = st.columns(2)
        
        with col_pic:
            if is_offline:
                st.button("Generate Visual Pictogram", key="gen_pictogram", use_container_width=True, disabled=True)
                st.caption("Not available in offline mode")
            else:
                if st.button("Generate Visual Pictogram", key="gen_pictogram", use_container_width=True):
                    with st.spinner("Creating visual instructions..."):
                        try:
                            pictogram_url = generate_pictogram(
                                result.get("patient_instruction_text", ""),
                                result.get("likely_condition", "")
                            )
                            st.session_state.last_pictogram_url = pictogram_url
                        except Exception as e:
                            st.error(f"Could not generate pictogram: {str(e)}")
        
        with col_audio:
            if is_offline:
                st.button("Generate Audio Instructions", key="gen_audio", use_container_width=True, disabled=True)
                st.caption("Not available in offline mode")
            else:
                if st.button("Generate Audio Instructions", key="gen_audio", use_container_width=True):
                    with st.spinner("Creating audio instructions..."):
                        try:
                            audio_bytes = generate_audio_instructions(
                                result.get("patient_instruction_text", "No specific instructions.")
                            )
                            st.session_state.last_audio_instructions = audio_bytes
                        except Exception as e:
                            st.error(f"Could not generate audio: {str(e)}")
        
        if st.session_state.last_pictogram_url:
            st.markdown("### Visual Instructions for Patient")
            st.image(st.session_state.last_pictogram_url, caption="Visual guide for patient", use_container_width=True)
        
        if st.session_state.last_audio_instructions:
            st.markdown("### Audio Instructions")
            st.audio(st.session_state.last_audio_instructions, format="audio/mp3")


def case_history_page():
    st.title("Case History")
    st.caption("Search and filter all recorded cases")
    
    if st.button("Back to Assessment", key="back_to_assessment"):
        st.session_state.current_page = "assessment"
        st.rerun()
    
    st.divider()
    
    all_cases = load_all_cases()
    
    if all_cases.empty:
        st.info("No cases recorded yet. Go to Patient Assessment to analyze your first case.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search symptoms or condition", placeholder="e.g., fever, rash...")
    
    with col2:
        triage_filter = st.selectbox(
            "Filter by Triage Level",
            ["All", "Green", "Yellow", "Red"]
        )
    
    with col3:
        date_range = st.date_input(
            "Filter by Date Range",
            value=[],
            key="date_filter"
        )
    
    filtered_df = all_cases.copy()
    
    if search_query:
        search_lower = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["symptoms"].str.lower().str.contains(search_lower, na=False) |
            filtered_df["likely_condition"].str.lower().str.contains(search_lower, na=False)
        ]
    
    if triage_filter != "All":
        filtered_df = filtered_df[filtered_df["triage"] == triage_filter]
    
    if len(date_range) == 2:
        filtered_df["date"] = pd.to_datetime(filtered_df["timestamp"]).dt.date
        filtered_df = filtered_df[
            (filtered_df["date"] >= date_range[0]) &
            (filtered_df["date"] <= date_range[1])
        ]
        filtered_df = filtered_df.drop(columns=["date"])
    
    st.divider()
    
    st.markdown(f"### Showing {len(filtered_df)} of {len(all_cases)} cases")
    
    triage_counts = filtered_df["triage"].value_counts()
    col_g, col_y, col_r = st.columns(3)
    with col_g:
        st.metric("Green", triage_counts.get("Green", 0))
    with col_y:
        st.metric("Yellow", triage_counts.get("Yellow", 0))
    with col_r:
        st.metric("Red", triage_counts.get("Red", 0))
    
    st.divider()
    
    filtered_df_reversed = filtered_df.iloc[::-1]
    
    for idx, row in filtered_df_reversed.iterrows():
        triage_color = get_triage_color(row.get("triage", "Unknown"))
        offline_badge = " [OFFLINE]" if row.get("offline_mode") else ""
        
        with st.expander(f"**{row.get('timestamp', 'N/A')}** - {row.get('likely_condition', 'Unknown')} ({row.get('triage', 'N/A')}){offline_badge}"):
            st.markdown(f"""
            <div style="border-left: 4px solid {triage_color}; padding-left: 10px;">
            <strong>Triage:</strong> {row.get('triage', 'Unknown')}<br>
            <strong>Condition:</strong> {row.get('likely_condition', 'Unknown')}<br>
            <strong>Worker:</strong> {row.get('user', 'Unknown')}<br>
            <strong>Input Type:</strong> {'Voice ' if row.get('had_voice') else ''}{'Image ' if row.get('had_image') else ''}{'Text' if not row.get('had_voice') and not row.get('had_image') else ''}<br>
            <strong>Mode:</strong> {'Offline/Demo' if row.get('offline_mode') else 'Online (AI)'}<br>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Symptoms:**")
            st.write(row.get("symptoms", "N/A"))
            
            st.markdown("**Patient Instructions:**")
            instructions = row.get("patient_instructions", "N/A")
            if pd.notna(instructions):
                st.info(instructions)
            
            try:
                next_steps = json.loads(row.get("next_steps", "[]"))
                if next_steps:
                    st.markdown("**Next Steps:**")
                    for i, step in enumerate(next_steps, 1):
                        st.write(f"{i}. {step}")
            except:
                pass
            
            try:
                danger_signs = json.loads(row.get("danger_signs", "[]"))
                if danger_signs:
                    st.markdown("**Danger Signs:**")
                    for sign in danger_signs:
                        st.warning(sign)
            except:
                pass


def main_app():
    st.title("OJAS - AI Co-Pilot for Rural Healthcare")
    st.caption(f"Logged in as: **{st.session_state.username}** | AI-powered triage for ASHA workers")
    
    col_logout, col_history, col_mode = st.columns([1, 1, 1])
    with col_logout:
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.current_page = "assessment"
            st.rerun()
    with col_history:
        if st.button("View Case History", key="history_btn", use_container_width=True):
            st.session_state.current_page = "history"
            st.rerun()
    with col_mode:
        demo_mode = st.toggle("Offline/Demo Mode", value=st.session_state.demo_mode, key="demo_toggle")
        if demo_mode != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_mode
            st.rerun()
    
    if st.session_state.demo_mode:
        st.info("**Offline Mode Active**: Using pre-written triage responses. Cases will be saved locally and can be reviewed when back online. Voice recording and AI features are limited.")
    elif not OPENAI_API_KEY:
        st.warning("OpenAI API key not configured. Enable Offline/Demo Mode to use the app without internet.")
        st.info("On Replit: Go to the 'Secrets' tab and add OPENAI_API_KEY with your API key.")
    
    st.divider()
    
    st.subheader("Patient Assessment")
    
    if st.session_state.demo_mode:
        input_method = "Text Input"
        st.markdown("**Describe Patient Symptoms**")
        symptoms = st.text_area(
            "Symptoms",
            placeholder="Example: Child with fever for 2 days, cough, no appetite...",
            height=150,
            label_visibility="collapsed"
        )
        st.caption("Voice recording is not available in offline mode")
        voice_used = False
        
        col_img, _ = st.columns(2)
        with col_img:
            st.markdown("**Upload Image (Optional)**")
            uploaded_image = st.file_uploader(
                "Upload an image of the symptom (rash, wound, etc.)",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded image (analyzed offline with symptom keywords)", use_container_width=True)
    else:
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "Voice Recording"],
            horizontal=True
        )
        
        symptoms = ""
        voice_used = False
        
        col1, col2 = st.columns(2)
        
        with col1:
            if input_method == "Text Input":
                st.markdown("**Describe Patient Symptoms**")
                symptoms = st.text_area(
                    "Symptoms",
                    placeholder="Child with red itchy rash on arm for 3 days, no fever...",
                    height=150,
                    label_visibility="collapsed"
                )
            else:
                st.markdown("**Record Voice Description**")
                st.info("Click the microphone to record patient symptoms in any language")
                
                audio_bytes = st_audiorec()
                
                if audio_bytes:
                    st.success("Audio recorded! Processing with Whisper...")
                    with st.spinner("Transcribing audio..."):
                        try:
                            symptoms = transcribe_audio(audio_bytes)
                            voice_used = True
                            st.markdown("**Transcribed symptoms:**")
                            st.write(symptoms)
                        except Exception as e:
                            st.error(f"Could not transcribe audio: {str(e)}")
        
        with col2:
            st.markdown("**Upload Image (Optional)**")
            uploaded_image = st.file_uploader(
                "Upload an image of the symptom (rash, wound, etc.)",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded image", use_container_width=True)
    
    st.divider()
    
    button_label = "Analyze & Get Triage (Offline)" if st.session_state.demo_mode else "Analyze & Get Triage"
    
    if st.button(button_label, type="primary", use_container_width=True):
        has_symptoms = symptoms and symptoms.strip()
        has_image = uploaded_image is not None
        
        if not has_symptoms and not has_image:
            st.error("Please provide patient symptoms (text or voice) or upload an image to analyze.")
            return
        
        st.session_state.last_pictogram_url = None
        st.session_state.last_audio_instructions = None
        
        if st.session_state.demo_mode:
            with st.spinner("Analyzing symptoms with offline database..."):
                result = get_demo_triage_response(symptoms)
                
                st.session_state.last_triage_result = result
                
                save_case_to_csv(
                    username=st.session_state.username,
                    symptoms=symptoms,
                    triage_result=result,
                    had_image=has_image,
                    had_voice=voice_used,
                    offline_mode=True
                )
                
                st.divider()
                st.subheader("Triage Result (Offline)")
                display_triage_result(result, show_multimedia=True, is_offline=True)
        else:
            with st.spinner("Analyzing symptoms and image with AI..."):
                try:
                    encoded_image = None
                    if uploaded_image:
                        uploaded_image.seek(0)
                        encoded_image = encode_image_to_base64(uploaded_image)
                    
                    result = call_gpt_vision(symptoms, encoded_image)
                    
                    st.session_state.last_triage_result = result
                    
                    save_case_to_csv(
                        username=st.session_state.username,
                        symptoms=symptoms,
                        triage_result=result,
                        had_image=has_image,
                        had_voice=voice_used,
                        offline_mode=False
                    )
                    
                    st.divider()
                    st.subheader("Triage Result")
                    display_triage_result(result, show_multimedia=True, is_offline=False)
                    
                except Exception as e:
                    st.error(f"Error analyzing case: {str(e)}")
                    st.info("Try enabling Offline/Demo Mode to use the app without internet connection.")
    
    elif st.session_state.last_triage_result:
        st.divider()
        st.subheader("Previous Triage Result")
        display_triage_result(st.session_state.last_triage_result, show_multimedia=True, is_offline=st.session_state.demo_mode)
    
    st.divider()
    st.subheader("Recent Cases")
    
    recent_cases = load_recent_cases(5)
    if not recent_cases.empty:
        display_cols = ["timestamp", "user", "symptoms", "triage", "likely_condition"]
        available_cols = [col for col in display_cols if col in recent_cases.columns]
        display_df = recent_cases[available_cols].copy()
        display_df.columns = ["Time", "Worker", "Symptoms", "Triage", "Condition"][:len(available_cols)]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No cases recorded yet. Analyze a patient to see history here.")


def main():
    st.set_page_config(
        page_title="OJAS - AI Healthcare Co-Pilot",
        page_icon="🏥",
        layout="wide"
    )
    
    init_session_state()
    
    if not st.session_state.logged_in:
        login_screen()
    else:
        if st.session_state.current_page == "history":
            case_history_page()
        else:
            main_app()


if __name__ == "__main__":
    main()
