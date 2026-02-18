from __future__ import annotations
import os
import re
from html import escape
import traceback
from typing import Optional, Dict, Any

import requests  # uses Anki's bundled venv

from aqt import mw, gui_hooks
from aqt.qt import QAction, QInputDialog, QKeySequence, QShortcut, QWidget
from aqt.utils import showInfo, showWarning, tooltip

AddonConfig = Dict[str, Any]


# ==============================
# Config helper
# ==============================

def _get_config() -> AddonConfig:
    cfg = mw.addonManager.getConfig(__name__)
    return cfg or {}


# Helpers to fetch numbered keys
def cfg_get(cfg: dict, key: str, default=None):
    return cfg.get(key, default)


# ==============================
# Prompt building
# ==============================

def _build_prompts(fields_text: str, fields_map: dict[str, str], cfg: AddonConfig) -> tuple[str, str]:
    """
    Build system and user prompts with the new simplified approach.
    - System prompt: enforces HTML-only output
    - User prompt: uses user-defined template with {{fields}} and {{FieldName}} substitution
    """
    # System prompt enforces HTML output only
    system_prompt = (
        "You are a helpful tutor. "
        "You must return your response in HTML format ONLY. "
        "Do NOT use markdown code fences or backticks. "
        "Do NOT wrap your response in ```html or ``` tags."
    )
    
    # Get user-defined prompt template
    user_prompt_template = cfg_get(cfg, "03_user_prompt", "")
    if not user_prompt_template:
        # Fallback to a simple default if not configured
        user_prompt_template = (
            "Please provide a clear and concise explanation for the following content:\n\n"
            "{{fields}}\n\n"
            "Provide an explanation that helps understand the concept."
        )
    
    # Substitute {{fields}} placeholder with actual field content
    user_prompt = user_prompt_template.replace("{{fields}}", fields_text)
    
    # Substitute individual {{FieldName}} placeholders with their values
    # Use regex to find all {{...}} patterns
    import re
    placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def replace_placeholder(match):
        field_name = match.group(1)
        # Return the field value if it exists, otherwise empty string
        return fields_map.get(field_name, "")
    
    user_prompt = placeholder_pattern.sub(replace_placeholder, user_prompt)
    
    return system_prompt, user_prompt


# ==============================
# API calls (OpenAI / Gemini)
# ==============================

def _call_openai(api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        # Note: max_tokens removed to allow model's default behavior.
        # Users can now control response length via their custom prompt instead
        # of having a hard-coded 512-token limit.
    }
    r = requests.post(url, headers=headers, json=body, timeout=40)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _call_gemini(api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": system_prompt + "\n\n" + user_prompt}]}]}
    r = requests.post(url, headers=headers, json=body, timeout=40)
    r.raise_for_status()
    data = r.json()
    parts = data["candidates"][0]["content"]["parts"]
    return parts[0]["text"].strip()


# ==============================
# Generate explanation for 1 note
# ==============================

def _generate_for_note(note) -> tuple[Optional[str], Optional[str]]:
    # 互換のため残しておくが、今後は main-thread 専用として使う想定
    cfg = _get_config()
    job, err = _prepare_note_job_from_note(note, cfg)
    if err:
        return None, err
    html, err2 = _generate_html(job["fields_text"], job["fields_map"], cfg)
    if err2:
        return None, err2
    ok, err3 = _apply_html_to_note(job["nid"], job["e_field"], html, job["behavior"], job["sep"])
    return (html, None) if ok else (None, err3)


def _prepare_note_job_from_note(note, cfg: AddonConfig) -> tuple[Optional[dict], Optional[str]]:
    """
    Prepare job data from a note using the new multi-field approach.
    Reads fields specified in 02_input_fields and concatenates them in "FieldName:\nvalue" format.
    Also creates a fields_map for individual field placeholder replacement.
    """
    input_fields = cfg_get(cfg, "02_input_fields", ["Front", "Back"])
    if not isinstance(input_fields, list) or not input_fields:
        input_fields = ["Front", "Back"]
    
    e_field = cfg_get(cfg, "02_explanation_field", "Explanation")

    # Read all input fields and concatenate
    field_parts = []
    fields_map = {}  # Map of field name to field value
    
    for field_name in input_fields:
        try:
            field_value = (note[field_name] or "").strip()
            # Add to fields_map even if empty (for consistent placeholder behavior)
            fields_map[field_name] = field_value
            
            if field_value:
                # Note: Field values are passed as-is to the LLM without sanitization.
                # This preserves HTML tags, formatting, and special characters that
                # may be important context for generating explanations.
                field_parts.append(f"{field_name}:\n{field_value}")
        except KeyError:
            # Field doesn't exist in this note type, don't add to map
            pass
    
    # If all fields are empty, we can't generate anything
    if not field_parts:
        return None, "All input fields are empty or missing."
    
    # Concatenate with double newline separator
    fields_text = "\n\n".join(field_parts)
    
    # Check explanation field
    try:
        existing_raw = note[e_field] or ""
    except KeyError:
        return None, "Explanation field does not exist."
    
    behavior = cfg_get(cfg, "04_on_existing_behavior", "skip")
    if existing_raw.strip() and behavior == "skip":
        return None, "Explanation already exists."
    
    sep = cfg_get(cfg, "04_append_separator", "\n<hr>\n")
    
    return {
        "nid": int(note.id),
        "e_field": e_field,
        "fields_text": fields_text,
        "fields_map": fields_map,
        "behavior": behavior,
        "sep": sep,
    }, None

_RE_WHOLE_FENCE = re.compile(
    r"^\s*```(?:\s*(?P<lang>[a-zA-Z0-9_-]+))?\s*\n(?P<body>.*)\n```\s*$",
    re.DOTALL,
)

def _strip_markdown_fences(s: str) -> str:
    if not s:
        return ""
    t = s.strip()

    # 「全文が1つの ```...``` で包まれている」場合だけ剥がす
    m = _RE_WHOLE_FENCE.match(t)
    if m:
        body = (m.group("body") or "").strip()
        lang = (m.group("lang") or "").lower()

        # 任意：HTMLっぽくない言語のときは剥がさない（保守的）
        # 例: json / python が来たらそのまま返す
        if lang and lang not in ("html", "htm", "xml"):
            return t

        return body

    # それ以外は何もしない（消しすぎ防止）
    return t


def _generate_html(fields_text: str, fields_map: dict[str, str], cfg: AddonConfig) -> tuple[Optional[str], Optional[str]]:
    system_prompt, user_prompt = _build_prompts(fields_text, fields_map, cfg)
    provider = cfg_get(cfg, "01_provider", "openai")
    if provider == "openai":
        api_key = cfg_get(cfg, "01_openai_api_key") or os.getenv("OPENAI_API_KEY")
        model = cfg_get(cfg, "01_openai_model", "gpt-4o-mini")
    else:
        api_key = cfg_get(cfg, "01_gemini_api_key") or os.getenv("GEMINI_API_KEY")
        model = cfg_get(cfg, "01_gemini_model", "gemini-2.5-flash-lite")

    if not api_key:
        return None, "API key not set."

    try:
        if provider == "openai":
            raw = _call_openai(api_key, model, system_prompt, user_prompt)
        else:
            raw = _call_gemini(api_key, model, system_prompt, user_prompt)

        html_out = _strip_markdown_fences(raw)

        # 任意：最低限の安全チェック（事故防止）
        if html_out and not html_out.lstrip().startswith("<"):
            # ここは好み。エラーにするなら return None, ...
            # とりあえずそのまま通すならコメントアウトでOK
            pass

        return html_out, None

    except Exception as e:
        traceback.print_exc()
        return None, f"API error: {e}"


def _apply_html_to_note(nid: int, e_field: str, html: str, behavior: str, sep: str) -> tuple[bool, Optional[str]]:
    # ★ note/col 操作はメインスレッド側で行う前提
    note2 = mw.col.get_note(nid)
    existing_raw = note2[e_field] or ""
    existing = existing_raw.strip()
    if existing and behavior == "skip":
        return False, "Explanation already exists."
    if existing and behavior == "append":
        note2[e_field] = existing_raw + (sep or "\n<hr>\n") + html
    else:
        note2[e_field] = html
    note2.flush()
    return True, None

# ==============================
# Current card in reviewer
# ==============================

def _generate_for_current_card() -> None:
    reviewer = getattr(mw, "reviewer", None)
    card = getattr(reviewer, "card", None) if reviewer else None
    if not card:
        tooltip("No current card.")
        return

    note = card.note()
    cfg = _get_config()
    job, err = _prepare_note_job_from_note(note, cfg)
    if err:
        tooltip(f"Skipped: {err}")
        return

    def worker():
        return _generate_html(job["fields_text"], job["fields_map"], cfg)

    def on_done(fut):
        try:
            result = fut.result()
        except Exception as e:
            showWarning(f"AI Card Explainer failed:\n{e}")
            traceback.print_exc()
            return
        finally:
            mw.progress.finish()
        if not result:
            tooltip("Empty result.")
            return
        html, err = result
        if html:
            ok, err2 = _apply_html_to_note(job["nid"], job["e_field"], html, job["behavior"], job["sep"])
            if not ok:
                tooltip(f"Skipped: {err2}")
                return
            tooltip("AI explanation generated.")
            # ★ ここで「今表示しているカードを描き直す」
            try:
                if mw.reviewer and mw.reviewer.card is card:
                    mw.reviewer._redraw_current_card()
            except Exception:
                # 失敗してもレビュー自体が落ちないようにする
                pass

        else:
            tooltip(f"Skipped: {err}")

    mw.progress.start(label="Generating AI explanation...", immediate=True)
    mw.taskman.run_in_background(worker, on_done)


# ==============================
# Tools menu batch run
# ==============================

def _on_tools_generate_with_search() -> None:
    cfg = _get_config()
    deck_name = mw.col.decks.current()["name"]
    default_search = f'deck:"{deck_name}"'

    search, ok = QInputDialog.getText(
        mw,
        "AI Card Explainer",
        "Enter search query for notes:",
        text=default_search,
    )
    if not ok or not search.strip():
        return

    nids = mw.col.find_notes(search)
    if not nids:
        showInfo("No matching notes.")
        return

    max_notes = int(cfg_get(cfg, "05_max_notes_per_run", 50))
    target = nids[:max_notes]

    # ★ 先に main thread で必要情報だけ抜き出す（max_notes が小さい想定なので軽い）
    jobs = []
    pre_skipped = 0
    for nid in target:
        note = mw.col.get_note(nid)
        job, err = _prepare_note_job_from_note(note, cfg)
        if err:
            pre_skipped += 1
        else:
            jobs.append(job)

    def worker():
        results = []
        for job in jobs:
            html, err = _generate_html(job["fields_text"], job["fields_map"], cfg)
            results.append((job, html, err))
        return {"results": results, "total": len(target), "pre_skipped": pre_skipped}

    def on_done(fut):
        try:
            st = fut.result()
        except Exception as e:
            showWarning(f"AI Card Explainer batch failed:\n{e}")
            traceback.print_exc()
            return
        finally:
            mw.progress.finish()
        okc = sk = er = 0
        for job, html, err in st["results"]:
            if html:
                ok, err2 = _apply_html_to_note(job["nid"], job["e_field"], html, job["behavior"], job["sep"])
                if ok:
                    okc += 1
                else:
                    sk += 1
            else:
                er += 1
        sk += int(st.get("pre_skipped", 0))
        showInfo(
            "AI explanation batch finished.\n"
            f"Notes: {st['total']}\n"
            f"Generated: {okc}\n"
            f"Skipped: {sk}\n"
            f"Errors: {er}"
        )

    mw.progress.start(label="Batch generating explanations...", immediate=True)
    mw.taskman.run_in_background(worker, on_done)


# ==============================
# Reviewer “More…” menu
# ==============================

def _on_reviewer_context_menu(reviewer, menu):
    act = menu.addAction("Generate AI Explanation (AI Card Explainer)")
    act.triggered.connect(_generate_for_current_card)


# ==============================
# Initialization
# ==============================

def _init_menu():
    act = QAction("AI Card Explainer: generate for search results", mw)
    act.triggered.connect(_on_tools_generate_with_search)
    mw.form.menuTools.addAction(act)


def _init_shortcut():
    cfg = _get_config()
    key = (cfg_get(cfg, "05_review_shortcut", "Ctrl+Shift+L") or "Ctrl+Shift+L").strip()
    if not key:
        key = "Ctrl+Shift+L"
    sc = getattr(mw, "_ai_card_explainer_sc", None)
    if sc:
        # 設定変更後に即反映できるように更新
        try:
            sc.setKey(QKeySequence(key))
        except Exception:
            pass
        return
    sc2 = QShortcut(QKeySequence(key), mw)
    sc2.activated.connect(_generate_for_current_card)
    mw._ai_card_explainer_sc = sc2

def _open_config_gui(*args, **kwargs) -> None:
    """
    Anki: Tools -> Add-ons -> Config を押したときに呼ばれる。
    Anki 側の呼び出しシグネチャ差を吸収するため *args/**kwargs にしている。
    """
    try:
        from .config_gui import open_config_gui
        parent = None
        if args and isinstance(args[0], QWidget):
            parent = args[0]
        parent = kwargs.get("parent", parent) or mw
        open_config_gui(__name__, parent=parent, on_apply=_init_shortcut)
    except Exception as e:
        showWarning(f"Failed to open settings dialog:\n{e}")
        traceback.print_exc()

def _on_profile_loaded():
    if getattr(mw, "_ai_card_explainer_inited", False):
        return
    mw._ai_card_explainer_inited = True

    _init_menu()
    gui_hooks.reviewer_will_show_context_menu.append(_on_reviewer_context_menu)
    _init_shortcut()
    try:
        mw.addonManager.setConfigAction(__name__, _open_config_gui)
    except Exception:
        # 古いAnki等で未対応でも落とさない
        pass


gui_hooks.profile_did_open.append(_on_profile_loaded)
