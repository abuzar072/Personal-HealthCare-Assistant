

import streamlit as st
from groq import Groq
from streamlit_option_menu import option_menu
from fpdf import FPDF
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Virtual Doctor Assistant",
    page_icon="🩺",
    layout="wide"
)

# ==============================
# API KEY
# ==============================
# Better method:
# groq_api_key = os.getenv("GROQ_API_KEY")

groq_api_key = "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"

# ==============================
# GROQ CLIENT
# ==============================
client = Groq(api_key=groq_api_key)

# ==============================
# SESSION STATE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tip_index" not in st.session_state:
    st.session_state.tip_index = 0

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:

    st.image(
        "green and white modern medical logo.webp",
        width=220
    )

    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Doctor Chat", "Nutrition", "About"],
        icons=["house", "chat-dots", "apple", "info-circle"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {
                "padding": "5px",
                "background-color": "#0f0c29"
            },
            "icon": {
                "color": "#f5f0e1",
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "4px",
                "--hover-color": "#ffc13b",
            },
            "nav-link-selected": {
                "background-color": "#ff6e40",
            },
        }
    )

    st.session_state.page = selected

# ==============================
# CUSTOM CSS
# ==============================
st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #0f0c29 0%,
            #302b63 50%,
            #24243e 100%
        );
        color: white;
    }

    .stButton>button {
        background-color: #ff6e40;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #ffc13b;
        color: black;
        transform: scale(1.03);
    }

    .tip-container {
        border: 2px solid #ff6e40;
        padding: 20px;
        border-radius: 12px;
        font-size: 18px;
        text-align: center;
        font-weight: bold;
        background-color: rgba(255,255,255,0.08);
        margin-top: 20px;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# AI RESPONSE FUNCTION
# ==============================
def get_ai_response(prompt, system_role):

    try:

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_role
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="openai/gpt-oss-20b"
        )

        return chat_completion.choices[0].message.content

    except Exception as e:

        st.error(f"Error: {e}")

        return "Sorry, I could not generate a response."


# ==============================
# NUTRITION PLAN FUNCTION
# ==============================
def get_nutrition_plan(age, weight, height, goal, duration):

    bmi = weight / ((height / 100) ** 2)

    prompt = f"""
    Create a detailed nutrition plan for:

    Age: {age}
    Weight: {weight} kg
    Height: {height} cm
    BMI: {bmi:.1f}

    Goal: {goal}
    Duration: {duration}

    Include:
    - Daily meal plans
    - Healthy foods
    - Exercise routine
    - Water intake
    """

    return get_ai_response(
        prompt,
        "You are a professional nutritionist and fitness expert."
    )


# ==============================
# FIXED PDF GENERATOR
# ==============================
def generate_pdf(content, filename):

    try:

        pdf = FPDF()

        pdf.add_page()

        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_font("Arial", size=12)

        # Fix Unicode Characters
        safe_content = (
            content
            .replace("—", "-")
            .replace("–", "-")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("•", "*")
            .replace("…", "...")
        )

        # Convert unsupported characters
        safe_content = safe_content.encode(
            "latin-1",
            "replace"
        ).decode("latin-1")

        pdf.multi_cell(0, 10, safe_content)

        pdf.output(filename)

        return True

    except Exception as e:

        st.error(f"PDF Generation Error: {e}")

        return False


# ==============================
# HOME PAGE
# ==============================
def home():

    st.title("🩺 Virtual Doctor Assistant")

    st.write(
        "AI-powered healthcare assistant for health guidance, doctor chat, and nutrition planning."
    )

    st.image(
        "https://images.unsplash.com/photo-1584515933487-779824d29309",
        width=700
    )

    tips = [
        "🥗 Eat more fruits and vegetables daily.",
        "💧 Drink 2-3 liters of water every day.",
        "🏃 Exercise at least 30 minutes daily.",
        "😴 Sleep 7-8 hours for better health.",
        "🧘 Reduce stress through meditation."
    ]

    st.markdown(
        f"""
        <div class="tip-container">
            {tips[st.session_state.tip_index]}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Show Next Health Tip"):

        st.session_state.tip_index = (
            st.session_state.tip_index + 1
        ) % len(tips)


# ==============================
# DOCTOR CHAT PAGE
# ==============================
def doctor_chat():

    st.title("👨‍⚕️ Doctor Chat")

    st.write("Describe your symptoms and get AI guidance.")

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    prompt = st.chat_input("Enter your symptoms here...")

    if prompt:

        st.chat_message("user").markdown(prompt)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = get_ai_response(
            prompt,
            "You are a helpful AI doctor assistant. Provide healthcare advice and remind users to consult real doctors for emergencies."
        )

        with st.chat_message("assistant"):

            st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


# ==============================
# NUTRITION PAGE
# ==============================
def nutrition():

    st.title("🍎 Nutrition Planner")

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=25
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=300.0,
        value=70.0
    )

    height = st.number_input(
        "Height (cm)",
        min_value=50.0,
        max_value=250.0,
        value=170.0
    )

    goal = st.selectbox(
        "Goal",
        [
            "Lose Weight",
            "Gain Weight",
            "Maintain Weight"
        ]
    )

    duration = st.selectbox(
        "Duration",
        [
            "1 Week",
            "1 Month",
            "3 Months"
        ]
    )

    # Generate Plan
    if st.button("Generate Nutrition Plan"):

        with st.spinner("Generating nutrition plan..."):

            plan = get_nutrition_plan(
                age,
                weight,
                height,
                goal,
                duration
            )

            st.session_state.nutrition_plan = plan

            st.success("Nutrition Plan Generated!")

            st.markdown(plan)

    # Show Existing Plan
    if "nutrition_plan" in st.session_state:

        st.markdown(st.session_state.nutrition_plan)

        # Download PDF
        if st.button("Download PDF Report"):

            filename = "nutrition_plan_report.pdf"

            success = generate_pdf(
                st.session_state.nutrition_plan,
                filename
            )

            if success:

                with open(filename, "rb") as f:

                    st.download_button(
                        label="📥 Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )


# ==============================
# ABOUT PAGE
# ==============================
def about():

    st.title("ℹ️ About Us")
    st.write("Hello This Is Abuzar Ali Agentic And Robotics AI engineer. I am passionate about leveraging AI to create innovative solutions that improve lives. With a background in both healthcare and technology, I am dedicated to developing tools that make healthcare more accessible and personalized for everyone.")

    st.write("""
    We are building AI-powered healthcare tools to make
    healthcare guidance accessible for everyone.


    Features:
    - AI Doctor Chat
    - Nutrition Planning
    - PDF Reports
    - Modern Healthcare UI
             
         
    """)


# ==============================
# PAGE ROUTING
# ==============================
if st.session_state.page == "Home":

    home()

elif st.session_state.page == "Doctor Chat":

    doctor_chat()

elif st.session_state.page == "Nutrition":

    nutrition()

elif st.session_state.page == "About":

    about()
