# AI Card Explainer – Configuration Guide

This add-on automatically generates **concise medical explanations** for Anki notes  
(by sending a question + answer to OpenAI or Gemini).  
All settings can be adjusted in the Config screen.

---

## 1. Provider Settings (01_xxx)

### **01_provider**
- `"openai"` or `"gemini"`
- Selects which API to use.

### **01_openai_api_key**
- Your OpenAI API key.  
- If empty, the add-on will try the environment variable `OPENAI_API_KEY`.

### **01_openai_model**
- Model name used for OpenAI.
- Example:  
  - `"gpt-4o-mini"`  
  - `"gpt-4.1-mini"`  
  - `"gpt-4o"`  

### **01_gemini_api_key**
- Your Google Gemini API key.  
- If empty, the add-on will try the environment variable `GEMINI_API_KEY`.

### **01_gemini_model**
- Model name used for Gemini.
- Example:  
  - `"gemini-2.5-flash"`  
  - `"gemini-1.5-flash"`  

---

## 2. Field Settings (02_xxx)

### **02_input_fields**
- Array of field names to read from the note (in order).
- These fields are concatenated and sent to the AI.
- Default: `["Front", "Back"]`
- Example: `["Question", "Answer", "Context"]`

### **02_explanation_field**
- The field where the generated explanation will be written.
- Default: `"Explanation"`

---

## 3. User Prompt (03_xxx)

### **03_user_prompt**
- The prompt template sent to the AI model.
- Supports placeholders:
  - `{{fields}}` - Replaced with all input fields concatenated (e.g., "Front:\nvalue\n\nBack:\nvalue")
  - `{{FieldName}}` - Replaced with individual field values (e.g., `{{Front}}`, `{{Back}}`, `{{Question}}`)
  - Unknown field placeholders are replaced with empty strings
  
Example using `{{fields}}`:
```
Please provide a clear and concise explanation for:
{{fields}}
```

Example using individual fields:
```
Question: {{Front}}
Answer: {{Back}}
Please explain why this answer is correct.
```

Example mixing both:
```
Card content:
{{fields}}

Focus on: {{Question}}
```

**Note:** The system prompt automatically enforces HTML-only output, so you don't need to specify that.

---

## 4. Behavior for Existing Explanation (04_xxx)

### **04_on_existing_behavior**
- `"skip"`  
  - If the explanation field already contains text, do nothing.
- `"append"`  
  - Keep the old explanation and append new AI output.
- `"overwrite"`  
  - Replace the existing explanation completely.

### **04_append_separator**
- Separator used when `"append"` mode is active.  
- Default: `<hr>`.

---

## 5. Execution Settings (05_xxx)

### **05_max_notes_per_run**
- Maximum number of notes processed when running via **Tools → AI Card Explainer**.
- Prevents accidental processing of very large note sets.

### **05_review_shortcut**
- Keyboard shortcut used in the review screen to generate explanation for the current card.
- Default: **Ctrl+Shift+L**

You may change this to any valid Qt shortcut, such as:
- `"Ctrl+Shift+E"`
- `"Ctrl+Alt+X"`
- `"Alt+M"`

---

## Notes

- The add-on supports both **OpenAI** and **Gemini**.
- If API keys are not set in config, the add-on automatically checks  
  environment variables (`OPENAI_API_KEY` / `GEMINI_API_KEY`).
- Explanations are written in **HTML**, following the style:
  - `<p>Summary...</p>`
  - `<ul><li>Mechanism...</li></ul>`

---

## Example Config (default)

```json
{
  "01_provider": "gemini",
  "01_openai_api_key": "",
  "01_openai_model": "gpt-4o-mini",
  "01_gemini_api_key": "",
  "01_gemini_model": "gemini-2.5-flash-lite",

  "02_input_fields": ["Front", "Back"],
  "02_explanation_field": "Explanation",

  "03_user_prompt": "Please provide a clear and concise explanation for the following content from an Anki card:\n\n{{fields}}\n\nProvide an explanation that helps understand the concept, its context, and why it's important. Return the explanation in HTML format only, without using markdown code fences or backticks.",

  "04_on_existing_behavior": "append",
  "04_append_separator": "\n<hr>\n",

  "05_max_notes_per_run": 50,
  "05_review_shortcut": "Ctrl+Shift+L"
}
