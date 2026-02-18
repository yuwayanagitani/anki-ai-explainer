# config_gui.py
from __future__ import annotations

from typing import Any, Dict, Optional, Callable

from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip, showWarning


AddonConfig = Dict[str, Any]

DEFAULT_CONFIG: AddonConfig = {
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
    "05_review_shortcut": "Ctrl+Shift+L",
}


def _merged_config(addon_id: str) -> AddonConfig:
    cfg = mw.addonManager.getConfig(addon_id) or {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    return merged


class ExplainerConfigDialog(QDialog):
    def __init__(
        self,
        addon_id: str,
        parent: Optional[QWidget] = None,
        on_apply: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent or mw)
        self.addon_id = addon_id
        self.on_apply = on_apply

        self.setWindowTitle("AI Card Explainer — Settings")
        self.setMinimumWidth(720)

        self.cfg = _merged_config(addon_id)

        self._build_ui()
        self._load_to_ui(self.cfg)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)

        # --- Tab: Provider ---
        tab_provider = QWidget(self)
        self.tabs.addTab(tab_provider, "Provider")
        lay_p = QVBoxLayout(tab_provider)

        form_p = QFormLayout()
        lay_p.addLayout(form_p)

        self.provider = QComboBox()
        self.provider.addItem("OpenAI", "openai")
        self.provider.addItem("Gemini", "gemini")
        form_p.addRow("Provider", self.provider)

        # OpenAI
        openai_box = QGroupBox("OpenAI")
        lay_p.addWidget(openai_box)
        openai_form = QFormLayout(openai_box)

        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("If empty: use env OPENAI_API_KEY")
        self.openai_key.setMinimumWidth(520)

        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("e.g. gpt-4o-mini")
        self.openai_model.setMinimumWidth(520)

        openai_form.addRow("API key", self.openai_key)
        openai_form.addRow("Model", self.openai_model)

        # Gemini
        gemini_box = QGroupBox("Gemini")
        lay_p.addWidget(gemini_box)
        gemini_form = QFormLayout(gemini_box)

        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key.setPlaceholderText("If empty: use env GEMINI_API_KEY")
        self.gemini_key.setMinimumWidth(520)

        self.gemini_model = QLineEdit()
        self.gemini_model.setPlaceholderText("e.g. gemini-2.5-flash-lite")
        self.gemini_model.setMinimumWidth(520)

        gemini_form.addRow("API key", self.gemini_key)
        gemini_form.addRow("Model", self.gemini_model)

        # --- Tab: Fields ---
        tab_fields = QWidget(self)
        self.tabs.addTab(tab_fields, "Fields")
        lay_fields = QVBoxLayout(tab_fields)

        # Input fields section
        input_label = QLabel("Input fields (read in order, concatenated as {{fields}} placeholder):")
        lay_fields.addWidget(input_label)

        fields_hbox = QHBoxLayout()
        
        self.input_fields_list = QListWidget()
        self.input_fields_list.setMinimumHeight(150)
        fields_hbox.addWidget(self.input_fields_list)

        # Buttons for managing input fields
        fields_buttons = QVBoxLayout()
        self.add_field_btn = QPushButton("Add")
        self.remove_field_btn = QPushButton("Remove")
        self.move_up_btn = QPushButton("Up")
        self.move_down_btn = QPushButton("Down")
        
        fields_buttons.addWidget(self.add_field_btn)
        fields_buttons.addWidget(self.remove_field_btn)
        fields_buttons.addWidget(self.move_up_btn)
        fields_buttons.addWidget(self.move_down_btn)
        fields_buttons.addStretch()
        
        fields_hbox.addLayout(fields_buttons)
        lay_fields.addLayout(fields_hbox)

        # Explanation field
        form_e = QFormLayout()
        self.e_field = QLineEdit()
        self.e_field.setMinimumWidth(520)
        form_e.addRow("Explanation field (output)", self.e_field)
        lay_fields.addLayout(form_e)

        # Connect field buttons
        self.add_field_btn.clicked.connect(self._on_add_field)
        self.remove_field_btn.clicked.connect(self._on_remove_field)
        self.move_up_btn.clicked.connect(self._on_move_up)
        self.move_down_btn.clicked.connect(self._on_move_down)

        # --- Tab: Prompt ---
        tab_prompt = QWidget(self)
        self.tabs.addTab(tab_prompt, "Prompt")
        lay_prompt = QVBoxLayout(tab_prompt)

        prompt_label = QLabel(
            "User prompt (use {{fields}} placeholder for field contents):"
        )
        lay_prompt.addWidget(prompt_label)

        self.user_prompt = QTextEdit()
        self.user_prompt.setMinimumHeight(200)
        self.user_prompt.setPlaceholderText(
            "Enter your custom prompt here. Use {{fields}} to insert the concatenated field contents."
        )
        lay_prompt.addWidget(self.user_prompt)

        note_label = QLabel(
            "Note: The add-on enforces HTML-only output. No need to specify that in your prompt."
        )
        note_label.setStyleSheet("color: gray; font-style: italic;")
        lay_prompt.addWidget(note_label)

        # --- Tab: Behavior ---
        tab_b = QWidget(self)
        self.tabs.addTab(tab_b, "Behavior")
        lay_b = QVBoxLayout(tab_b)

        form_b = QFormLayout()
        lay_b.addLayout(form_b)

        self.on_exists = QComboBox()
        self.on_exists.addItem("Skip (do nothing)", "skip")
        self.on_exists.addItem("Overwrite", "overwrite")
        self.on_exists.addItem("Append", "append")
        form_b.addRow("When explanation exists", self.on_exists)

        self.append_sep = QTextEdit()
        self.append_sep.setMinimumHeight(80)
        self.append_sep.setPlaceholderText("Separator used when Append is selected.")
        form_b.addRow("Append separator", self.append_sep)

        self.max_notes = QSpinBox()
        self.max_notes.setRange(1, 5000)
        form_b.addRow("Max notes per run", self.max_notes)

        self.shortcut = QKeySequenceEdit()
        form_b.addRow("Review shortcut", self.shortcut)

        # live UI tweaks
        self.on_exists.currentIndexChanged.connect(self._sync_append_enabled)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        root.addWidget(self.buttons)

        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)
        self.buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._on_defaults)

    def _sync_append_enabled(self) -> None:
        is_append = (self.on_exists.currentData() == "append")
        self.append_sep.setEnabled(is_append)

    def _on_add_field(self) -> None:
        text, ok = QInputDialog.getText(self, "Add Field", "Enter field name:")
        if ok and text.strip():
            field_name = text.strip()
            # Check for duplicates
            existing_fields = []
            for i in range(self.input_fields_list.count()):
                item = self.input_fields_list.item(i)
                if item:
                    existing_fields.append(item.text())
            
            if field_name in existing_fields:
                showWarning(f"Field '{field_name}' is already in the list.")
                return
            
            self.input_fields_list.addItem(field_name)

    def _on_remove_field(self) -> None:
        current_row = self.input_fields_list.currentRow()
        if current_row >= 0:
            self.input_fields_list.takeItem(current_row)

    def _on_move_up(self) -> None:
        current_row = self.input_fields_list.currentRow()
        if current_row > 0:
            item = self.input_fields_list.takeItem(current_row)
            self.input_fields_list.insertItem(current_row - 1, item)
            self.input_fields_list.setCurrentRow(current_row - 1)

    def _on_move_down(self) -> None:
        current_row = self.input_fields_list.currentRow()
        if current_row >= 0 and current_row < self.input_fields_list.count() - 1:
            item = self.input_fields_list.takeItem(current_row)
            self.input_fields_list.insertItem(current_row + 1, item)
            self.input_fields_list.setCurrentRow(current_row + 1)

    def _load_to_ui(self, cfg: AddonConfig) -> None:
        # Provider
        self._set_combo_by_data(self.provider, cfg.get("01_provider", "openai"))
        self.openai_key.setText(str(cfg.get("01_openai_api_key", "")) or "")
        self.openai_model.setText(str(cfg.get("01_openai_model", DEFAULT_CONFIG["01_openai_model"])) or "")
        self.gemini_key.setText(str(cfg.get("01_gemini_api_key", "")) or "")
        self.gemini_model.setText(str(cfg.get("01_gemini_model", DEFAULT_CONFIG["01_gemini_model"])) or "")

        # Fields
        input_fields = cfg.get("02_input_fields", DEFAULT_CONFIG["02_input_fields"])
        if not isinstance(input_fields, list):
            input_fields = ["Front", "Back"]
        self.input_fields_list.clear()
        for field in input_fields:
            self.input_fields_list.addItem(str(field))
        
        self.e_field.setText(str(cfg.get("02_explanation_field", "Explanation")) or "Explanation")

        # Prompt
        user_prompt = cfg.get("03_user_prompt", DEFAULT_CONFIG["03_user_prompt"])
        self.user_prompt.setPlainText(str(user_prompt))

        # Behavior
        self._set_combo_by_data(self.on_exists, cfg.get("04_on_existing_behavior", "skip"))
        self.append_sep.setPlainText(str(cfg.get("04_append_separator", "\n<hr>\n")))

        self.max_notes.setValue(int(cfg.get("05_max_notes_per_run", 50) or 50))

        seq = QKeySequence(str(cfg.get("05_review_shortcut", "Ctrl+Shift+L") or "Ctrl+Shift+L"))
        self.shortcut.setKeySequence(seq)

        self._sync_append_enabled()

    def _collect_from_ui(self) -> AddonConfig:
        cfg: AddonConfig = dict(self.cfg)

        cfg["01_provider"] = self.provider.currentData()

        cfg["01_openai_api_key"] = self.openai_key.text().strip()
        cfg["01_openai_model"] = self.openai_model.text().strip() or DEFAULT_CONFIG["01_openai_model"]

        cfg["01_gemini_api_key"] = self.gemini_key.text().strip()
        cfg["01_gemini_model"] = self.gemini_model.text().strip() or DEFAULT_CONFIG["01_gemini_model"]

        # Collect input fields from list
        input_fields = []
        for i in range(self.input_fields_list.count()):
            item = self.input_fields_list.item(i)
            if item:
                input_fields.append(item.text())
        cfg["02_input_fields"] = input_fields if input_fields else ["Front", "Back"]
        cfg["02_explanation_field"] = self.e_field.text().strip() or "Explanation"

        cfg["03_user_prompt"] = self.user_prompt.toPlainText()

        cfg["04_on_existing_behavior"] = self.on_exists.currentData()
        cfg["04_append_separator"] = self.append_sep.toPlainText()


        cfg["05_max_notes_per_run"] = int(self.max_notes.value())

        ks = self.shortcut.keySequence()
        cfg["05_review_shortcut"] = ks.toString() or DEFAULT_CONFIG["05_review_shortcut"]

        return cfg

    def _write_config(self, cfg: AddonConfig) -> None:
        mw.addonManager.writeConfig(self.addon_id, cfg)
        self.cfg = cfg

        if self.on_apply:
            try:
                self.on_apply()
            except Exception:
                # 反映失敗しても保存自体は成功させる
                pass

    def _on_apply(self) -> None:
        cfg = self._collect_from_ui()
        self._write_config(cfg)
        tooltip("Settings saved.")

    def _on_ok(self) -> None:
        self._on_apply()
        self.accept()

    def _on_defaults(self) -> None:
        self.cfg = dict(DEFAULT_CONFIG)
        self._load_to_ui(self.cfg)
        tooltip("Defaults loaded (not saved yet).")

    @staticmethod
    def _set_combo_by_data(cb: QComboBox, data: Any) -> None:
        for i in range(cb.count()):
            if cb.itemData(i) == data:
                cb.setCurrentIndex(i)
                return
        cb.setCurrentIndex(0)


def open_config_gui(addon_id: str, parent: Optional[QWidget] = None, on_apply: Optional[Callable[[], None]] = None) -> None:
    try:
        dlg = ExplainerConfigDialog(addon_id=addon_id, parent=parent or mw, on_apply=on_apply)
        dlg.exec()
    except Exception as e:
        showWarning(f"Failed to open settings dialog:\n{e}")
