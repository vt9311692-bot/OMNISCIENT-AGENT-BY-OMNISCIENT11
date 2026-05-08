# 🧠 OMNISCIENT AGENT | IPL Akinator

A premium AI-powered IPL guessing game inspired by the Apple Music aesthetic. Think of an IPL cricketer, and the Omniscient Agent will guess it within 8 questions using its neural cricket brain!

## ✨ Features
- **Apple Music Glassmorphism UI**: Stunning dark-mode interface with animated gradient orbs and glass cards.
- **200+ Player Dataset**: Comprehensive data merged from multiple sources including squads from CSK, RCB, MI, PBKS, and more.
- **Witty Hinglish Persona**: The AI has a personality! Expect funny team slangs like *Whistle Podu Gang*, *Royal Chokers*, and *Paltan*.
- **Optimal Guessing**: Uses advanced binary search logic to narrow down suspects in exactly 8 questions.
- **"Sahi Pakde Hai!" Celebration**: Custom result screens with funny celebration lines.

## 🚀 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/OmniscientAgent.git
   cd OmniscientAgent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API Key:**
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
   *Note: You can also enter the key directly in the app's UI.*

4. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tech Stack
- **Framework**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Llama-3.1-8b-instant via Groq](https://groq.com/)
- **Styling**: Custom Vanilla CSS (Glassmorphism)
- **Data**: Excel (Openpyxl) & CSV

## 📜 License
MIT License
