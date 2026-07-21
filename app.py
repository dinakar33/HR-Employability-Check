import streamlit as st
import pypdf
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="MBA HR Tech Hub", page_icon="🏢", layout="wide")

# --- GLOBAL STATE FOR LIVE POLLING ---
# This ensures votes sync across all students' phones in real-time
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
    
    # Admin can change the question and options on the fly
    new_q = st.sidebar.text_input("Change Poll Question", poll_state["question"])
    if st.sidebar.button("Update Question"):
        poll_state["question"] = new_q
        poll_state["votes"] = [0, 0, 0, 0] # Reset votes
        
    # Toggle results visibility for students
    poll_state["show_results"] = st.sidebar.checkbox("Show Poll Results to Students", value=poll_state["show_results"])

# --- MAIN APP TABS ---
st.title("🎯 Campus HR Conclave & ATS Scanner")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Poll", "📝 Registration & ATS", "🎥 HR Visuals", "⭐ Event Feedback"])

# --- TAB 1: LIVE POLLING ---
with tab1:
    st.header("Live Interactive Poll")
    st.write(f"**{poll_state['question']}**")
    
    # Voting logic
    col1, col2 = st.columns(2)
    for i, option in enumerate(poll_state["options"]):
        if col1.button(option, key=f"vote_{i}"):
            poll_state["votes"][i] += 1
            st.success(f"Vote cast for: {option}")
            
    # Show results only if Admin toggled it on
    if poll_state["show_results"]:
        st.subheader("Live Results")
        chart_data = pd.DataFrame({"Votes": poll_state["votes"]}, index=poll_state["options"])
        st.bar_chart(chart_data)
    else:
        st.info("The recruiter is hiding the results for now. Stay tuned!")

# --- TAB 2: REGISTRATION & ATS ---
with tab2:
    st.header("Step 2: Resume Screening (ATS)")
    st.write("Register for the event and upload your resume for an instant ATS breakdown.")
    
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    # The JD you are measuring against
    jd = "Seeking skills in recruitment, team dynamics, compensation, employee ethics, and labor law."
    
    if is_admin and uploaded_file and name and email:
        st.warning("Admin Mode: You are viewing the backend ATS processor.")
        if st.button("Process ATS & Send Report Email"):
            with st.spinner("Analyzing and emailing..."):
                # Extract Text
                pdf_reader = pypdf.PdfReader(uploaded_file)
                resume_text = "".join([page.extract_text().lower() for page in pdf_reader.pages])
                
                # Mock ATS Logic (Strengths, Weaknesses, Improvements)
                jd_words = ["recruitment", "dynamics", "compensation", "ethics", "law", "excel"]
                matched = [w for w in jd_words if w in resume_text]
                missing = [w for w in jd_words if w not in resume_text]
                score = int((len(matched) / len(jd_words)) * 100)
                
                st.metric("Score", f"{score}%")
                st.write("**Strengths (Found):**", ", ".join(matched))
                st.write("**Gaps (Missing):**", ", ".join(missing))
                st.write("**Actionable Improvement:** Quantify your project impacts using exact numbers.")
                
                # Send Email Logic (Requires App Passwords as discussed before)
                try:
                    sender = st.secrets["EMAIL_USER"]
                    password = st.secrets["EMAIL_PASSWORD"]
                    msg = MIMEText(f"Hi {name},\n\nYour ATS Score is {score}%.\n\nMissing Keywords: {', '.join(missing)}\n\nImprovement tip: Add more quantifiable metrics to your project experience.\n\nBest,\nHR Team")
                    msg['Subject'] = "Your ATS Resume Review"
                    msg['From'] = sender
                    msg['To'] = email
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, password)
                    server.send_message(msg)
                    server.quit()
                    st.success("✅ Detailed report emailed to the candidate successfully!")
                except Exception as e:
                    st.error("Configure email secrets to send live emails.")
    elif not is_admin:
        st.info("Submit your details. The HR Admin at the booth will run your analysis!")

# --- TAB 3: HR VISUALIZATIONS ---
with tab3:
    st.header("Explore HR Topics")
    st.write("Select a topic below to view curated industry insights.")
    
    # Dictionary mapping topics to YouTube video IDs
    # (Swap the placeholder 'dQw4w9WgXcQ' strings with actual YouTube IDs)
    videos = {
        "Compensation and Benefits": "YOUR_YOUTUBE_ID_1",
        "Rights of an Employee": "YOUR_YOUTUBE_ID_2", 
        "Employee Ethics": "YOUR_YOUTUBE_ID_3",
        "Workplace Red Flags": "YOUR_YOUTUBE_ID_4",
        "HR Myth Busters": "YOUR_YOUTUBE_ID_5",
        "Collective Bargaining": "YOUR_YOUTUBE_ID_6",
        "Labour Law": "YOUR_YOUTUBE_ID_7"
    }
    
    selection = st.selectbox("Choose a visualization topic:", list(videos.keys()))
    st.video(f"https://www.youtube.com/watch?v={videos[selection]}")

# --- TAB 4: EVENT FEEDBACK ---
with tab4:
    st.header("Rate Our Event")
    rating = st.slider("How would you rate your experience today?", 1, 5, 5)
    feedback_text = st.text_area("Any suggestions for us?")
    
    if st.button("Submit Feedback"):
        # In a real app, you would append this to your Google Sheet
        st.success("Thank you for your feedback!")
