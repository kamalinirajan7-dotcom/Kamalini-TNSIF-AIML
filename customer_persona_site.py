import time
from pathlib import Path
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"
DEMO_USERNAME, DEMO_PASSWORD = "dude", "dude123"
PERSONAS = {
    "Premium Customer": ("Customers with strong purchasing power and high engagement.", "Personalise benefits and loyalty recognition.", "#0f766e", 86),
    "High-Income Low-Spender": ("Customers with meaningful purchasing power who are selective spenders.", "Use relevant recommendations to deepen engagement.", "#2563eb", 52),
    "Budget-Conscious Customer": ("Customers who make considered, value-led spending decisions.", "Lead with accessible value and clear savings.", "#0891b2", 30),
}
ASSET_DIR = Path(__file__).parent / "assets" / "personas"
PERSONA_ART = {
    "Premium Customer": ASSET_DIR / "premium-customer.png",
    "High-Income Low-Spender": ASSET_DIR / "thoughtful-customer.png",
    "Budget-Conscious Customer": ASSET_DIR / "value-customer.png",
}


def setup():
    st.set_page_config("Customer Persona", layout="wide", initial_sidebar_state="collapsed")
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    .stApp{background:#fcfefd;color:#123b40;font-family:'DM Sans',sans-serif} #MainMenu,footer,header{visibility:hidden}.block-container{max-width:1180px;padding:1.7rem 2.2rem 3rem}
    .brand{color:#167b76;font-size:.74rem;font-weight:700;letter-spacing:.17em}.display,.title,.persona{font-family:'Playfair Display',serif;color:#123b40;letter-spacing:-.04em}.display{font-size:3.5rem;line-height:1.1;margin:.75rem 0 1rem;max-width:760px}.title{font-size:2.3rem;margin:.4rem 0 .7rem}.lead,.copy{color:#668187;line-height:1.7}.lead{font-size:1.08rem;max-width:660px}.navbrand{font-weight:700;letter-spacing:.1em;padding:.5rem 0 1.6rem;border-bottom:1px solid #e8f0ef;margin-bottom:1.5rem}.navbrand span{color:#117c76}.hero,.result-hero{border:1px solid #d8ebe8;border-radius:28px;padding:4.2rem;background:linear-gradient(118deg,#ecf8f6,#f9fdfc)}.card,.shell,.metric{background:#fff;border:1px solid #dcebea;box-shadow:0 12px 32px rgba(20,68,68,.045)}.card{border-radius:20px;padding:1.6rem;min-height:180px}.shell{border-radius:24px;padding:2.35rem}.metric{border-radius:16px;padding:1.25rem}.cardtitle{font-weight:700;font-size:1.18rem;color:#123b40;margin:.65rem 0}.index,.label{color:#167b76;font-size:.73rem;font-weight:700;letter-spacing:.12em}.persona{font-size:2.65rem;margin:.55rem 0}.score{height:12px;border-radius:99px;background:#dcefeb;overflow:hidden;margin:.75rem 0}.fill{height:100%;border-radius:99px;background:#117c76}.step{text-align:center;padding:1rem}.stepno{width:35px;height:35px;border-radius:50%;background:#e4f4f1;color:#117c76;font-weight:700;display:inline-flex;align-items:center;justify-content:center}.login{max-width:470px;margin:8vh auto;background:#fff;border:1px solid #dcebea;border-radius:25px;padding:2.75rem;box-shadow:0 22px 64px rgba(12,67,65,.08)}.stButton>button{border-radius:10px;min-height:46px;font-weight:700;border:1px solid #cddfdd;color:#245c5a}.stButton>button[kind="primary"]{background:#117c76;color:white;border-color:#117c76}.stTextInput input,.stNumberInput input{border-radius:10px;border-color:#cddfdd}@media(max-width:700px){.block-container{padding:1rem}.hero{padding:2.4rem 1.5rem}.display{font-size:2.5rem}.shell{padding:1.4rem}.login{padding:2rem 1.45rem;margin-top:3vh}}
    </style>""", unsafe_allow_html=True)
    st.markdown("""<style>
    .stApp{background:radial-gradient(circle at 14% 12%,rgba(245,213,224,.25),transparent 28%),radial-gradient(circle at 88% 76%,rgba(123,51,126,.46),transparent 27%),linear-gradient(130deg,#210635 0%,#420d4b 46%,#6667ab 100%);color:#fff;min-height:100vh}.stApp:before{content:'';position:fixed;inset:0;pointer-events:none;background-image:radial-gradient(circle at 18% 25%,#f5d5e0 0 1px,transparent 1.5px),radial-gradient(circle at 75% 18%,#f5d5e0 0 1px,transparent 1.5px),radial-gradient(circle at 60% 82%,#f5d5e0 0 1px,transparent 1.5px);opacity:.55}.navbrand{color:#f5d5e0;border-color:rgba(255,255,255,.2)}.navbrand span,.brand,.index,.label{color:#f5d5e0}.display,.title,.persona,.cardtitle{color:#fff;text-shadow:0 4px 20px rgba(24,3,45,.38)}.lead,.copy{color:rgba(255,255,255,.82)}.hero,.result-hero,.login,.shell,.card,.metric{background:linear-gradient(135deg,rgba(102,103,171,.36),rgba(66,13,75,.42));backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(245,213,224,.45);box-shadow:0 18px 42px rgba(19,2,41,.36),inset 0 1px 0 rgba(255,255,255,.13)}.hero{position:relative;overflow:hidden}.hero:after{content:'';position:absolute;width:260px;height:260px;right:-80px;top:-105px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#f5d5e0,#c980d9 38%,#7b337e 72%);filter:blur(1px);opacity:.45}.card,.metric{transition:transform .22s ease,box-shadow .22s ease}.card:hover,.metric:hover{transform:translateY(-5px);box-shadow:0 22px 44px rgba(251,156,235,.2)}.stButton>button{color:#fff!important;background:rgba(255,255,255,.1)!important;border-color:rgba(245,213,224,.55)!important;backdrop-filter:blur(12px)}.stButton>button[kind="primary"]{color:#300634!important;background:linear-gradient(100deg,#f5d5e0,#e780df)!important;border:0!important;box-shadow:0 10px 24px rgba(246,130,222,.3)}.stTextInput input,.stNumberInput input{background:rgba(255,255,255,.1)!important;color:#fff!important;border-color:rgba(245,213,224,.38)!important}.stTextInput label,.stNumberInput label,.stSlider label,.stSelectbox label,.stCaption{color:rgba(255,255,255,.86)!important}.stSlider [data-baseweb=slider] div[role=slider]{background:#f5d5e0}.score{background:rgba(245,213,224,.18)}.fill{background:linear-gradient(90deg,#f5d5e0,#dc72e2)}.moon-mascot{position:relative;width:132px;height:132px;border-radius:50%;background:radial-gradient(circle at 36% 30%,#fff4fb 0 7%,#f5d5e0 8% 35%,#c576da 63%,#7b337e 100%);box-shadow:0 0 0 12px rgba(245,213,224,.08),0 0 36px rgba(241,143,229,.65);margin:1rem auto}.moon-mascot:before{content:'•  •';white-space:pre;color:#420d4b;font-size:28px;letter-spacing:12px;position:absolute;top:42px;left:32px}.moon-mascot:after{content:'⌣';color:#420d4b;font-family:serif;font-size:31px;position:absolute;top:55px;left:50px}.mascot-wrap{position:absolute;right:5%;bottom:8%;z-index:2}.mascot-wrap .moon-mascot{width:112px;height:112px}.loader{padding:2.2rem;text-align:center;background:rgba(66,13,75,.52);border:1px solid rgba(245,213,224,.5);border-radius:24px;backdrop-filter:blur(18px);box-shadow:0 0 42px rgba(242,132,224,.28)}.orbit{width:150px;height:150px;border:2px solid rgba(245,213,224,.45);border-radius:50%;margin:0 auto 1rem;position:relative;animation:float 2s ease-in-out infinite}.orbit:before{content:'';width:28px;height:28px;border-radius:50%;background:#f5d5e0;box-shadow:0 0 20px #f5d5e0;position:absolute;top:-15px;left:58px}.loader .moon-mascot{width:92px;height:92px;margin:27px auto}.loader .moon-mascot:before{font-size:21px;top:29px;left:24px}.loader .moon-mascot:after{font-size:25px;top:41px;left:33px}@keyframes float{50%{transform:translateY(-8px) rotate(8deg)}}
    </style>""",unsafe_allow_html=True)
    st.markdown("""<style>
    .stApp{background:radial-gradient(circle at 12% 8%,rgba(245,213,224,.35),transparent 30%),radial-gradient(circle at 85% 20%,rgba(179,104,238,.4),transparent 27%),radial-gradient(circle at 82% 82%,rgba(245,91,202,.26),transparent 30%),linear-gradient(128deg,#210635 0%,#420d4b 42%,#6667ab 100%)}
    .hero,.result-hero,.login,.shell,.card,.metric{background:linear-gradient(135deg,rgba(129,108,200,.5),rgba(76,22,104,.57));border-color:rgba(245,213,224,.64);box-shadow:0 20px 52px rgba(15,0,38,.42),0 0 32px rgba(216,95,223,.12),inset 0 1px 0 rgba(255,255,255,.2)}
    .navbrand{display:block!important;font-family:'Playfair Display',serif;font-size:1.25rem}.login-intro{padding:4rem 2rem 3rem 1rem;min-height:440px;display:flex;flex-direction:column;justify-content:center}.login-intro .display{font-size:3.25rem}.login-panel-title{font-family:'Playfair Display',serif;color:#fff;font-size:2rem;text-align:center;margin-bottom:.25rem}.login-panel-copy{text-align:center;color:#f5d5e0;margin-bottom:1.1rem}.login-panel-mascot{transform:scale(.68);margin:-1.25rem auto -1.4rem}.stForm{background:linear-gradient(135deg,rgba(105,89,182,.42),rgba(47,9,75,.6));border:1px solid rgba(245,213,224,.62);border-radius:20px;padding:1.65rem 1.4rem 1.4rem!important;box-shadow:0 18px 38px rgba(19,2,41,.28);max-width:900px;margin:0 auto}.stForm [data-testid="stFormSubmitButton"] button{margin-top:.35rem;background:linear-gradient(100deg,#f5d5e0,#df87e6)!important;color:#310536!important;box-shadow:0 9px 22px rgba(238,136,223,.38)}.stTextInput input,.stNumberInput input,div[data-baseweb="input"] input{background:rgba(31,4,55,.82)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border-color:rgba(245,213,224,.58)!important;min-height:42px}.hero{min-height:315px}.mascot-wrap{right:8%;bottom:12%}.analysis-intro{max-width:720px;margin-bottom:1.2rem}.chart-card{background:linear-gradient(135deg,rgba(72,24,111,.55),rgba(37,5,71,.64));border:1px solid rgba(245,213,224,.35);border-radius:16px;padding:1rem .9rem .4rem;min-height:320px}
    @media(max-width:700px){.login-intro{padding:1.5rem .2rem;min-height:0}.login-intro .display{font-size:2.5rem}.stForm{max-width:none}}
    </style>""",unsafe_allow_html=True)
    for key, value in {"logged":False,"page":"login","prediction":None,"income":None,"score":None}.items(): st.session_state.setdefault(key,value)


def go(page): st.session_state.page=page; st.rerun()
def nav():
    st.markdown('<div class="navbrand">MOON <span>· CUSTOMER PERSONA</span></div>',unsafe_allow_html=True)
    a,b,c,_,e=st.columns([1,1,1,4,1])
    with a:
        if st.button("Home",use_container_width=True):go("home")
    with b:
        if st.button("Analyse",use_container_width=True):go("analysis")
    with c:
        if st.button("Insights",use_container_width=True):go("insights")
    with e:
        if st.button("Logout",use_container_width=True): st.session_state.logged=False;st.session_state.prediction=None;go("login")


def login():
    intro,signin=st.columns([1.08,.92],gap="large")
    with intro:
        st.markdown('<div class="login-intro"><div class="brand">MOON · CUSTOMER PERSONA</div><div class="display">Know Your Customers Better</div><p class="lead">Turn customer signals into clear, useful behavioural insight.</p><div class="moon-mascot"></div></div>',unsafe_allow_html=True)
    with signin:
        st.markdown('<div class="login-panel-mascot"><div class="moon-mascot"></div></div><div class="login-panel-title">Welcome back</div><div class="login-panel-copy">Sign in to continue</div>',unsafe_allow_html=True)
        with st.form("signin"):
            user=st.text_input("Username",placeholder="Enter your username")
            password=st.text_input("Password",type="password",placeholder="Enter your password")
            submit=st.form_submit_button("Sign In",type="primary",use_container_width=True)
    if submit:
        if user==DEMO_USERNAME and password==DEMO_PASSWORD: st.session_state.logged=True;go("home")
        else: st.error("We couldn’t sign you in with those details. Please check your username and password.")


def home():
    nav();st.markdown('<div class="hero"><div class="brand">CUSTOMER INTELLIGENCE</div><div class="display">Know Your Customer. Understand Their Behaviour.</div><div class="lead">Explore how income and spending patterns shape customer behaviour. Customer Persona turns meaningful customer signals into a clear behavioural view.</div><div class="mascot-wrap"><div class="moon-mascot"></div></div></div>',unsafe_allow_html=True);st.write('')
    for col,(n,title,text) in zip(st.columns(3),[("01","Understand","Bring annual income and spending behaviour into one focused profile."),("02","Segment","Identify the behavioural group that best reflects each customer."),("03","Discover","Use a clear persona to guide relevant conversations.")]):
        with col: st.markdown(f'<div class="card"><div class="index">{n}</div><div class="cardtitle">{title}</div><div class="copy">{text}</div></div>',unsafe_allow_html=True)
    st.write('');_,center,_=st.columns([1.3,1.4,1.3])
    with center:
        if st.button("Analyse a Customer",type="primary",use_container_width=True):go("analysis")


def analysis():
    nav();st.markdown('<div class="analysis-intro"><div class="brand">CUSTOMER ANALYSIS</div><div class="title">Build a customer profile</div><p class="lead">Enter annual income and spending score to identify the customer persona.</p></div>',unsafe_allow_html=True)
    with st.form("analyse"):
        left,right=st.columns(2)
        with left:
            income=st.number_input("Annual Income",min_value=.1,max_value=1000.,value=75.,step=1.,format="%.1f")
            st.caption("Currency: USD ($) · Amount in thousands")
        with right: score=st.slider("Spending Score",0,100,50);st.caption("0 = lower spending behaviour · 100 = higher spending behaviour")
        submit=st.form_submit_button("Analyse Customer",type="primary",use_container_width=True)
    if submit:
        loader=st.empty()
        loader.markdown('<div class="loader"><div class="orbit"><div class="moon-mascot"></div></div><div class="cardtitle">Analysing customer behaviour</div><div class="copy">Finding cluster · Generating persona</div></div>',unsafe_allow_html=True)
        with st.spinner("Preparing your result…"):
            time.sleep(.75)
            try:
                response=requests.post(API_URL,json={"annual_income_k":float(income),"spending_score":float(score)},timeout=12)
                result=response.json() if response.status_code==200 else None
                if not isinstance(result,dict) or "persona" not in result or "cluster" not in result: raise ValueError
            except requests.exceptions.Timeout: st.error("The analysis is taking longer than expected. Please try again in a moment.");return
            except (requests.RequestException,ValueError): st.error("We’re unable to analyse this customer right now. Please check the details and try again shortly.");return
        loader.empty();st.session_state.prediction=result;st.session_state.income=float(income);st.session_state.score=int(score);go("result")


def result():
    nav();data=st.session_state.prediction
    if not data: st.info("Start with a customer analysis to view a persona.");return
    persona=data.get("persona","Customer Persona");desc,focus,color,_=PERSONAS.get(persona,("This customer has been assigned to a behavioural group based on the details provided.","Use this persona to guide a relevant customer experience.","#117c76",50));income=st.session_state.income or data.get("annual_income_k",0);score=st.session_state.score if st.session_state.score is not None else data.get("spending_score",0)
    st.markdown('<div class="brand">ANALYSIS RESULT</div><div class="title">Customer persona identified</div>',unsafe_allow_html=True)
    persona_copy,persona_art=st.columns([3.2,1],vertical_alignment="center")
    with persona_copy:
        st.markdown(f'<div class="result-hero"><div class="label">CUSTOMER PERSONA</div><div class="persona">{persona}</div><div class="copy">{desc}</div></div>',unsafe_allow_html=True)
    with persona_art:
        art=PERSONA_ART.get(persona)
        if art and art.exists(): st.image(str(art),use_container_width=True)
    st.write('')
    for col,(label,value) in zip(st.columns(3),[('Cluster',str(data.get('cluster'))),('Annual Income',f'${income:,.1f}K'),('Spending Score',f'{int(score)}/100')]):
        with col:st.markdown(f'<div class="metric"><div class="copy">{label}</div><div class="cardtitle">{value}</div></div>',unsafe_allow_html=True)
    st.write('');left,right=st.columns([1.25,1])
    with left:st.markdown(f'<div class="metric"><div class="cardtitle">Spending behaviour</div><div class="score"><div class="fill" style="width:{float(score)}%"></div></div><div class="copy">{int(score)} out of 100 — a direct view of relative spending activity.</div></div>',unsafe_allow_html=True)
    with right:st.markdown(f'<div class="metric"><div class="cardtitle">Recommended focus</div><div class="copy">{focus}</div></div>',unsafe_allow_html=True)
    st.write('');a,b,_=st.columns([1.4,1.2,2])
    with a:
        if st.button("Analyse Another Customer",type="primary",use_container_width=True):st.session_state.prediction=None;go("analysis")
    with b:
        if st.button("View Insights",use_container_width=True):go("insights")


def insights():
    nav();st.markdown('<div class="brand">CUSTOMER INSIGHTS</div><div class="title">Three clear behavioural views</div><p class="lead">Personas create a shared language for interpreting customer behaviour and making each interaction more relevant.</p>',unsafe_allow_html=True)
    for col,(name,(desc,_,color,width)) in zip(st.columns(3),PERSONAS.items()):
        with col:st.markdown(f'<div class="card"><div class="cardtitle"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{color};margin-right:8px"></span>{name}</div><div class="copy">{desc}</div><div class="score" style="margin-top:1.4rem"><div class="fill" style="width:{width}%;background:{color}"></div></div></div>',unsafe_allow_html=True)
    st.write('')
    chart_left,chart_right=st.columns(2)
    with chart_left:
        st.markdown('<div class="cardtitle">Spending behaviour by persona</div><p class="copy">Typical spending score</p>',unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(5.3,3.1));fig.patch.set_facecolor('#2d0a51');ax.set_facecolor('#2d0a51')
        labels=['Premium','High-income\nlow-spender','Budget\nconscious'];values=[82,34,29];colors=['#54d7e8','#8c9cff','#ea78dc']
        bars=ax.bar(labels,values,color=colors,width=.56)
        ax.set_ylim(0,100);ax.set_ylabel('Spending score',color='#f5d5e0',fontsize=9);ax.tick_params(colors='#f5d5e0',labelsize=8);ax.grid(axis='y',alpha=.16,color='#f5d5e0');ax.spines[:].set_visible(False)
        for bar,value in zip(bars,values): ax.text(bar.get_x()+bar.get_width()/2,value+3,str(value),ha='center',color='#fff',fontsize=9,fontweight='bold')
        fig.tight_layout();st.pyplot(fig,use_container_width=True,clear_figure=True)
    with chart_right:
        st.markdown('<div class="cardtitle">Income vs spending map</div><p class="copy">Persona positions by annual income and spending score</p>',unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(5.3,3.1));fig.patch.set_facecolor('#2d0a51');ax.set_facecolor('#2d0a51')
        points=[('Premium',75,75,'#54d7e8'),('High-income low-spender',70,30,'#8c9cff'),('Budget-conscious',30,30,'#ea78dc')]
        for name,x,y,color in points: ax.scatter(x,y,s=105,c=color,edgecolors='#f5d5e0',linewidths=.8,label=name,zorder=3)
        ax.set_xlim(10,95);ax.set_ylim(10,100);ax.set_xlabel('Annual income (K)',color='#f5d5e0',fontsize=9);ax.set_ylabel('Spending score',color='#f5d5e0',fontsize=9);ax.tick_params(colors='#f5d5e0',labelsize=8);ax.grid(alpha=.15,color='#f5d5e0');ax.spines[:].set_visible(False)
        legend=ax.legend(loc='upper left',frameon=False,fontsize=7,labelcolor='#fff');fig.tight_layout();st.pyplot(fig,use_container_width=True,clear_figure=True)
    st.write('');st.markdown('<div class="brand">HOW IT WORKS</div><div class="title">From details to direction</div>',unsafe_allow_html=True)
    for col,(number,label) in zip(st.columns(4),[(1,'Enter details'),(2,'Analyse behaviour'),(3,'Identify group'),(4,'View persona')]):
        with col:st.markdown(f'<div class="step"><div class="stepno">{number}</div><div class="cardtitle">{label}</div></div>',unsafe_allow_html=True)


def run():
    setup()
    if not st.session_state.logged: login()
    elif st.session_state.page=="home": home()
    elif st.session_state.page=="analysis": analysis()
    elif st.session_state.page=="result": result()
    else: insights()


run()    
