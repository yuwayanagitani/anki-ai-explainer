# AI Card Explainer

AnkiWeb: https://ankiweb.net/shared/by-author/2117859718

AI Card Explainer automatically generates concise, high-quality explanations for flashcards using large language models (OpenAI or Google Gemini). Designed for medical, nursing, and life-science students who want clean, exam-oriented explanations.

## Features
- Generates exam-focused explanations per-card
- Customizable prompt templates and length limits
- Supports single-note and batch generation
- Writes explanations into a target field without altering templates

## Requirements
- API key for selected AI provider (OpenAI, Gemini, etc.)
- Internet connection

## Installation
1. Tools → Add-ons → Open Add-ons Folder.
2. Place the add-on folder into `addons21/`.
3. Restart Anki.

## Usage
- Tools → AI Explainer → Generate explanation for selected notes.
- Configure which field to write to and the prompt template in settings.

## Configuration
`config.json`:
- provider, model, api_key location
- source_field, target_field
- prompt_template, max_tokens

Important sample:
```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "target_field": "Explanation",
  "prompt_template": "Provide a concise exam-style explanation..."
}
```

## Privacy & Safety
Do not send protected health information (PHI) or other sensitive data to third-party AI services.

## Issues & Support
Provide sample cards and desired output style when opening issues.

## License
See LICENSE.
