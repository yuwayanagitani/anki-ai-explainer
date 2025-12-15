# AI Card Explainer (Anki Add-on)

AI Card Explainer generates a **concise explanation** for an Anki card using an AI model, and writes it into an **Explanation** field (HTML output).

It is built for medical / biology / nursing study workflows, where you want a short “why/how” explanation on the back of the card—without manually writing it every time.

---

## What it does

For a given note, the add-on:

1. Reads **Question** and **Answer** fields from the note
2. Sends them to an AI provider (OpenAI or Gemini)
3. Receives a short explanation (HTML)
4. Writes that HTML into your configured **Explanation field**

You can run it:
- for the **current card in the Reviewer**
- for **many notes at once** using a search query

---

## How to use

### 1) Generate for the current review card

You can generate an explanation while reviewing:

- **Reviewer “More…” menu** → `Generate AI Explanation (AI Card Explainer)`
- **Keyboard shortcut** (default: `Ctrl+Shift+L`)

After generation, the add-on attempts to redraw the current card so you can see the explanation immediately. citeturn2view0

---

### 2) Batch-generate using a search query

Menu item:
- **Tools** → `AI Card Explainer: generate for search results`

Flow:
1. You enter an Anki search query (default is the current deck, like `deck:"<current deck>"`)
2. The add-on finds matching notes
3. It generates explanations in the background
4. It reports how many notes were generated / skipped / errored

A safety limit is applied:
- `05_max_notes_per_run` (default: 50) citeturn2view0

---

## Installation

### Option 1: AnkiWeb (recommended)
Install via the usual Anki add-on flow and restart Anki.

### Option 2: GitHub / manual
Place the add-on folder into your Anki `addons21` directory, then restart Anki.

---

## Setup: API keys

AI Card Explainer needs an API key for the provider you select.

The add-on can read keys from:
- **Add-on config**, or
- **Environment variables** (fallback)

Environment variable defaults:
- OpenAI: `OPENAI_API_KEY`
- Gemini: `GEMINI_API_KEY` citeturn2view0

If no key is available, it will not run and will show a message like “API key not set.” citeturn2view0

---

## Configuration

Open:
- **Tools → Add-ons → (AI Card Explainer) → Config**

This add-on registers a **custom settings dialog** (via `setConfigAction`) when available. citeturn2view0

### Provider (01_*)

- `01_provider`  
  `openai` or `gemini`

OpenAI:
- `01_openai_api_key` (optional if using env var)
- `01_openai_model` (default: `gpt-4o-mini`)

Gemini:
- `01_gemini_api_key` (optional if using env var)
- `01_gemini_model` (default: `gemini-2.5-flash-lite`) citeturn2view0

---

### Field mapping (02_*)

- `02_question_field` (default: `Front`)
- `02_answer_field` (default: `Back`)
- `02_explanation_field` (default: `Explanation`) citeturn2view0

---

### Output language & style (03_*)

- `03_language`  
  `ja` for Japanese, otherwise English

- `03_explanation_style`  
  - `definition_and_mechanism` (default)
  - `full`
  - (and other values if your config GUI exposes them)

- `03_target_length_chars`  
  Target length for the explanation (clamped to 80–800 chars) citeturn2view0

Output format:
- The model is instructed to return **HTML only**. citeturn2view0

---

### Behavior when an explanation already exists (04_*)

- `04_on_existing_behavior`
  - `skip` (default): do nothing if Explanation already has content
  - `append`: add the new explanation after the existing text
  - otherwise: overwrite (treated as “replace” behavior)

- `04_append_separator`  
  Separator used for append (default is a horizontal rule style block) citeturn2view0

---

### Review / batch options (05_*)

- `05_review_shortcut`  
  Default: `Ctrl+Shift+L`

- `05_max_notes_per_run`  
  Default: `50` citeturn2view0

---

## Notes on networking

Requests are made with `requests` (Anki’s bundled environment).  
Timeouts are set to 40 seconds per request. citeturn2view0

---

## Troubleshooting

### “No current card.”
You triggered generation outside the Reviewer, or no card is loaded.

### “Skipped: Explanation already exists.”
Your `04_on_existing_behavior` is set to `skip` and the Explanation field is not empty.

### “API key not set.”
Set the key in config (`01_*_api_key`) or as an environment variable (`OPENAI_API_KEY` / `GEMINI_API_KEY`), then restart Anki.

### “API error: …”
This is returned when the provider request fails (network error, invalid key, rate limits, etc.). The add-on prints a traceback to help debugging. citeturn2view0

---

## Privacy

This add-on sends your card’s **Question + Answer** text to an external AI provider (OpenAI or Google Gemini) when enabled.  
Do not use it with sensitive or private data unless you understand the provider’s data handling policies.

---

## License

See the repository’s LICENSE file.
