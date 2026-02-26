#!/usr/bin/env python3
"""
Message Tracker System - Event-based message logging for UI transparency

Tracks all system events with:
- Unique IDs for each message
- Correlation IDs to link related operations
- Timestamps (millisecond precision)
- Processing durations
- Network latency
- Message sizes
- Sources (client, server, websocket, ollama)

This provides complete visibility into:
1. User Input (LEFT PANE)
2. Server Processing (CENTER PANE)
3. WebSocket Communication (RIGHT PANE)
"""

import time
import json
import uuid
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class MessageSource(Enum):
    """Where the message originates from"""
    USER_INPUT = "user_input"
    SERVER_PROCESS = "server_process"
    WEBSOCKET_SEND = "websocket_send"
    WEBSOCKET_RECEIVE = "websocket_receive"
    STREAM_TOKEN = "stream_token"
    ERROR = "error"
    CHROMA_DB = "chroma_db"
    OLLAMA = "ollama"
    CSV_OPERATION = "csv_operation"


class MessageType(Enum):
    """Type of message"""
    USER_SEARCH = "user_search"
    USER_SELECT = "user_select"
    USER_ACTION = "user_action"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_PROGRESS = "tool_call_progress"
    TOOL_CALL_COMPLETE = "tool_call_complete"
    CHROMA_SEARCH = "chroma_search"
    OLLAMA_START = "ollama_start"
    OLLAMA_TOKEN = "ollama_token"
    OLLAMA_COMPLETE = "ollama_complete"
    CSV_READ = "csv_read"
    CSV_WRITE = "csv_write"
    WEBSOCKET_SEND = "websocket_send"
    WEBSOCKET_RECEIVE = "websocket_receive"
    CONNECTION = "connection"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Message:
    """Core message structure for all system events"""
    
    # Identification
    id: str  # Unique message ID (UUID)
    correlation_id: str  # Links related messages together
    
    # Classification
    source: str  # Where this message came from
    message_type: str  # Type of message
    
    # Timing
    timestamp: int  # Unix timestamp in milliseconds
    duration: Optional[int] = None  # How long operation took (ms)
    latency: Optional[int] = None  # Network latency (ms)
    
    # Content
    content: Any = None  # The actual data/payload
    
    # Metadata
    tool_name: Optional[str] = None  # Which tool was called
    patient_id: Optional[str] = None  # Which patient
    message_size: Optional[int] = None  # Size in bytes
    status: Optional[str] = None  # Status of operation (success, error, in-progress)
    
    # Additional context
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enums to strings if needed
        for key in ['source', 'message_type', 'status']:
            if isinstance(data.get(key), Enum):
                data[key] = data[key].value
        return data
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class MessageTracker:
    """
    Central message tracking system
    
    Captures all system events and makes them available for UI consumption
    """
    
    def __init__(self, max_messages: int = 10000):
        self.messages: List[Message] = []
        self.max_messages = max_messages
        self.current_correlation_id: Optional[str] = None
        self.active_operations: Dict[str, float] = {}  # Track start times
    
    def set_correlation_id(self, correlation_id: str):
        """Set the current correlation ID for linking related messages"""
        self.current_correlation_id = correlation_id
    
    def new_correlation_id(self) -> str:
        """Generate and set a new correlation ID"""
        self.current_correlation_id = str(uuid.uuid4())
        return self.current_correlation_id
    
    def get_correlation_id(self) -> str:
        """Get current correlation ID"""
        if not self.current_correlation_id:
            self.new_correlation_id()
        return self.current_correlation_id
    
    def _get_timestamp_ms(self) -> int:
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)
    
    def _get_message_size(self, obj: Any) -> int:
        """Calculate size of object in bytes"""
        try:
            return len(json.dumps(obj).encode('utf-8'))
        except:
            return 0
    
    def log_message(
        self,
        source: MessageSource,
        message_type: MessageType,
        content: Any = None,
        tool_name: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: str = "success",
        duration: Optional[int] = None,
        latency: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Log a new message
        
        Args:
            source: Where the message comes from
            message_type: Type of message
            content: Message content/payload
            tool_name: MCP tool being called (if applicable)
            patient_id: Patient ID (if applicable)
            status: Operation status (success, error, in-progress)
            duration: How long operation took (ms)
            latency: Network latency (ms)
            metadata: Additional context
        
        Returns:
            The created message
        """
        message = Message(
            id=str(uuid.uuid4()),
            correlation_id=self.get_correlation_id(),
            source=source.value,
            message_type=message_type.value,
            timestamp=self._get_timestamp_ms(),
            content=content,
            tool_name=tool_name,
            patient_id=patient_id,
            message_size=self._get_message_size(content),
            status=status,
            duration=duration,
            latency=latency,
            metadata=metadata or {},
        )
        
        # Add to tracker
        self.messages.append(message)
        
        # Trim old messages if needed
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        return message
    
    def start_operation(self, operation_id: str):
        """Mark the start of an operation for duration tracking"""
        self.active_operations[operation_id] = time.time()
    
    def end_operation(self, operation_id: str) -> Optional[int]:
        """
        Mark the end of an operation and get duration in ms
        
        Returns:
            Duration in milliseconds, or None if operation wasn't tracked
        """
        if operation_id not in self.active_operations:
            return None
        
        start = self.active_operations.pop(operation_id)
        duration_ms = int((time.time() - start) * 1000)
        return duration_ms
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages as list of dicts"""
        return [msg.to_dict() for msg in self.messages]
    
    def get_messages_for_correlation(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific correlation ID"""
        return [
            msg.to_dict()
            for msg in self.messages
            if msg.correlation_id == correlation_id
        ]
    
    def get_messages_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get all messages from a specific source"""
        return [
            msg.to_dict()
            for msg in self.messages
            if msg.source == source
        ]
    
    def get_messages_by_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """Get all messages of a specific type"""
        return [
            msg.to_dict()
            for msg in self.messages
            if msg.message_type == msg_type
        ]
    
    def get_messages_for_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all messages related to a specific patient"""
        return [
            msg.to_dict()
            for msg in self.messages
            if msg.patient_id == patient_id
        ]
    
    def get_messages_since(self, timestamp_ms: int) -> List[Dict[str, Any]]:
        """Get all messages since a specific timestamp"""
        return [
            msg.to_dict()
            for msg in self.messages
            if msg.timestamp >= timestamp_ms
        ]
    
    def get_recent_messages(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get the most recent N messages"""
        return [msg.to_dict() for msg in self.messages[-count:]]
    
    def clear_messages(self):
        """Clear all messages (for starting fresh)"""
        self.messages = []
        self.current_correlation_id = None
        self.active_operations = {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about tracked messages"""
        if not self.messages:
            return {
                "total_messages": 0,
                "total_sources": 0,
                "total_types": 0,
                "time_span_ms": 0,
            }
        
        sources = set(msg.source for msg in self.messages)
        types = set(msg.message_type for msg in self.messages)
        
        time_span = (
            self.messages[-1].timestamp - self.messages[0].timestamp
            if len(self.messages) > 1
            else 0
        )
        
        total_data = sum(msg.message_size or 0 for msg in self.messages)
        
        avg_latency = None
        latencies = [msg.latency for msg in self.messages if msg.latency]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
        
        return {
            "total_messages": len(self.messages),
            "unique_sources": len(sources),
            "sources": list(sources),
            "unique_types": len(types),
            "types": list(types),
            "time_span_ms": time_span,
            "total_data_bytes": total_data,
            "average_latency_ms": avg_latency,
            "first_message_ts": self.messages[0].timestamp if self.messages else None,
            "last_message_ts": self.messages[-1].timestamp if self.messages else None,
        }
    
    def get_operation_timeline(self, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a timeline view of operations
        
        Shows the sequence and timing of operations
        """
        messages = (
            self.get_messages_for_correlation(correlation_id)
            if correlation_id
            else self.get_all_messages()
        )
        
        timeline = {
            "correlation_id": correlation_id,
            "message_count": len(messages),
            "timeline": [],
        }
        
        if not messages:
            return timeline
        
        start_ts = messages[0]["timestamp"]
        total_duration = messages[-1]["timestamp"] - start_ts
        
        for msg in messages:
            relative_ts = msg["timestamp"] - start_ts
            progress = (relative_ts / total_duration * 100) if total_duration > 0 else 0
            
            timeline["timeline"].append({
                "time_ms": relative_ts,
                "progress_percent": progress,
                "source": msg["source"],
                "type": msg["message_type"],
                "status": msg.get("status", ""),
                "content_preview": str(msg.get("content", ""))[:100],
            })
        
        timeline["total_duration_ms"] = total_duration
        return timeline


# Global instance
_tracker = MessageTracker()


def get_tracker() -> MessageTracker:
    """Get the global message tracker instance"""
    return _tracker
