import re
from pydantic import BaseModel


def parse_assessment(
    raw_output: str,
    model: type[BaseModel],
):
    content = raw_output.strip()

    # Remove Markdown code fences
    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(r"\s*```$", "", content)

    return model.model_validate_json(content)