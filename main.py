import os
import pathway as pw
from transformers import pipeline
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()  

# ======================
# Gemini Setup
# ======================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-2.5-flash-lite")


# ======================
# Hugging Face Model
# ======================
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# ======================
# Log Classification
# ======================
def classify_log(line: str) -> str:
    """Classify a log line as normal, warning, or critical."""
    if not line.strip():
        return "unknown"
    result = classifier(line[:512])[0]
    label = result["label"]
    score = result["score"]
    if label == "NEGATIVE" and score > 0.6:
        return "critical"
    elif label == "NEGATIVE":
        return "warning"
    else:
        return "normal"

# ======================
# Gemini Explanation
# ======================
def explain_with_gemini(log: str, classification: str) -> str:
    """Ask Gemini to explain and suggest a fix."""
    if classification == "normal":
        return "No issue detected — system functioning normally."

    prompt = f"""
You are an expert DevOps assistant.
A system log was flagged as '{classification}' severity.

Log message:
{log}

Please explain the likely cause and suggest specific steps to fix or investigate it.
If possible, include preventive measures.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini explanation failed: {e}"

# ======================
# Stream Logs from Folder
# ======================
# logs = pw.io.fs.read(
#     path="./logs/",
#     format="plaintext",
#     mode="streaming"
# )

import subprocess
import threading

def stream_system_logs():
    """Continuously copy system logs into ./logs/live.log"""
    with open("./logs/live.log", "w") as f:
        process = subprocess.Popen(
            ["tail", "-F", "/var/log/system.log"],  # or /var/log/syslog
            stdout=f,
            stderr=subprocess.STDOUT
        )
        process.wait()

threading.Thread(target=stream_system_logs, daemon=True).start()

# then Pathway reads ./logs/live.log
logs = pw.io.fs.read(
    path="./logs/live.log",
    format="plaintext",
    mode="streaming"
)


# ======================
# Apply ML + Gemini
# ======================
classified_logs = logs.select(
    log=logs.data,
    classification=pw.apply(classify_log, logs.data),
)

# Add Gemini explanation only for non-normal logs
enhanced_logs = classified_logs.select(
    log=classified_logs.log,
    classification=classified_logs.classification,
    explanation=pw.apply(explain_with_gemini, classified_logs.log, classified_logs.classification)
)

# ======================
# Save to JSON output
# ======================
pw.io.fs.write(
    enhanced_logs,
    "./alerts/enhanced_logs.json",
    format="json"
)

# ======================
# Run the Streaming Pipeline
# ======================
pw.run()
