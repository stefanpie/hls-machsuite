from dataclasses import dataclass, field
from typing import Any

import llm
import requests
from pydantic import Field


@dataclass
class ModelWithSettings:
    model: llm.Model
    settings: dict[str, Any] = field(default_factory=dict)


class TAITimeout(Exception): ...


class TogetherAI(llm.Model):
    needs_key = "togetherai"
    key_env_var = "TOGETHER_API_KEY"

    class Options(llm.Options):
        max_tokens: int | None = Field(
            ge=1,
            default=None,
        )
        stop: list[str] | None = Field(
            default=["[/INST]", "</s>"],
        )
        temperature: float | None = Field(
            ge=0,
            default=None,
        )
        top_p: float | None = Field(
            ge=0,
            default=None,
        )
        top_k: int | None = Field(
            ge=0,
            default=None,
        )
        repetition_penalty: float | None = Field(
            ge=0,
            default=None,
        )
        json_schema_output: dict[str, Any] | None = Field(
            default=None,
        )

    API_URL_INFERENCE = "https://api.together.xyz/v1/chat/completions"

    def __init__(self, model_id, model_id_tai):
        self.model_id = model_id
        self.model_id_tai = model_id_tai

    def execute(self, prompt, stream, response, conversation):
        payload = {
            "model": self.model_id_tai,
        }

        payload["messages"] = []
        if prompt.system:
            payload["messages"].append({"role": "system", "content": prompt.system})

        if conversation:
            for response in conversation.responses:
                payload["messages"].append(
                    {"role": "user", "content": response.prompt.prompt}
                )
                payload["messages"].append(
                    {"role": "assistant", "content": response.text()}
                )

        payload["messages"].append({"role": "user", "content": prompt.prompt})

        if prompt.options.json_schema_output:
            payload["response_format"] = {}
            payload["response_format"]["type"] = "json_object"
            payload["response_format"]["schema"] = prompt.options.json_schema_output

        payload["stop"] = prompt.options.stop
        # payload["max_tokens"] = -1
        if prompt.options.max_tokens:
            payload["max_tokens"] = prompt.options.max_tokens

        if prompt.options.temperature:
            payload["temperature"] = prompt.options.temperature

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.key}",
        }

        r = requests.post(self.API_URL_INFERENCE, json=payload, headers=headers)
        if r.status_code == 524:
            raise TAITimeout("Model took too long to respond on TogetherAI's side")
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            print(r.text)
            raise e
        data = r.json()

        assert data["choices"]
        assert len(data["choices"]) > 0
        first_choice = data["choices"][0]
        assert first_choice["message"]
        assert first_choice["message"]["role"] == "assistant"
        assert first_choice["message"]["content"]

        return first_choice["message"]["content"]


def LLM_TAI_MIXTRAL_8X22B_INSTRUCT(
    api_key: str,
    settings: dict[str, Any] = {
        "stop": ["</s>", "[/INST]"],
        "max_tokens": None,
    },
) -> ModelWithSettings:
    model = TogetherAI(
        "mixtral-8x22b-instruct", "mistralai/Mixtral-8x22B-Instruct-v0.1"
    )
    model.key = api_key
    return ModelWithSettings(model, settings)


def LLM_LLAMA_3_70B_CHAT_HF(
    api_key: str,
    settings: dict[str, Any] = {
        "stop": ["<|eot_id|>"],
    },
) -> ModelWithSettings:
    model = TogetherAI("llama-3-70b-chat-hf", "meta-llama/Llama-3-70b-chat-hf")
    model.key = api_key
    return ModelWithSettings(model, settings)
