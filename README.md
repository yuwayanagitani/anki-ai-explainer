# Anki AI Explainer

Anki add-on that generates an **HTML explanation** for the current card (or for a batch of notes) using an LLM.

This add-on is designed to be **simple and highly generic**:

- You can write **any prompt you want** (single “User prompt”).
- You can choose **any number of input fields** to send to the model (no hard limit).
- The add-on enforces that the model returns **HTML only** (to paste directly into an Anki field).
- Prompts support:
  - `{{fields}}` : all selected fields concatenated as `FieldName:\nvalue`
  - `{{FieldName}}` : access an individual field value directly (e.g. `{{Question}}`, `{{Answer}}`)

> The add-on intentionally does **not** provide built-in settings like language, style, or length.
> Put those instructions in your prompt.

---

## Features

- Generate explanation for the **current reviewer card** (via shortcut / reviewer context menu)
- Batch-generate explanations for notes matched by an **Anki search query** (Tools menu)
- Flexible behavior when the destination field already has content:
  - Skip / Overwrite / Append (with custom separator)
- Works with either:
  - **OpenAI** (Chat Completions API)
  - **Google Gemini** (Generative Language API)

---

## Installation

### From AnkiWeb
Install via AnkiWeb (recommended).  
(AnkiWeb URL will be added after publishing.)

### Manual install (GitHub)
1. Download this repository as a zip
2. Extract into your Anki add-ons folder:
   - `Tools → Add-ons → View Files`
3. Restart Anki

---

## Quick Start

1. Open add-on settings: `Tools → Add-ons → Anki AI Explainer → Config`
2. Set your provider and API key
3. Choose:
   - **Input fields** you want the model to read (e.g. `Question`, `Answer`, `Extra`)
   - **Explanation field** to write the output to (default: `Explanation`)
4. Write your **User prompt**
5. Generate explanations:
   - In review: press the shortcut (default `Ctrl+Shift+L`)
   - Or: open reviewer “More…” menu → *Generate AI Explanation*
   - Or: Tools → *AI Card Explainer: generate for search results*

---

## Prompt Placeholders

### `{{fields}}`
Expands to all selected input fields, concatenated in order:

Example expansion:
```
Question:
What is ATP?

Answer:
Adenosine triphosphate
```

### `{{FieldName}}`
Expands to the value of the individual field.

Example:
- `{{Question}}` → value of the `Question` field
- `{{Answer}}` → value of the `Answer` field

If a placeholder refers to a field that is missing/unavailable, it is replaced with an empty string.

---

## Example Prompts

### Minimal (recommended)
```
Explain the following Anki note in concise HTML.

{{fields}}
```

### Q/A style
```
<p><b>Q:</b> {{Question}}</p>
<p><b>A:</b> {{Answer}}</p>

Requirements:
- HTML only
- No greetings
- Use <ul><li> for lists
- Highlight key words with <b>
```

---

## Settings

Key settings (in `config.json`):

- `01_provider`: `openai` or `gemini`
- `01_openai_api_key`, `01_openai_model`
- `01_gemini_api_key`, `01_gemini_model`
- `02_input_fields`: array of field names to read (order matters)
- `02_explanation_field`: field name to write HTML output into
- `03_user_prompt`: your prompt template
- `04_on_existing_behavior`: `skip` / `overwrite` / `append`
- `04_append_separator`: used when appending
- `05_max_notes_per_run`: batch limit
- `05_review_shortcut`: reviewer shortcut

---

## Notes / Safety

- The add-on requests the model to return **HTML only**.
  Some models may still wrap output in Markdown fences (```html).  
  The add-on attempts to strip a single surrounding fence to reduce friction.
- Field values are passed to the model **as-is** (including any HTML contained in the note fields).
  Do not include sensitive data in notes if you do not want to send it to your provider.

---

## License

MIT License
