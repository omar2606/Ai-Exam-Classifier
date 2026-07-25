import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Exam Question Classifier By omar",
    page_icon="📚",
    layout="wide"
)

BACKEND_URL = "https://dramatic-art-feed.ngrok-free.dev"
HEADERS = {"ngrok-skip-browser-warning": "true"}

st.title("📚 AI-Powered Past Exam Question Classifier.")

st.write(
    "Upload past exam PDFs and provide the syllabus. "
    "The system will classify questions by chapter and generate a question bank."
)

# Upload PDFs
exam_files = st.file_uploader(
    "Upload Past Exam PDFs",
    type="pdf",
    accept_multiple_files=True
)

# Syllabus
syllabus = st.text_area(
    "Paste the syllabus here",
    height=250
)

# Generate button
generate = st.button("Generate Question Bank")

if generate:
    if not exam_files:
        st.error("Please upload at least one PDF.")

    elif not syllabus.strip():
        st.error("Please enter the syllabus.")

    else:
        # Prepare uploaded files
        files = [
            ("files", (pdf.name, pdf.getvalue(), "application/pdf"))
            for pdf in exam_files
        ]

        # Step 1: kick off the job (returns immediately, doesn't wait for processing)
        with st.spinner("Uploading files to the backend..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    headers=HEADERS,
                    data={"syllabus": syllabus},
                    files=files,
                    timeout=60  # this call should be fast now, it just starts the job
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend: {e}")
                st.stop()

        if response.status_code != 200:
            st.error("Backend Error")
            st.text(response.text)
            st.stop()

        job_id = response.json()["job_id"]

        # Step 2: poll for status instead of holding one long request open
        status_box = st.empty()
        progress_bar = st.progress(0)
        poll_count = 0

        while True:
            try:
                status_resp = requests.get(
                    f"{BACKEND_URL}/status/{job_id}",
                    headers=HEADERS,
                    timeout=30
                )
                status_data = status_resp.json()
            except requests.exceptions.RequestException as e:
                status_box.error(f"Lost connection while checking status: {e}")
                st.stop()

            status = status_data.get("status")

            if status == "done":
                progress_bar.progress(100)
                status_box.success("✅ Question bank generated successfully!")
                break

            elif status == "error":
                status_box.error(f"Processing failed: {status_data.get('error')}")
                st.stop()

            else:
                poll_count += 1
                status_box.info("⏳ Classifying your exam questions... this can take a few minutes.")
                progress_bar.progress(min(poll_count * 5, 95))
                time.sleep(5)

        # Step 3: fetch the finished PDF
        with st.spinner("Downloading your question bank..."):
            try:
                result_resp = requests.get(
                    f"{BACKEND_URL}/result/{job_id}",
                    headers=HEADERS,
                    timeout=60
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Could not download the result: {e}")
                st.stop()

        if result_resp.status_code == 200:
            st.download_button(
                label="📥 Download Question Bank",
                data=result_resp.content,
                file_name="Question_Bank.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Backend Error while downloading result")
            st.text(result_resp.text)