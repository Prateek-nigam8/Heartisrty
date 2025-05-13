# ❤️ Heartistry - The Art of Cardiovascular Wellness

## 🧠 Overview

**Heartistry** is an intelligent web-based platform built with **Streamlit** that helps users assess and manage heart health with ease.

It uses **machine learning and OCR** to automatically extract heart-related metrics from medical reports, supports **manual data entry**, and offers an **admin dashboard** for managing records.

---

## 🚀 Key Features

- 📄 Upload medical reports (PDF)
- 🔍 Extract health metrics using OCR and AI
- ✍️ Edit and review data manually if needed
- 📊 View analysis and receive actionable recommendations
- 📬 SOS email alerts to emergency contacts
- 🛠️ Admin dashboard to manage users and reports

---

## 📊 FINDINGS

This app demonstrates how users can:
- Upload their medical reports
- Automatically extract and analyze key metrics
- Manually review/edit extracted data
- Save data securely in a database
- Get health recommendations based on the findings

---

## 📂 User Report PDF (Sample)

You can explore and download sample medical reports for testing:

[📂 View All Sample Reports on Google Drive] (https://drive.google.com/drive/folders/1T4w3FuE6x-Bt6YVYUWNPQXtccvnKCSNW?usp=drive_link)

---

## 📈 Report PDF Analysis

### Extracted Data Example

| Metric            | Value     |
|-------------------|-----------|
| Age               | 22        |
| RestingBP         | 120 mmHg  |
| Cholesterol       | 119 mg/dL |
| Chest Pain Type   | Typical   |
| Smoking           | No        |

---

## 📌 Recommendations Based on Analysis

- ⚠️ Cholesterol is slightly low — consider a more nutrient-rich diet.
- ✅ Blood pressure is in the normal range — keep it maintained.
- 🚭 No smoking habits detected — very good.
- 🧠 No signs of severe heart risk, but routine checkups are encouraged.

---

## 📸 Screenshots



### 📄 PDF Analysis Output
![PDF Analysis Output](screenshots/analysis.png)

### 📝 Manual Entry Form (Editable Fields)
![Manual Entry Form](screenshots/form.png)

### 💡 Health Recommendation Section
![Recommendations](screenshots/recom.png)

### 🛠️ Admin Dashboard Interface
![Admin Dashboard](screenshots/admin1.png)
![Admin Dashboard](screenshots/admin2.png)

### 📬 SOS Email Received by User
![SOS Email](screenshots/email.png)

---

## 💻 How to Run Locally

### 1. Clone the Repo
```bash
git clone https://github.com/Prateek-nigam8/Heartisrty.git
-cd heartistry

2. Install Python Requirements
-pip install -r requirements.txt

3. Run the App
-streamlit run app.py
