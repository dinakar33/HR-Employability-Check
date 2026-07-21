# ... existing code ...
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- INITIALIZE INBOX QUEUE ---
if "candidate_queue" not in st.session_state:
    st.session_state.candidate_queue = []

st.set_page_config(page_title="MBA HR Tech Hub", page_icon="🏢", layout="wide")

# --- GLOBAL STATE FOR LIVE POLLING ---
# ... existing code ...
    # Toggle results visibility for students
    poll_state["show_results"] = st.sidebar.checkbox("Show Poll Results to Students", value=poll_state["show_results"])

    # --- ADMIN INBOX DASHBOARD ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Candidate Inbox")
    
    if len(st.session_state.candidate_queue) == 0:
        st.sidebar.info("No resumes submitted yet.")
    else:
        for i, candidate in enumerate(st.session_state.candidate_queue):
            # Create a dropdown for each candidate in the queue
            with st.sidebar.expander(f"📄 {candidate['name']}"):
                st.write(f"**Email:** {candidate['email']}")
                
                # 1. DOWNLOAD BUTTON
                st.download_button(
                    label="⬇️ Download PDF",
                    data=candidate["pdf_bytes"],
                    file_name=candidate["file_name"],
                    mime="application/pdf",
                    key=f"dl_{i}"
                )
                
                # 2. RUN ATS BUTTON
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
                            msg = MIMEText(f"Hi {candidate['name']},\n\nYour ATS Score is {score}%.\n\nMissing Keywords: {', '.join(missing)}\n\nBest,\nHR Team")
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
                            st.error("Email failed to send. Check configuration.")

# --- MAIN APP TABS ---
# ... existing code ...
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
# ... existing code ...
