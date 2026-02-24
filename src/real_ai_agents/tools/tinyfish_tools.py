"""
TinyFish Web Agent Tools for Research Crew.

API Reference: https://docs.tinyfish.ai/
Base URL: https://agent.tinyfish.ai/v1/automation
Auth: X-API-Key header using TINYFISH_API_KEY env var
"""

import os
import json
import requests
from typing import Type, Any, Dict, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


TINYFISH_BASE_URL = "https://agent.tinyfish.ai/v1/automation"


class TinyFishExtractorInput(BaseModel):
    """Input schema for TinyFish Web Agent Extractor Tool."""

    url: str = Field(
        ...,
        description="The URL of the web page to extract data from."
    )
    goal: str = Field(
        ...,
        description=(
            "Natural language instruction describing what data to extract "
            "and how to return it. Example: 'Extract all property listings "
            "with title, price, address, phone number, and image URLs. "
            "Return as JSON.'"
        )
    )
    use_stealth: bool = Field(
        default=False,
        description=(
            "Set to True for bot-protected sites (Cloudflare, DataDome). "
            "Uses a stealth browser profile with anti-detection measures."
        )
    )
    proxy_country: Optional[str] = Field(
        default=None,
        description=(
            "ISO country code for geo-proxy routing. "
            "Supported: US, GB, CA, DE, FR, JP, AU."
        )
    )


class TinyFishExtractorTool(BaseTool):
    name: str = "TinyFish Web Extractor"
    description: str = (
        "Extract structured data from any web page using an AI-powered browser agent. "
        "Provide a URL and a natural language goal describing what to extract. "
        "Handles JavaScript rendering, bot protection (stealth mode), and geo-proxies. "
        "Returns structured JSON data extracted from the page."
    )
    args_schema: Type[BaseModel] = TinyFishExtractorInput

    def _run(
        self,
        url: str,
        goal: str,
        use_stealth: bool = False,
        proxy_country: Optional[str] = None,
    ) -> str:
        api_key = os.getenv("TINYFISH_API_KEY")
        if not api_key:
            return json.dumps({
                "success": False,
                "error": "TINYFISH_API_KEY environment variable is not set"
            })

        body: Dict[str, Any] = {"url": url, "goal": goal}

        if use_stealth:
            body["browser_profile"] = "stealth"

        if proxy_country:
            body["proxy_config"] = {
                "enabled": True,
                "country_code": proxy_country.upper(),
            }

        try:
            response = requests.post(
                f"{TINYFISH_BASE_URL}/run",
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            status = data.get("status", "")

            if status == "COMPLETED":
                result = data.get("result")
                if result is not None:
                    return json.dumps({"success": True, "data": result, "url": url})
                return json.dumps({
                    "success": False,
                    "error": "Run completed but no result data returned",
                    "url": url,
                })

            if status == "FAILED":
                error_info = data.get("error", {})
                error_message = (
                    error_info.get("message", "Unknown error")
                    if isinstance(error_info, dict)
                    else str(error_info)
                )
                return json.dumps({
                    "success": False,
                    "error": f"TinyFish run failed: {error_message}",
                    "url": url,
                })

            return json.dumps({
                "success": False,
                "error": f"Unexpected run status: {status}",
                "url": url,
            })

        except requests.exceptions.RequestException as e:
            return json.dumps({
                "success": False,
                "error": f"TinyFish API request failed: {str(e)}",
                "url": url,
            })
