from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class UserPreferences:
    def __init__(self, storage_path: Path) -> None:
        self._path = storage_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                raw = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._data = {str(k): dict(v) for k, v in raw.items()}
            except json.JSONDecodeError:
                # 파일이 손상된 경우 초기화
                self._data = {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_speaker(self, user_id: int, speaker: str) -> None:
        key = str(user_id)
        prefs = self._data.get(key, {})
        prefs["speaker"] = speaker
        self._data[key] = prefs
        self._save()

    def clear_speaker(self, user_id: int) -> None:
        key = str(user_id)
        prefs = self._data.get(key)
        if prefs and "speaker" in prefs:
            prefs.pop("speaker")
            if prefs:
                self._data[key] = prefs
            else:
                self._data.pop(key, None)
            self._save()

    def get_speaker(self, user_id: int) -> Optional[str]:
        prefs = self._data.get(str(user_id))
        if prefs:
            speaker = prefs.get("speaker")
            if speaker:
                return speaker
        return None
