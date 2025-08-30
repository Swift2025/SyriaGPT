import json
import os
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    def __init__(self):
        self.config_path = Path(__file__).parent
        self._messages = None
        self._oauth_providers = None
        self._email_templates = None

    def load_messages(self) -> Dict[str, Any]:
        if self._messages is None:
            try:
                with open(self.config_path / "messages.json", "r", encoding="utf-8") as f:
                    self._messages = json.load(f)
            except FileNotFoundError:
                print("Warning: messages.json not found, using empty dict")
                self._messages = {}
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in messages.json: {e}")
                self._messages = {}
        return self._messages

    def load_oauth_providers(self) -> Dict[str, Any]:
        if self._oauth_providers is None:
            try:
                with open(self.config_path / "oauth_providers.json", "r", encoding="utf-8") as f:
                    self._oauth_providers = json.load(f)
            except FileNotFoundError:
                print("Warning: oauth_providers.json not found, using empty dict")
                self._oauth_providers = {}
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in oauth_providers.json: {e}")
                self._oauth_providers = {}
        return self._oauth_providers

    def load_email_templates(self) -> Dict[str, Any]:
        if self._email_templates is None:
            try:
                with open(self.config_path / "email_templates.json", "r", encoding="utf-8") as f:
                    self._email_templates = json.load(f)
            except FileNotFoundError:
                print("Warning: email_templates.json not found, using empty dict")
                self._email_templates = {}
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in email_templates.json: {e}")
                self._email_templates = {}
        return self._email_templates

    def get_message(self, category: str, key: str, **kwargs) -> str:
        messages = self.load_messages()
        message = messages.get(category, {}).get(key, f"Missing message: {category}.{key}")
        if kwargs:
            try:
                return message.format(**kwargs)
            except KeyError as e:
                return f"Message formatting error: {e}"
        return message

    def get_oauth_provider_config(self, provider: str) -> Dict[str, Any]:
        providers = self.load_oauth_providers()
        return providers.get(provider, {})

    def get_email_template(self, template_name: str) -> Dict[str, Any]:
        templates = self.load_email_templates()
        return templates.get(template_name, {})


config_loader = ConfigLoader()