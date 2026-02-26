#!/usr/bin/env python3
"""
Message Event API - Exposes message tracker via FastAPI endpoints

Provides:
1. GET /api/messages - Get all messages
2. GET /api/messages/correlation/{id} - Get messages for correlation
3. GET /api/messages/patient/{id} - Get messages for patient
4. GET /api/messages/recent - Get recent messages
5. GET /api/statistics - Get message statistics
6. GET /api/timeline - Get operation timeline
7. POST /api/clear - Clear messages
"""

from fastapi import APIRouter
from typing import Optional, Dict, Any, List
from message_tracker import get_tracker, MessageSource, MessageType


# Create router
message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.get("/")
async def get_all_messages() -> Dict[str, Any]:
    """Get all tracked messages"""
    tracker = get_tracker()
    return {
        "count": len(tracker.messages),
        "messages": tracker.get_all_messages(),
    }


@message_router.get("/correlation/{correlation_id}")
async def get_messages_by_correlation(correlation_id: str) -> Dict[str, Any]:
    """Get all messages for a specific correlation ID"""
    tracker = get_tracker()
    messages = tracker.get_messages_for_correlation(correlation_id)
    return {
        "correlation_id": correlation_id,
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/source/{source}")
async def get_messages_by_source(source: str) -> Dict[str, Any]:
    """Get all messages from a specific source"""
    tracker = get_tracker()
    messages = tracker.get_messages_by_source(source)
    return {
        "source": source,
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/type/{message_type}")
async def get_messages_by_type(message_type: str) -> Dict[str, Any]:
    """Get all messages of a specific type"""
    tracker = get_tracker()
    messages = tracker.get_messages_by_type(message_type)
    return {
        "message_type": message_type,
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/patient/{patient_id}")
async def get_messages_by_patient(patient_id: str) -> Dict[str, Any]:
    """Get all messages related to a specific patient"""
    tracker = get_tracker()
    messages = tracker.get_messages_for_patient(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/recent")
async def get_recent_messages(count: int = 50) -> Dict[str, Any]:
    """Get the most recent N messages"""
    tracker = get_tracker()
    # Limit count to reasonable maximum
    count = min(count, 1000)
    messages = tracker.get_recent_messages(count)
    return {
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/since/{timestamp_ms}")
async def get_messages_since(timestamp_ms: int) -> Dict[str, Any]:
    """Get all messages since a specific timestamp"""
    tracker = get_tracker()
    messages = tracker.get_messages_since(timestamp_ms)
    return {
        "since_timestamp": timestamp_ms,
        "count": len(messages),
        "messages": messages,
    }


@message_router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get statistics about tracked messages"""
    tracker = get_tracker()
    stats = tracker.get_statistics()
    return {
        "status": "success",
        "statistics": stats,
    }


@message_router.get("/timeline")
async def get_timeline(correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Get operation timeline"""
    tracker = get_tracker()
    timeline = tracker.get_operation_timeline(correlation_id)
    return {
        "status": "success",
        "timeline": timeline,
    }


@message_router.post("/clear")
async def clear_messages() -> Dict[str, Any]:
    """Clear all tracked messages"""
    tracker = get_tracker()
    tracker.clear_messages()
    return {
        "status": "success",
        "message": "All messages cleared",
    }


# Separate router for statistics endpoint
stats_router = APIRouter(prefix="/api", tags=["statistics"])


@stats_router.get("/stats")
async def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    tracker = get_tracker()
    return {
        "statistics": tracker.get_statistics(),
    }
