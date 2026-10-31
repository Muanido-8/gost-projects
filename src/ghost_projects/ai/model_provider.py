# from openai import AsyncOpenAI
# from agents import OpenAIChatCompletionsModel
# from ghost_projects.config.settings import settings

# def get_model_provider():
#     """
#     Configures and returns the AI model provider using the project settings.
    
#     Returns:
#         An OpenAIChatCompletionsModel instance configured for Ollama Cloud.
#     """
#     # Use the existing settings for Ollama Cloud configuration
#     client = AsyncOpenAI(
#         base_url=settings.ollama_base_url,
#         api_key=settings.ollama_api_key.get_secret_value(),
#     )
    
#     return OpenAIChatCompletionsModel(
#         settings.model_name,
#         client,
#     )



import json
import logging
import os

import httpx
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, OpenAIResponsesModel

from ghost_projects.config.settings import settings

logger = logging.getLogger(__name__)


async def _debug_ollama_response(response: httpx.Response) -> None:
    """Print the raw model response without consuming it permanently."""
    await response.aread()

    try:
        payload = response.json()
    except ValueError:
        print("\n[OLLAMA RAW HTTP BODY]")
        print(response.text[:20000])
        return

    print("\n" + "=" * 80)
    print("[OLLAMA RAW MODEL RESPONSE]")
    print("HTTP status:", response.status_code)

    choices = payload.get("choices", [])

    if not choices:
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:20000])

    for index, choice in enumerate(choices):
        message = choice.get("message", {})

        print(f"\nChoice {index}")
        print("Finish reason:", choice.get("finish_reason"))
        print("Content (raw):")
        print(repr(message.get("content")))

        tool_calls = message.get("tool_calls")
        if tool_calls:
            print("Tool calls (raw):")
            print(json.dumps(
                tool_calls,
                ensure_ascii=False,
                indent=2,
            ))

    print("=" * 80 + "\n")


def get_model_provider():
    debug = os.getenv("DEBUG_OLLAMA_RAW", "0") == "1"

    kwargs = {}

    if debug:
        kwargs["http_client"] = httpx.AsyncClient(
            event_hooks={
                "response": [_debug_ollama_response]
            }
        )

    client = AsyncOpenAI(
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key.get_secret_value(),
        **kwargs,
    )

    # return OpenAIChatCompletionsModel(
    #     settings.model_name,
    #     client,
    # )

    return OpenAIResponsesModel(
        model=settings.model_name,
        openai_client=client,
    )
