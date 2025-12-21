"""
Retell AI Voice Call Tools for Call Agent Crew.

These tools integrate with Retell AI's API to make outbound phone calls
for property inspections (rent/buy) and acquisition negotiations.

API Reference: https://docs.retellai.com/api-references/create-phone-call
"""

import os
import time
import json
from typing import Optional
from crewai.tools import tool

# Retell AI SDK - install with: pip install retell-sdk
try:
    from retell import Retell
except ImportError:
    Retell = None


# Environment variables
RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_FROM_NUMBER = os.getenv("RETELL_FROM_NUMBER")  # Your Retell-purchased number
RETELL_INSPECTOR_AGENT_ID = os.getenv("RETELL_INSPECTOR_AGENT_ID")
RETELL_NEGOTIATOR_AGENT_ID = os.getenv("RETELL_NEGOTIATOR_AGENT_ID")


def _get_retell_client():
    """Get Retell client instance."""
    if Retell is None:
        raise ImportError("retell-sdk not installed. Run: pip install retell-sdk")
    if not RETELL_API_KEY:
        raise ValueError("RETELL_API_KEY environment variable not set")
    return Retell(api_key=RETELL_API_KEY)


@tool("Make Inspection Call")
def make_inspection_call(
    to_number: str,
    property_id: str,
    property_address: str,
    property_price: str,
    user_questions: str,
    contact_name: Optional[str] = None
) -> str:
    """
    Make an outbound phone call to a property agent for booking an inspection.
    
    Use this tool when you need to contact a property listing agent to:
    - Schedule a property viewing/inspection
    - Ask user-defined questions about the property
    - Gather additional property information
    
    Args:
        to_number: Phone number to call in E.164 format (e.g., +15125550123)
        property_id: Unique identifier for the property
        property_address: Full address of the property
        property_price: Listed price or rent amount
        user_questions: Comma-separated list of questions to ask
        contact_name: Name of the contact person (optional)
    
    Returns:
        JSON string with call_id and initial status for tracking
    """
    try:
        client = _get_retell_client()
        
        if not RETELL_FROM_NUMBER:
            return json.dumps({
                "success": False,
                "error": "RETELL_FROM_NUMBER environment variable not set"
            })
        
        if not RETELL_INSPECTOR_AGENT_ID:
            return json.dumps({
                "success": False,
                "error": "RETELL_INSPECTOR_AGENT_ID environment variable not set"
            })
        
        # Create the phone call with dynamic variables for the Retell agent
        call_response = client.call.create_phone_call(
            from_number=RETELL_FROM_NUMBER,
            to_number=to_number,
            override_agent_id=RETELL_INSPECTOR_AGENT_ID,
            retell_llm_dynamic_variables={
                "property_address": property_address,
                "property_price": property_price,
                "user_questions": user_questions,
                "contact_name": contact_name or "the property agent",
                "call_purpose": "schedule_inspection"
            },
            metadata={
                "property_id": property_id,
                "call_type": "inspection",
                "flow_phase": "engagement"
            }
        )
        
        return json.dumps({
            "success": True,
            "call_id": call_response.call_id,
            "call_status": call_response.call_status,
            "property_id": property_id,
            "to_number": to_number,
            "message": "Inspection call initiated successfully"
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "property_id": property_id,
            "to_number": to_number
        })


@tool("Make Negotiation Call")
def make_negotiation_call(
    to_number: str,
    property_id: str,
    property_address: str,
    estimated_value: str,
    investor_budget: str,
    contact_name: Optional[str] = None
) -> str:
    """
    Make an outbound phone call to a property owner for acquisition negotiation.
    
    Use this tool when you need to contact a property owner to:
    - Gauge their interest in selling the property
    - Discuss preliminary acquisition terms
    - Establish rapport for potential deals
    
    Args:
        to_number: Phone number to call in E.164 format (e.g., +15125550123)
        property_id: Unique identifier for the property
        property_address: Full address of the property
        estimated_value: Estimated market value of the property
        investor_budget: Budget range the investor is willing to pay
        contact_name: Name of the property owner (optional)
    
    Returns:
        JSON string with call_id and initial status for tracking
    """
    try:
        client = _get_retell_client()
        
        if not RETELL_FROM_NUMBER:
            return json.dumps({
                "success": False,
                "error": "RETELL_FROM_NUMBER environment variable not set"
            })
        
        if not RETELL_NEGOTIATOR_AGENT_ID:
            return json.dumps({
                "success": False,
                "error": "RETELL_NEGOTIATOR_AGENT_ID environment variable not set"
            })
        
        # Create the phone call with dynamic variables for the Retell agent
        call_response = client.call.create_phone_call(
            from_number=RETELL_FROM_NUMBER,
            to_number=to_number,
            override_agent_id=RETELL_NEGOTIATOR_AGENT_ID,
            retell_llm_dynamic_variables={
                "property_address": property_address,
                "estimated_value": estimated_value,
                "investor_budget": investor_budget,
                "contact_name": contact_name or "the property owner",
                "call_purpose": "acquisition_negotiation"
            },
            metadata={
                "property_id": property_id,
                "call_type": "negotiation",
                "flow_phase": "engagement"
            }
        )
        
        return json.dumps({
            "success": True,
            "call_id": call_response.call_id,
            "call_status": call_response.call_status,
            "property_id": property_id,
            "to_number": to_number,
            "message": "Negotiation call initiated successfully"
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "property_id": property_id,
            "to_number": to_number
        })


@tool("Get Call Result")
def get_call_result(call_id: str, max_wait_seconds: int = 300) -> str:
    """
    Retrieve the result of a completed Retell AI call including transcript.
    
    Use this tool after initiating a call to get:
    - Full conversation transcript with timestamps
    - Call duration and status
    - Recording URL (if available)
    - Any collected data from the call
    
    Args:
        call_id: The call_id returned from make_inspection_call or make_negotiation_call
        max_wait_seconds: Maximum time to wait for call completion (default 300s/5min)
    
    Returns:
        JSON string with call transcript, duration, status, and metadata
    """
    try:
        client = _get_retell_client()
        
        # Poll for call completion
        start_time = time.time()
        poll_interval = 5  # seconds
        
        while True:
            call_data = client.call.retrieve(call_id)
            
            # Check if call has ended
            if call_data.call_status in ["ended", "error", "failed"]:
                break
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= max_wait_seconds:
                return json.dumps({
                    "success": False,
                    "call_id": call_id,
                    "error": f"Timeout waiting for call completion after {max_wait_seconds}s",
                    "last_status": call_data.call_status
                })
            
            time.sleep(poll_interval)
        
        # Format transcript from utterances
        transcript_lines = []
        if hasattr(call_data, 'transcript') and call_data.transcript:
            for utterance in call_data.transcript:
                speaker = utterance.get('role', 'unknown')
                content = utterance.get('content', '')
                timestamp = utterance.get('timestamp', 0)
                minutes = int(timestamp // 60000)
                seconds = int((timestamp % 60000) // 1000)
                transcript_lines.append(f"[{minutes:02d}:{seconds:02d}] {speaker}: {content}")
        
        transcript_text = "\n".join(transcript_lines) if transcript_lines else None
        
        # Calculate duration
        duration_seconds = None
        if hasattr(call_data, 'start_timestamp') and hasattr(call_data, 'end_timestamp'):
            if call_data.start_timestamp and call_data.end_timestamp:
                duration_seconds = (call_data.end_timestamp - call_data.start_timestamp) // 1000
        
        return json.dumps({
            "success": True,
            "call_id": call_id,
            "call_status": call_data.call_status,
            "duration_seconds": duration_seconds,
            "transcript": transcript_text,
            "recording_url": getattr(call_data, 'recording_url', None),
            "metadata": getattr(call_data, 'metadata', {}),
            "collected_variables": getattr(call_data, 'collected_dynamic_variables', {}),
            "disconnection_reason": getattr(call_data, 'disconnection_reason', None)
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "call_id": call_id,
            "error": str(e)
        })


@tool("Check Call Status")
def check_call_status(call_id: str) -> str:
    """
    Check the current status of a Retell AI call without waiting.
    
    Use this tool to quickly check if a call is still in progress,
    has completed, or has failed.
    
    Args:
        call_id: The call_id to check status for
    
    Returns:
        JSON string with current call status
    """
    try:
        client = _get_retell_client()
        call_data = client.call.retrieve(call_id)
        
        return json.dumps({
            "success": True,
            "call_id": call_id,
            "call_status": call_data.call_status,
            "in_progress": call_data.call_status in ["registered", "ongoing"],
            "completed": call_data.call_status == "ended",
            "failed": call_data.call_status in ["error", "failed"]
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "call_id": call_id,
            "error": str(e)
        })
