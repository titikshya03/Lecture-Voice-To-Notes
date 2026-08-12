# 🎙️ Lecture Voice-to-Notes Generator

An AI-powered lecture processing application that converts recorded lecture audio into structured and easy-to-study notes.

The application allows students to upload a lecture recording, generate a transcript using **Microsoft Azure AI Speech**, and organize the lecture content into useful study material such as summaries and key concepts.

---

## ✨ Features

- 🎵 Upload lecture audio files
- 🎙️ Convert speech into text using Azure AI Speech
- 📝 Generate lecture transcripts
- 📌 Generate concise lecture summaries
- 🔑 Extract important key concepts
- 📚 Organize lecture content into study material
- 💾 Export generated notes
- 🎨 Clean and student-friendly Streamlit interface
- 🔐 Azure credentials managed securely using `.env`

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Frontend and web interface |
| Microsoft Azure AI Speech | Speech-to-text |
| python-dotenv | Environment variable management |
| Azure AI | AI-powered lecture processing |

---

## 📂 Project Structure

```text
Lecture-Voice-to-Notes/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── venv/
│
└── assets/
    └── ...
