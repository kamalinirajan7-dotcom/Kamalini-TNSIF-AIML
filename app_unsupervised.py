import streamlit as st
from customer_persona_site import run

try:
    run()
except Exception:
    st.error("Something prevented this page from loading. Please refresh and try again.")
raise SystemExit

import requests
import time
import textwrap
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Customer Persona Segmentation",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000/predict"

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin123"

# Approximate conversion used only for demo UI.
# The trained model uses income in USD thousands.
USD_TO_INR = 83.0


# ============================================================
# HELPER FOR HTML
# ============================================================

def render_html(content):
    """
    Safely render multiline HTML without Streamlit
    displaying the HTML tags as text.
    """
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(207, 239, 234, 0.55),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 85%,
                rgba(225, 242, 239, 0.65),
                transparent 30%
            ),
            #f7fbfa;
        color: #173b3b;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* -------------------------------------------------------
       TYPOGRAPHY
       ------------------------------------------------------- */

    .brand {
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 3px;
        color: #2b8179;
        margin-bottom: 12px;
    }

    .page-title {
        font-size: 38px;
        font-weight: 800;
        line-height: 1.15;
        color: #163b3b;
        margin-bottom: 10px;
    }

    .page-subtitle {
        font-size: 17px;
        line-height: 1.7;
        color: #658080;
        max-width: 760px;
    }


    /* -------------------------------------------------------
       LOGIN
       ------------------------------------------------------- */

    .login-wrapper {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid #dceceb;
        border-radius: 28px;
        padding: 48px;
        box-shadow: 0 20px 60px rgba(40, 100, 95, 0.08);
        margin: 60px auto 20px auto;
        max-width: 760px;
    }

    .login-title {
        font-size: 34px;
        font-weight: 800;
        color: #173b3b;
        margin-bottom: 10px;
    }

    .login-text {
        color: #6c8383;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 10px;
    }


    /* -------------------------------------------------------
       WELCOME HERO
       ------------------------------------------------------- */

    .hero {
        background: linear-gradient(
            135deg,
            #e9f8f5 0%,
            #f7fbfa 100%
        );
        border: 1px solid #d6ebe8;
        border-radius: 28px;
        padding: 52px;
        margin-bottom: 28px;
        box-shadow: 0 18px 45px rgba(43, 129, 121, 0.06);
    }

    .hero-title {
        font-size: 43px;
        font-weight: 850;
        line-height: 1.12;
        color: #153b3b;
        margin-bottom: 15px;
    }

    .hero-text {
        font-size: 17px;
        line-height: 1.8;
        color: #627979;
        max-width: 780px;
    }


    /* -------------------------------------------------------
       FEATURE CARDS
       ------------------------------------------------------- */

    .feature-card {
        background: #ffffff;
        border: 1px solid #e0ecea;
        border-radius: 20px;
        padding: 27px;
        min-height: 175px;
        box-shadow: 0 10px 28px rgba(30, 75, 72, 0.05);
    }

    .feature-number {
        font-size: 13px;
        font-weight: 800;
        color: #2b8179;
        letter-spacing: 2px;
        margin-bottom: 14px;
    }

    .feature-title {
        font-size: 21px;
        font-weight: 750;
        color: #193f3e;
        margin-bottom: 8px;
    }

    .feature-text {
        font-size: 14px;
        line-height: 1.7;
        color: #718585;
    }


    /* -------------------------------------------------------
       ANALYSIS CARD
       ------------------------------------------------------- */

    .analysis-card {
        background: #ffffff;
        border: 1px solid #dcebea;
        border-radius: 25px;
        padding: 32px;
        box-shadow: 0 15px 40px rgba(30, 75, 72, 0.06);
        margin-top: 20px;
        margin-bottom: 25px;
    }

    .section-label {
        font-size: 13px;
        font-weight: 800;
        color: #2b8179;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .section-heading {
        font-size: 28px;
        font-weight: 800;
        color: #173b3b;
        margin-bottom: 8px;
    }

    .section-description {
        color: #708282;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 22px;
    }


    /* -------------------------------------------------------
       RESULT
       ------------------------------------------------------- */

    .result-card {
        background: linear-gradient(
            135deg,
            #e6f7f3,
            #f7fbfa
        );
        border: 1px solid #cfe8e4;
        border-radius: 25px;
        padding: 40px;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 24px;
    }

    .result-label {
        color: #54817d;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .persona-name {
        color: #175f59;
        font-size: 36px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .cluster-text {
        color: #718686;
        font-size: 15px;
    }


    /* -------------------------------------------------------
       INSIGHT CARDS
       ------------------------------------------------------- */

    .insight-card {
        background: #ffffff;
        border: 1px solid #e1eceb;
        border-radius: 20px;
        padding: 26px;
        min-height: 170px;
        box-shadow: 0 10px 28px rgba(30, 75, 72, 0.04);
    }

    .insight-title {
        font-size: 18px;
        font-weight: 800;
        color: #204b49;
        margin-bottom: 13px;
    }

    .insight-text {
        color: #657b7b;
        font-size: 14px;
        line-height: 1.8;
    }


    /* -------------------------------------------------------
       STATUS
       ------------------------------------------------------- */

    .status-card {
        background: #f1faf8;
        border: 1px solid #d7ece9;
        border-radius: 16px;
        padding: 16px 20px;
        color: #39736d;
        font-size: 14px;
        margin-top: 12px;
    }


    /* -------------------------------------------------------
       FOOTER
       ------------------------------------------------------- */

    .footer {
        text-align: center;
        color: #8ba0a0;
        font-size: 12px;
        padding: 35px 0 10px 0;
        letter-spacing: 0.4px;
    }


    /* -------------------------------------------------------
       BUTTONS
       ------------------------------------------------------- */

    .stButton > button {
        border-radius: 12px;
        min-height: 46px;
        font-weight: 700;
        border: 1px solid #d1e4e1;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #2b8179;
        color: #216f69;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: #2b8179;
        color: white;
        border: none;
    }


    /* -------------------------------------------------------
       INPUTS
       ------------------------------------------------------- */

    div[data-baseweb="input"],
    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    div[data-baseweb="slider"] {
        padding-top: 10px;
    }


    /* -------------------------------------------------------
       MOBILE
       ------------------------------------------------------- */

    @media (max-width: 700px) {

        .block-container {
            padding: 1rem;
        }

        .login-wrapper {
            padding: 28px 22px;
            margin-top: 20px;
        }

        .hero {
            padding: 30px 23px;
        }

        .hero-title {
            font-size: 31px;
        }

        .page-title {
            font-size: 30px;
        }

        .persona-name {
            font-size: 27px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "prediction" not in st.session_state:
    st.session_state.prediction = None


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():

    render_html(
        """
        <div class="login-wrapper">

            <div class="brand">
                DATA DUDES
            </div>

            <div class="login-title">
                Customer Persona
            </div>

            <div class="login-text">
                Understand customer behaviour through
                intelligent segmentation powered by
                unsupervised machine learning.
            </div>

        </div>
        """
    )

    left, center, right = st.columns([1, 2, 1])

    with center:

        username = st.text_input(
            "Username",
            placeholder="Enter username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password"
        )

        st.write("")

        login_button = st.button(
            "Sign In",
            type="primary",
            use_container_width=True
        )

        if login_button:

            if (
                username == DEMO_USERNAME
                and password == DEMO_PASSWORD
            ):

                st.session_state.logged_in = True
                st.session_state.page = "welcome"

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

        st.caption(
            "Demo login: admin / admin123"
        )


# ============================================================
# WELCOME PAGE
# ============================================================

def show_welcome():

    top_left, top_right = st.columns([6, 1])

    with top_right:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.prediction = None

            st.rerun()

    render_html(
        """
        <div class="hero">

            <div class="brand">
                CUSTOMER INTELLIGENCE
            </div>

            <div class="hero-title">
                Understand Your Customers Better
            </div>

            <div class="hero-text">
                Discover meaningful customer personas from
                income and spending behaviour using
                unsupervised machine learning.
                Our K-Means model groups customers into
                behavioural segments to make customer
                analysis easier and more meaningful.
            </div>

        </div>
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    01
                </div>

                <div class="feature-title">
                    Understand
                </div>

                <div class="feature-text">
                    Identify meaningful patterns
                    in customer behaviour.
                </div>

            </div>
            """
        )

    with col2:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    02
                </div>

                <div class="feature-title">
                    Segment
                </div>

                <div class="feature-text">
                    Group customers into distinct
                    behavioural personas.
                </div>

            </div>
            """
        )

    with col3:

        render_html(
            """
            <div class="feature-card">

                <div class="feature-number">
                    03
                </div>

                <div class="feature-title">
                    Discover
                </div>

                <div class="feature-text">
                    Gain useful insights from
                    customer characteristics.
                </div>

            </div>
            """
        )

    st.write("")
    st.write("")

    left, center, right = st.columns([1, 2, 1])

    with center:

        if st.button(
            "Start Customer Analysis",
            type="primary",
            use_container_width=True
        ):

            st.session_state.page = "analysis"
            st.session_state.prediction = None

            st.rerun()


# ============================================================
# PERSONA DESCRIPTIONS
# ============================================================

PERSONA_INFO = {

    "Premium Customer": {

        "title": "Premium Customer",

        "description":
            "This customer shows relatively high income "
            "and strong spending behaviour. They belong "
            "to a high-engagement customer segment.",

        "action":
            "Premium services, loyalty benefits and "
            "personalised offers may be relevant."
    },

    "High-Income Low-Spender": {

        "title": "High-Income Low-Spender",

        "description":
            "This customer has relatively high income "
            "but comparatively lower spending behaviour.",

        "action":
            "Targeted promotions and personalised "
            "recommendations may help increase engagement."
    },

    "Budget-Conscious Customer": {

        "title": "Budget-Conscious Customer",

        "description":
            "This customer shows relatively lower income "
            "and lower spending behaviour.",

        "action":
            "Value-oriented products, discounts and "
            "budget-friendly offers may be relevant."
    }
}


# ============================================================
# ANALYSIS PAGE
# ============================================================

def show_analysis():

    top_left, top_right = st.columns([6, 1])

    with top_left:

        render_html(
            """
            <div class="brand">
                DATA DUDES · CUSTOMER INTELLIGENCE
            </div>
            """
        )

    with top_right:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.prediction = None

            st.rerun()

    render_html(
        """
        <div class="page-title">
            Customer Analysis
        </div>

        <div class="page-subtitle">
            Enter the customer's income and spending behaviour.
            The K-Means model will identify the most relevant
            customer persona.
        </div>
        """
    )


    # --------------------------------------------------------
    # INPUT CARD
    # --------------------------------------------------------

    render_html(
        """
        <div class="analysis-card">

            <div class="section-label">
                Customer Profile
            </div>

            <div class="section-heading">
                Tell us about the customer
            </div>

            <div class="section-description">
                Provide the annual income and spending score.
                The model will use these characteristics
                to identify the customer's behavioural segment.
            </div>

        </div>
        """
    )


    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    with col1:

        currency = st.selectbox(
            "Income Currency",
            [
                "USD ($)",
                "INR (₹)"
            ]
        )


    # --------------------------------------------------------
    # INCOME
    # --------------------------------------------------------

    with col2:

        if currency == "USD ($)":

            income = st.number_input(
                "Annual Income (thousand USD)",
                min_value=1.0,
                max_value=1000.0,
                value=75.0,
                step=1.0
            )

        else:

            income = st.number_input(
                "Annual Income (thousand INR)",
                min_value=1.0,
                max_value=100000.0,
                value=6250.0,
                step=10.0
            )


    # --------------------------------------------------------
    # SPENDING SCORE
    # --------------------------------------------------------

    spending_score = st.slider(
        "Spending Score",
        min_value=1,
        max_value=100,
        value=50,

        help=(
            "A higher score represents stronger "
            "spending behaviour."
        )
    )


    # --------------------------------------------------------
    # CONVERSION
    # --------------------------------------------------------

    if currency == "USD ($)":

        model_income = float(income)

        display_income = (
            f"${float(income):,.2f}K"
        )

        conversion_message = (
            f"Model input: {display_income} annual income"
        )

    else:

        model_income = float(income) / USD_TO_INR

        display_income = (
            f"₹{float(income):,.2f}K"
        )

        conversion_message = (
            f"Converted model input: "
            f"${model_income:,.2f}K annual income"
        )


    render_html(
        f"""
        <div class="status-card">
            {conversion_message}
        </div>
        """
    )


    st.write("")
    st.write("")


    # --------------------------------------------------------
    # PREDICT BUTTON
    # --------------------------------------------------------

    left, center, right = st.columns([1, 2, 1])

    with center:

        predict_button = st.button(
            "Predict Customer Persona",
            type="primary",
            use_container_width=True
        )


    if predict_button:

        st.session_state.prediction = None

        progress = st.progress(0)

        status = st.empty()


        # ----------------------------------------------------
        # LOADING
        # ----------------------------------------------------

        messages = [
            "Preparing customer information...",
            "Analysing income and spending behaviour...",
            "Finding behavioural patterns...",
            "Running customer segmentation...",
            "Generating customer persona..."
        ]


        for index, message in enumerate(messages):

            value = int(
                ((index + 1) / len(messages)) * 100
            )

            progress.progress(value)

            status.info(message)

            time.sleep(0.35)


        progress.empty()
        status.empty()


        # ----------------------------------------------------
        # API REQUEST
        # ----------------------------------------------------

        payload = {

            "annual_income_k":
                model_income,

            "spending_score":
                spending_score
        }


        try:

            response = requests.post(
                API_URL,
                json=payload,
                timeout=10
            )


            if response.status_code == 200:

                result = response.json()

                st.session_state.prediction = result

                st.rerun()


            else:

                st.error(
                    f"Prediction failed. "
                    f"Backend returned status "
                    f"{response.status_code}."
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to the FastAPI backend. "
                "Please start main_unsupervised.py "
                "on port 8000."
            )


        except requests.exceptions.Timeout:

            st.error(
                "The prediction request timed out. "
                "Please try again."
            )


        except Exception as error:

            st.error(
                f"Unexpected error: {error}"
            )


    # ========================================================
    # RESULT
    # ========================================================

    if st.session_state.prediction:

        result = st.session_state.prediction


        persona = result.get(
            "persona",
            "Unknown Persona"
        )


        cluster = result.get(
            "cluster",
            "Unknown"
        )


        info = PERSONA_INFO.get(
            persona,
            {
                "title": persona,
                "description":
                    "The customer has been assigned "
                    "to a behavioural segment based "
                    "on the trained clustering model.",
                "action":
                    "Use the identified segment to "
                    "guide customer analysis."
            }
        )


        # ----------------------------------------------------
        # RESULT CARD
        # ----------------------------------------------------

        render_html(
            f"""
            <div class="result-card">

                <div class="result-label">
                    Identified Customer Persona
                </div>

                <div class="persona-name">
                    {info["title"]}
                </div>

                <div class="cluster-text">
                    Customer Cluster {cluster}
                </div>

            </div>
            """
        )


        # ----------------------------------------------------
        # INSIGHT CARDS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)


        with col1:

            render_html(
                f"""
                <div class="insight-card">

                    <div class="insight-title">
                        Customer Profile
                    </div>

                    <div class="insight-text">

                        Annual Income:
                        <b>{display_income}</b>

                        <br><br>

                        Spending Score:
                        <b>{spending_score}/100</b>

                    </div>

                </div>
                """
            )


        with col2:

            render_html(
                f"""
                <div class="insight-card">

                    <div class="insight-title">
                        Behavioural Insight
                    </div>

                    <div class="insight-text">
                        {info["description"]}
                        <br><br>
                        <b>Suggested focus:</b>
                        {info["action"]}
                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # SIMPLE VISUAL INDICATOR
        # ----------------------------------------------------

        st.write("")
        st.write("")


        render_html(
            """
            <div class="section-label">
                Spending Behaviour
            </div>

            <div class="section-description">
                The customer's spending score is shown
                relative to the 1–100 behavioural scale.
            </div>
            """
        )


        chart_col1, chart_col2 = st.columns([4, 1])


        with chart_col1:

            chart_data = pd.DataFrame(
                {
                    "Spending Score": [
                        spending_score
                    ]
                }
            )


            fig, ax = plt.subplots(
                figsize=(8, 1.4)
            )


            ax.barh(
                ["Customer"],
                [spending_score]
            )


            ax.set_xlim(0, 100)

            ax.set_xlabel(
                "Spending Score"
            )

            ax.grid(
                axis="x",
                alpha=0.2
            )


            for spine in ax.spines.values():

                spine.set_visible(False)


            st.pyplot(
                fig,
                use_container_width=True
            )


        with chart_col2:

            st.metric(
                "Score",
                f"{spending_score}/100"
            )


        st.write("")
        st.write("")


        # ----------------------------------------------------
        # ANOTHER CUSTOMER
        # ----------------------------------------------------

        left, center, right = st.columns([1, 2, 1])

        with center:

            if st.button(
                "Analyse Another Customer",
                use_container_width=True
            ):

                st.session_state.prediction = None

                st.rerun()


# ============================================================
# APPLICATION ROUTING
# ============================================================

if not st.session_state.logged_in:

    show_login()

elif st.session_state.page == "welcome":

    show_welcome()

elif st.session_state.page == "analysis":

    show_analysis()


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">
        DATA DUDES · Customer Persona Segmentation ·
        Unsupervised Learning · K-Means Clustering
    </div>
    """
)
