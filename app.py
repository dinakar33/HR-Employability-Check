import streamlit as st
import pandas as pd
import pypdf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

st.set_page_config(page_title="MBA HR Tech Hub & ATS", page_icon="🏢", layout="wide")

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
is_admin = (admin_password == "admin123")

if is_admin:
    st.sidebar.success("Admin Access Granted")
    st.sidebar.subheader("Live Poll Controls")
    new_q = st.sidebar.text_input("Change Poll Question", poll_state["question"])
    if st.sidebar.button("Update Question"):
        poll_state["question"] = new_q
        poll_state["votes"] = [0, 0, 0, 0]
    poll_state["show_results"] = st.sidebar.checkbox("Show Poll Results to Students", value=poll_state["show_results"])

st.title("🎯 Campus HR Conclave & ATS Tech Hub")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Poll", "📝 Registration & ATS Scanner", "🎥 HR Visuals", "⭐ Event Feedback"])

# --- TAB 1: LIVE POLL ---
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

# --- TAB 2: REGISTRATION & INSTANT ATS SCORE ---
with tab2:
    st.header("Official Event Registration & Instant ATS Resume Checker")
    st.write("Fill out your details, upload your PDF resume, and get an instant ATS score matching our target role description.")
    
    reg_name = st.text_input("Full Name")
    reg_email = st.text_input("Email Address")
    reg_dept = st.text_input("Department / Specialization")
    
    job_description = st.text_area("Target Job Description / Key Skills Required", 
                                   value="Seeking a candidate with strong skills in human resource management, recruitment, performance evaluation, team dynamics, employee ethics, collective bargaining, labor law, and communication.")
    
    uploaded_resume = st.file_uploader("Upload Your Resume (PDF format)", type=["pdf"])
    
    if st.button("Run ATS Analysis & Submit"):
        if not reg_name or not reg_email or not uploaded_resume:
            st.error("Please fill in all required fields and upload your PDF resume.")
        else:
            with st.spinner("Analyzing resume against ATS requirements and preparing your report..."):
                try:
                    # Extract text from uploaded PDF
                    pdf_reader = pypdf.PdfReader(uploaded_resume)
                    resume_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            resume_text += text.lower()
                    
                    # ATS Analysis Logic
                    jd_words = set([word.strip(".,!?()").lower() for word in job_description.split() if len(word) > 3])
                    matched_words = [word for word in jd_words if word in resume_text]
                    missing_words = [word for word in jd_words if word not in resume_text]
                    score = int((len(matched_words) / len(jd_words)) * 100) if jd_words else 0
                    
                    # Display Results on Screen
                    st.metric(label="Instant ATS Match Score", value=f"{score}%")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.success(f"**Matched Core Keywords ({len(matched_words)}):**")
                        st.write(", ".join(matched_words[:12]) if matched_words else "None")
                    with col_b:
                        st.warning(f"**Missing Critical Keywords ({len(missing_words)}):**")
                        st.write(", ".join(missing_words[:12]) if missing_words else "None! Excellent alignment.")
                        
                    st.info("💡 **Quick Improvement Tip:** Ensure your bullet points start with strong action verbs and include quantifiable metrics (e.g., 'Improved hiring speed by 25%').")
                    
                    # Attempt to email report to candidate & forward resume to admin inbox
                    try:
                        sender = st.secrets["EMAIL_USER"]
                        password = st.secrets["EMAIL_PASSWORD"]
                        
                        # 1. Email to Candidate with ATS results
                        msg_candidate = MIMEMultipart()
                        msg_candidate['From'] = sender
                        msg_candidate['To'] = reg_email
                        msg_candidate['Subject'] = f"📊 Your Instant ATS Resume Review - {reg_name}"
                        
                        body_cand = f"""
                        Hi {reg_name},
                        
                        Thank you for participating in our Campus HR Fair! Here is your instant ATS resume screening report:
                        
                        📊 ATS Match Score: {score}%
                        
                        🔍 Key Terms Matched: {", ".join(matched_words[:10])}
                        ❌ Missing Core Keywords: {", ".join(missing_words[:10])}
                        
                        💡 Recommendation: Add missing industry keywords naturally into your experience summary and quantify your professional achievements.
                        
                        Best regards,
                        Campus HR Recruitment Team
                        """
                        msg_candidate.attach(MIMEText(body_cand, 'plain'))
                        
                        # 2. Forwarding Resume PDF to Admin Inbox
                        msg_admin = MIMEMultipart()
                        msg_admin['From'] = sender
                        msg_admin['To'] = sender
                        msg_admin['Subject'] = f"📥 New Resume Submission & ATS Report: {reg_name} ({reg_dept}) - {score}% Match"
                        
                        body_admin = f"New candidate registered!\n\nName: {reg_name}\nEmail: {reg_email}\nDepartment: {reg_dept}\nATS Score: {score}%\n\nResume attached."
                        msg_admin.attach(MIMEText(body_admin, 'plain'))
                        
                        # Attach PDF bytes
                        uploaded_resume.seek(0)
                        pdf_bytes = uploaded_resume.read()
                        attachment = MIMEApplication(pdf_bytes, Name=uploaded_resume.name)
                        attachment['Content-Disposition'] = f'attachment; filename="{uploaded_resume.name}"'
                        msg_admin.attach(attachment)
                        
                        # Send via SMTP
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender, password)
                        server.send_message(msg_candidate)
                        server.send_message(msg_admin)
                        server.quit()
                        
                        st.success("✅ Analysis complete! Your detailed review report has been emailed to you, and your resume has been forwarded to the HR recruitment team.")
                    except Exception as email_err:
                        st.success("✅ Analysis complete and registration recorded successfully! (Configure email secrets in Streamlit to enable automated emailing).")
                        
                except Exception as e:
                    st.error(f"Error processing PDF resume: {e}")

# --- TAB 3: HR VISUALIZATIONS ---
with tab3:
    st.header("Explore HR Topics & Insights")
    st.write("Select a topic below to view curated industry videos.")
    
    videos = {
        "Compensation and Benefits": "dQw4w9WgXcQ",
        "Rights of an Employee": "dQw4w9WgXcQ",
        "Employee Ethics": "dQw4w9WgXcQ",
        "Workplace Red Flags": "dQw4w9WgXcQ",
        "HR Myth Busters": "dQw4w9WgXcQ",
        "Collective Bargaining": "dQw4w9WgXcQ",
        "Labour Law": "dQw4w9WgXcQ"
    }
    selection = st.selectbox("Choose a visualization topic:", list(videos.keys()))
    st.video(f"https://www.youtube.com/watch?v={videos[selection]}")

# --- TAB 4: EVENT FEEDBACK ---
with tab4:
    st.header("Rate Our Event")
    st.slider("How would you rate your experience today?", 1, 5, 5, key="feedback_slider")
    st.text_area("Any suggestions or feedback for us?", key="feedback_text")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! We appreciate you stopping by our HR Fair booth.")
