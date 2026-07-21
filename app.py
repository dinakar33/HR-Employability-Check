import streamlit as st
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components

st.set_page_config(page_title="MBA HR Tech Hub", page_icon="🏢", layout="wide")

# --- GLOBAL STATE FOR LIVE POLLING ---
@st.cache_resource
def get_poll_state():
    return {
        "question": "What is the most critical factor in Team Dynamics (TD)?",
        "options": ["Clear Communication", "Trust & Psychological Safety", "Defined Roles", "Conflict Resolution"],
        "votes": [0, 0, 0, 0],
        "show_results": False
    }

poll_state = get_poll_state()

# --- ADMIN SIDEBAR ---
st.sidebar.title("🔐 Admin Login")
admin_password = st.sidebar.text_input("Enter Passcode", type="password")
is_admin = (admin_password == "admin123") # Change this password!

if is_admin:
    st.sidebar.success("Admin Access Granted")
    st.sidebar.subheader("Live Poll Controls")
    
    new_q = st.sidebar.text_input("Change Poll Question", poll_state["question"])
    if st.sidebar.button("Update Question"):
        poll_state["question"] = new_q
        poll_state["votes"] = [0, 0, 0, 0] # Reset votes
        
    poll_state["show_results"] = st.sidebar.checkbox("Show Poll Results to Students", value=poll_state["show_results"])

# --- MAIN APP TABS ---
st.title("🎯 Campus HR Conclave & ATS Scanner")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Poll", "📝 Registration & ATS", "🎥 HR Visuals", "⭐ Event Feedback"])

# --- TAB 1: LIVE POLLING ---
with tab1:
    st.header("Live Interactive Poll")
    st.write(f"**{poll_state['question']}**")
    
    col1, col2 = st.columns(2)
    for i, option in enumerate(poll_state["options"]):
        if col1.button(option, key=f"vote_{i}"):
            poll_state["votes"][i] += 1
            st.success(f"Vote cast for: {option}")
            
    if poll_state["show_results"]:
        st.subheader("Live Results")
        chart_data = pd.DataFrame({"Votes": poll_state["votes"]}, index=poll_state["options"])
        st.bar_chart(chart_data)
    else:
        st.info("The recruiter is hiding the results for now. Stay tuned!")

# --- TAB 2: REGISTRATION & ATS ---
with tab2:
    st.header("Step 1: Official Registration & Resume Upload")
    st.write("Please fill out this official form to submit your PDF resume to our secure database.")
    
    # 🔴 PASTE YOUR GOOGLE FORM IFRAME LINK HERE 🔴
    google_form_iframe = '<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSe-YOUR-FORM-LINK-HERE/viewform?embedded=true" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>'
    components.html(google_form_iframe, height=600)
    
    st.markdown("---")
    
    st.header("Step 2: Instant ATS Score")
    st.write("Want to see how your resume performed? Paste your resume text below for an instant scan!")
    
    name = st.text_input("Full Name (For ATS Report)")
    email = st.text_input("Email Address (To receive your report)")
    resume_text = st.text_area("Paste your resume text here:")
    
    if is_admin and resume_text and name and email:
        st.warning("Admin Mode: Ready to process ATS.")
        if st.button("Process ATS & Send Report Email"):
            with st.spinner("Analyzing and emailing..."):
                
                # Mock ATS Logic
                jd_words = ["recruitment", "dynamics", "compensation", "ethics", "law", "excel"]
                matched = [w for w in jd_words if w in resume_text.lower()]
                missing = [w for w in jd_words if w not in resume_text.lower()]
                score = int((len(matched) / len(jd_words)) * 100)
                
                st.metric("Score", f"{score}%")
                st.write("**Strengths (Found):**", ", ".join(matched))
                st.write("**Gaps (Missing):**", ", ".join(missing))
                
                # Send Email
                try:
                    sender = st.secrets["EMAIL_USER"]
                    password = st.secrets["EMAIL_PASSWORD"]
                    msg = MIMEText(f"Hi {name},\n\nYour ATS Score is {score}%.\n\nMissing Keywords: {', '.join(missing)}\n\nBest,\nHR Team")
                    msg['Subject'] = "Your ATS Resume Review"
                    msg['From'] = sender
                    msg['To'] = email
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, password)
                    server.send_message(msg)
                    server.quit()
                    st.success("✅ Detailed report emailed successfully!")
                except Exception as e:
                    st.error("Configure email secrets to send live emails.")
    elif not is_admin:
        st.info("Submit your text. The HR Admin at the booth will run your analysis!")

# --- TAB 3: HR VISUALIZATIONS ---
with tab3:
    st.header("Explore HR Topics")
    videos = {
        "Compensation and Benefits": "dQw4w9WgXcQ",
        "Rights of an Employee": "dQw4w9WgXcQ"
    }
    selection = st.selectbox("Choose a visualization topic:", list(videos.keys()))
    st.video(f"https://www.youtube.com/watch?v={videos[selection]}")

# --- TAB 4: EVENT FEEDBACK ---
with tab4:
    st.header("Rate Our Event")
    st.slider("How would you rate your experience today?", 1, 5, 5)
    st.text_area("Any suggestions for us?")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
