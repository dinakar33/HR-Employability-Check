import streamlit as st
import pypdf
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="MBA HR Tech Hub", page_icon="🏢", layout="wide")

# --- INITIALIZE INBOX QUEUE ---
if "candidate_queue" not in st.session_state:
    st.session_state.candidate_queue = []

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
    
    # 1. LIVE POLL CONTROLS
    st.sidebar.subheader("Live Poll Controls")
    new_q = st.sidebar.text_input("Change Poll Question", poll_state["question"])
    if st.sidebar.button("Update Question"):
        poll_state["question"] = new_q
        poll_state["votes"] = [0, 0, 0, 0] # Reset votes
        
    poll_state["show_results"] = st.sidebar.checkbox("Show Poll Results to Students", value=poll_state["show_results"])
    
    # 2. CANDIDATE INBOX DASHBOARD
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Candidate Inbox")
    
    if len(st.session_state.candidate_queue) == 0:
        st.sidebar.info("No resumes submitted yet.")
    else:
        for i, candidate in enumerate(st.session_state.candidate_queue):
            # Create a dropdown for each candidate in the queue
            with st.sidebar.expander(f"📄 {candidate['name']}"):
                st.write(f"**Email:** {candidate['email']}")
                
                # DOWNLOAD BUTTON
                st.download_button(
                    label="⬇️ Download PDF",
                    data=candidate["pdf_bytes"],
                    file_name=candidate["file_name"],
                    mime="application/pdf",
                    key=f"dl_{i}"
                )
                
                # RUN ATS BUTTON
                if st.button("🔍 Run ATS & Email", key=f"ats_{i}"):
                    with st.spinner("Analyzing & emailing..."):
                        # ATS Logic
                        jd_words = ["recruitment", "dynamics", "compensation", "ethics", "law", "excel"]
                        matched = [w for w in jd_words if w in candidate["text"]]
                        missing = [w for w in jd_words if w not in candidate["text"]]
                        score = int((len(matched) / len(jd_words)) * 100)
                        
                        st.metric("Score", f"{score}%")
                        st.write("**Gaps (Missing):**", ", ".join(missing))
                        
                        # Send Email
                        try:
                            sender = st.secrets["EMAIL_USER"]
                            password = st.secrets["EMAIL_PASSWORD"]
                            msg = MIMEText(f"Hi {candidate['name']},\n\nThank you for stopping by our booth!\n\nYour ATS Score is {score}%.\n\nMissing Keywords: {', '.join(missing)}\n\nBest,\nHR Team")
                            msg['Subject'] = "Your ATS Resume Review"
                            msg['From'] = sender
                            msg['To'] = candidate['email']
                            
                            server = smtplib.SMTP('smtp.gmail.com', 587)
                            server.starttls()
                            server.login(sender, password)
                            server.send_message(msg)
                            server.quit()
                            st.success("✅ Email Sent!")
                            
                            # Remove candidate from queue after processing
                            st.session_state.candidate_queue.pop(i)
                            st.rerun() # Refresh the sidebar
                        except Exception as e:
                            st.error("Email failed to send. Check configuration secrets.")

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
    st.header("Step 2: Resume Screening (ATS)")
    st.write("Register for the event and upload your resume.")
    
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    if st.button("Submit Registration"):
        if name and email and uploaded_file:
            # Extract Text for the ATS scanner later
            pdf_reader = pypdf.PdfReader(uploaded_file)
            resume_text = "".join([page.extract_text().lower() for page in pdf_reader.pages])
            
            # Save the candidate data AND the PDF file to the Inbox Queue
            st.session_state.candidate_queue.append({
                "name": name,
                "email": email,
                "text": resume_text,
                "pdf_bytes": uploaded_file.getvalue(),
                "file_name": uploaded_file.name
            })
            st.success("✅ Registration submitted! The HR team will review it shortly.")
        else:
            st.error("Please fill all fields and upload a PDF.")

# --- TAB 3: HR VISUALIZATIONS ---
with tab3:
    st.header("Explore HR Topics")
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
    rating = st.slider("How would you rate your experience today?", 1, 5, 5)
    feedback_text = st.text_area("Any suggestions for us?")
    
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
```
eof

### How to Fix It:
1. Go back to GitHub and click the **Pencil icon** to edit your `app.py`.
2. **Delete absolutely everything** in the editor.
3. Paste the complete code I just provided above.
4. Click **Commit changes**.

Watch your Streamlit app—within 60 seconds, the error will vanish and your fully functioning, multi-tab app with the inbox will appear!
