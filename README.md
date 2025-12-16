# AI Card Explainer

**AI Card Explainer** is an Anki add-on that automatically generates **concise, high-quality explanations** for your flashcards using **large language models** (OpenAI or Google Gemini).  
It’s designed especially for **medical, nursing, life-science students**, and anyone who wants clean explanations without verbosity. :contentReference[oaicite:0]{index=0}

---

## 🔗 AnkiWeb Page

This add-on is also available on **AnkiWeb**:

👉 https://ankiweb.net/shared/info/1870119736

Please install from AnkiWeb for the easiest setup and automatic updates.

---

## 🎯 Features

- Automatically generates explanations from your card’s Question + Answer text. :contentReference[oaicite:1]{index=1}  
- Supports batch generation using any Anki search query. :contentReference[oaicite:2]{index=2}  
- Configurable provider: **OpenAI** or **Google Gemini**. :contentReference[oaicite:3]{index=3}  
- Customizable output style and length. :contentReference[oaicite:4]{index=4}  
- HTML formatting support for rich explanation rendering in cards. :contentReference[oaicite:5]{index=5}  

---

## 🚀 How It Works

1. Reads the **Question + Answer** fields from a note. :contentReference[oaicite:6]{index=6}  
2. Sends the text to the selected **AI provider**. :contentReference[oaicite:7]{index=7}  
3. Receives a concise explanation (HTML). :contentReference[oaicite:8]{index=8}  
4. Writes the explanation into your configured **Explanation field**. :contentReference[oaicite:9]{index=9}  

Behind the scenes, this pattern fits within modern AI-powered workflows for **spaced repetition learning** by helping you understand *why* answers are correct, not just *what* they are. :contentReference[oaicite:10]{index=10}

---

## 🚧 Installation

### ⬇️ From AnkiWeb (Recommended)

1. Open **Anki** → Tools → Add-Ons → Browse & Install.  
2. Search for **AI Card Explainer** and install.  
3. Restart Anki.

### 📦 From GitHub

1. Clone or download this repository into `~/.local/share/Anki2/addons21/anki-ai-explainer`.  
2. Restart Anki.

---

## 🔑 Setup — API Keys

This add-on requires API keys for your chosen provider:

| Provider | Env Var | Config Option |
|----------|---------|----------------|
| OpenAI | `OPENAI_API_KEY` | `01_openai_api_key` |
| Gemini | `GEMINI_API_KEY` | `01_gemini_api_key` | :contentReference[oaicite:11]{index=11}

If no key is found, the add-on will show an error message.

---

## ⚙️ Configuration

Open:  
**Tools** → **Add-Ons** → **AI Card Explainer** → **Config**

### Key Config Options

- `01_provider`: `"openai"` or `"gemini"`  
- Model selection (e.g., `gpt-4o-mini`, `gemini-2.5-flash-lite`)  
- Field mapping: question, answer, explanation fields  
- Output language, style, and target length  
- Behavior on existing explanations (skip / append / replace) :contentReference[oaicite:12]{index=12}

---

## 🧪 Usage

### 🔹 Single Card

While reviewing a card:  
**Reviewer → More… → Generate AI Explanation (AI Card Explainer)**  
or use shortcut: **Ctrl + Shift + L**. :contentReference[oaicite:13]{index=13}

### 🔹 Batch

**Tools → AI Card Explainer: generate for search results**  
Enter an Anki search (e.g., `deck:"Biology 2025"`) to generate explanations in bulk. :contentReference[oaicite:14]{index=14}

---

## ⚠️ Privacy and Safety

This add-on sends your card’s text to external services (OpenAI/Gemini).  
**Avoid using private/sensitive data** unless you understand the provider’s privacy policy. :contentReference[oaicite:15]{index=15}

---

## 🛠 Troubleshooting

| Issue | Solution |
|-------|----------|
| “No current card.” | Trigger generation during review. |
| “Explanation already exists.” | Adjust overwrite behavior in config. |
| “API key not set.” | Set API key in config or env vars. |
| API errors | Check network, rate limits, model settings. | :contentReference[oaicite:16]{index=16}

---

## 📜 License

This project is licensed under **MIT License**. :contentReference[oaicite:17]{index=17}
