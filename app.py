import streamlit as st
import pypdf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- PAGE CONFIGURATION & EXECUTIVE STYLING ---
st.set_page_config(
    page_title="HR Blog | Executive Recruitment Platform", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MBA Executive Aesthetic
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-tagline {
        font-size: 1.2rem;
        color: #475569;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL SESSION STATE ---
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {
        "name": "",
        "email": "",
        "archetype": "Not Evaluated",
        "ats_score": 0,
        "test_score": 0,
        "gd_score": 0,
        "interview_score": 0
    }

@st.cache_resource
def get_poll_state():
    return {
        "question": "What is the most critical metric in post-merger cultural integration?",
        "options": ["Employee Retention Rate", "Leadership Alignment", "Compensation Parity", "Communication Transparency"],
        "votes": [0, 0, 0, 0],
        "show_results": False
    }

poll_state = get_poll_state()

# --- ADMIN SIDEBAR CONTROLS ---
st.sidebar.title("🔐 Executive Portal")
# YOU CAN CHANGE YOUR ADMIN PASSWORD HERE:
ADMIN_PASSCODE = "admin123" 
admin_input = st.sidebar.text_input("Admin Passcode", type="password")
is_admin = (admin_input == ADMIN_PASSCODE)

if is_admin:
    st.sidebar.success("🔒 Admin Control Active")
    st.sidebar.subheader("Live Poll Manager")
    new_q = st.sidebar.text_input("Poll Question", poll_state["question"])
    if st.sidebar.button("Push Question"):
        poll_state["question"] = new_q
        poll_state["votes"] = [0, 0, 0, 0]
    poll_state["show_results"] = st.sidebar.checkbox("Reveal Poll Results to Audience", value=poll_state["show_results"])
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Candidate Queue Overview")
    st.sidebar.info("All registered candidate scores sync in real-time.")

# --- MAIN HERO TITLE ---
st.markdown('<p class="main-header">HR Blog: Assessment Gauntlet</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-tagline">"Crack the Code, Know Your Worth." — Postgraduate Recruitment & Analytics Hub</p>', unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 Onboarding & Profile", 
    "📊 Stage 1: ATS Audit", 
    "📝 Stage 2: Aptitude Test", 
    "💬 Stage 3: Group Discussion", 
    "🎯 Stage 4: Interview & Passport", 
    "⚖️ Labor Rights & Visuals", 
    "⭐ Event Feedback"
])

# =========================================================================
# TAB 1: ONBOARDING & PERSONALITY SURVEY
# =========================================================================
with tab1:
    st.header("Candidate Registration & Behavioral Profiling")
    st.write("Enter your credentials and complete the 3-minute psychological survey to determine your corporate workplace archetype.")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=st.session_state["user_data"]["name"])
        email = st.text_input("Email Address", value=st.session_state["user_data"]["email"])
    with col2:
        department = st.selectbox("Specialization", ["MBA - Human Resources", "MBA - Finance", "MBA - Marketing", "MBA - Operations & Analytics"])
        
    st.subheader("Workplace Archetype Assessment")
    q1 = st.radio("1. When facing a complex corporate roadblock, your first instinct is to:", [
        "Analyze past data and formulate a structured framework",
        "Brainstorm a disruptive, out-of-the-box workaround",
        "Consult team members to build consensus and morale",
        "Execute immediately with tactical focus on deliverables"
    ])
    
    if st.button("Generate My Executive Profile"):
        if not name or not email:
            st.error("Please enter your name and email.")
        else:
            st.session_state["user_data"]["name"] = name
            st.session_state["user_data"]["email"] = email
            
            # Archetype assignment logic based on selection
            if "structured framework" in q1:
                archetype = "🛠️ The Strategist (Analytical, Data-Driven)"
            elif "disruptive" in q1:
                archetype = "💡 The Innovator (Adaptable, Risk-Tolerant)"
            elif "consensus" in q1:
                archetype = "🤝 The Connector (Empathetic, Diplomat)"
            else:
                archetype = "🎯 The Executor (Goal-Oriented, Dependable)"
                
            st.session_state["user_data"]["archetype"] = archetype
            st.success(f"Profile locked! Your assigned Workplace Archetype is: **{archetype}**")

# =========================================================================
# TAB 2: STAGE 1 - ATS AUDIT
# =========================================================================
with tab2:
    st.header("Stage 1: The Digital Gatekeeper (ATS Audit)")
    st.write("Upload your resume to run our keyword density and formatting readability check.")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"])
    target_role_jd = st.text_area("Target Job Description / Key Competencies", 
                                   value="Seeking candidates skilled in HR analytics, recruitment lifecycle management, labor law compliance, compensation structuring, and cross-functional team dynamics.")
    
    if uploaded_file and st.button("Run ATS Evaluation"):
        with st.spinner("Analyzing resume structure and keyword overlap..."):
            reader = pypdf.PdfReader(uploaded_file)
            resume_text = "".join([page.extract_text().lower() for page in reader.pages])
            
            keywords = ["analytics", "recruitment", "labor", "compensation", "dynamics", "compliance", "strategy", "metrics"]
            matched = [w for w in keywords if w in resume_text]
            missing = [w for w in keywords if w not in resume_text]
            score = int((len(matched) / len(keywords)) * 100)
            
            st.session_state["user_data"]["ats_score"] = score
            
            st.metric("ATS Match Score", f"{score}%")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**✅ Core Keywords Detected:**", ", ".join(matched) if matched else "None")
            with col_b:
                st.write("**⚠️ Critical Gaps (Missing):**", ", ".join(missing) if missing else "None")
                
            st.info("💡 **ATS Formatting Tip:** Ensure your document uses a single-column layout without tables or graphics to maintain 99% parsing readability.")

# =========================================================================
# TAB 3: STAGE 2 - APTITUDE & WRITTEN TEST
# =========================================================================
with tab3:
    st.header("Stage 2: Competency & Aptitude Assessment")
    st.write("Answer the core situational judgment questions below to evaluate your corporate readiness.")
    
    ans1 = st.radio("1. An employee reports feeling unfairly compensated compared to a peer hired externally for the same role. What is your HR intervention?", [
        "Dismiss the complaint as external market rates fluctuate.",
        "Conduct an immediate internal pay equity audit and evaluate job evaluation bands transparently.",
        "Offer a discretionary bonus to quiet the employee temporarily.",
        "Advise the employee to look for another job."
    ])
    
    ans2 = st.radio("2. A key department lead is resisting the implementation of a new AI-driven performance review tool. How do you approach this?", [
        "Mandate its use immediately under penalty of review.",
        "Ignore their resistance and roll it out anyway.",
        "Facilitate a focus group to address friction points, offer comprehensive training, and highlight efficiency gains.",
        "Scrap the tool entirely."
    ])
    
    if st.button("Submit Assessment"):
        test_score = 85 # Simulated professional score calculation
        st.session_state["user_data"]["test_score"] = test_score
        st.success(f"Assessment Submitted! Your Competency & Situational Intelligence Score: **{test_score} / 100**")

# =========================================================================
# TAB 4: STAGE 3 - GROUP DISCUSSION
# =========================================================================
with tab4:
    st.header("Stage 3: The Collaborative Arena (Group Discussion)")
    st.write("Review today's active corporate case studies evaluated by HR Moderators.")
    
    st.info("📌 **Active Case Study:** *'AI in Performance Reviews: Objective Efficiency vs. Algorithmic Bias in Workplace Promotion Cycles.'*")
    
    st.subheader("Evaluation Rubric Benchmark")
    col1, col2, col3 = st.columns(3)
    col1.metric("Communication", "9 / 10")
    col2.metric("Active Listening", "8 / 10")
    col3.metric("Conflict Resolution", "8.5 / 10")
    
    gd_score_input = st.slider("Moderator Score Allocation (Out of 30)", 10, 30, 24)
    if st.button("Save GD Rating"):
        st.session_state["user_data"]["gd_score"] = gd_score_input
        st.success(f"Group Discussion score updated: {gd_score_input}/30")

# =========================================================================
# TAB 5: STAGE 4 - INTERVIEW & FINAL TALENT PASSPORT
# =========================================================================
with tab5:
    st.header("Stage 4: Strategic HR Interview & Talent Passport")
    st.write("Review your cumulative recruitment readiness dossier below.")
    
    interview_score = 90
    st.session_state["user_data"]["interview_score"] = interview_score
    
    user = st.session_state["user_data"]
    total_index = int((user["ats_score"] + user["test_score"] + (user["gd_score"]/30*100) + user["interview_score"]) / 4)
    
    st.markdown("---")
    st.subheader(f"🛡️ Executive Talent Passport: {user['name'] if user['name'] else 'Candidate'}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Workplace Archetype:** {user['archetype']}")
        st.markdown(f"**Overall Readiness Index:** `{total_index}%` (Job Ready)")
        st.markdown(f"**Stage 1 (ATS Audit):** `{user['ats_score']}/100`")
        st.markdown(f"**Stage 2 (Written Test):** `{user['test_score']}/100`")
    with col2:
        st.markdown(f"**Stage 3 (Group Discussion):** `{user['gd_score']}/30`")
        st.markdown(f"**Stage 4 (HR Interview):** `{user['interview_score']}/100`")
        
    if st.button("Email My Complete Dossier Report"):
        if not user["email"]:
            st.error("Please provide an email address in Tab 1 first.")
        else:
            st.success(f"📬 Executive Passport summary successfully dispatched to {user['email']}!")

# =========================================================================
# TAB 6: LABOR RIGHTS & VISUALS HUB
# =========================================================================
with tab6:
    st.header("Employee Rights & Labor Literacy Spotlight")
    st.write("Essential regulatory knowledge every postgraduate professional must master before signing an offer letter.")
    
    with st.expander("📖 1. Offer Letter Fundamentals (CTC vs. Base vs. Variable)"):
        st.write("Always examine your Cost to Company (CTC) breakdown. Base salary determines your provident fund and gratuity calculations, whereas variable pay is contingent on individual and company performance metrics.")
        
    with st.expander("📖 2. Workplace Standards & Compliance (Working Hours & POSH)"):
        st.write("Familiarize yourself with statutory working hour caps, notice period buyouts, non-compete enforceability limitations, and strict Internal Complaints Committee (ICC) protections under POSH mandates.")
        
    with st.expander("🎥 Curated Industry Masterclasses (Video Hub)"):
        topic = st.selectbox("Select Learning Topic:", [
            "Compensation & Benefits Structure", 
            "Rights of an Employee", 
            "Corporate Ethics & Whistleblowing", 
            "Collective Bargaining & Labor Law"
        ])
        # Embedded sample educational placeholder video
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# =========================================================================
# TAB 7: EVENT FEEDBACK & LIVE POLL
# =========================================================================
with tab7:
    st.header("Event Experience & Live Poll")
    
    st.subheader("Live Audience Poll")
    st.write(f"**{poll_state['question']}**")
    
    c1, c2 = st.columns(2)
    for i, opt in enumerate(poll_state["options"]):
        if c1.button(opt, key=f"poll_opt_{i}"):
            poll_state["votes"][i] += 1
            st.success(f"Vote recorded for: {opt}")
            
    if poll_state["show_results"]:
        st.subheader("Live Poll Results")
        chart_df = pd.DataFrame({"Votes": poll_state["votes"]}, index=poll_state["options"])
        st.bar_chart(chart_df)
    else:
        st.info("Polling results are currently hidden by the HR Moderator.")
        
    st.divider()
    st.subheader("Rate Our Event Experience")
    rating = st.slider("Rate this workshop out of 5 stars:", 1, 5, 5)
    comment = st.text_area("Key takeaways or feedback:")
    if st.button("Submit Feedback"):
        st.success("Thank you for shaping the future of HR recruitment excellence!")
