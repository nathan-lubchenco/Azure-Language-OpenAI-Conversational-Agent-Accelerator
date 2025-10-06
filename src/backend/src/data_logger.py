# HACKDAY: Data logger for flat file storage
import json
import os
from datetime import datetime
from pathlib import Path

# Create logs directory
LOG_DIR = Path("./hackday_logs")
LOG_DIR.mkdir(exist_ok=True)

def log_event(event_type, data):
    """
    Log an event to JSONL file (one JSON object per line)

    Args:
        event_type: Type of event (e.g., "utterance_extraction", "chat_completion")
        data: Dictionary of data to log
    """
    log_file = LOG_DIR / f"conversations_{datetime.now().strftime('%Y%m%d')}.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        **data
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"📝 Logged {event_type} to {log_file}")
    return entry


def log_utterance_extraction(original_message, extracted_utterances, model):
    """Log utterance extraction event"""
    return log_event("utterance_extraction", {
        "original_message": original_message,
        "extracted_utterances": extracted_utterances,
        "utterance_count": len(extracted_utterances) if isinstance(extracted_utterances, list) else 1,
        "model": model
    })


def log_orchestration(message, route, result, router_type):
    """Log orchestration routing event"""
    return log_event("orchestration", {
        "message": message,
        "route": route,
        "router_type": router_type,
        "result_preview": str(result)[:200] if result else None  # First 200 chars
    })


def log_chat_completion(original_message, utterances, responses, model, router_type):
    """Log complete chat interaction"""
    return log_event("chat_completion", {
        "original_message": original_message,
        "utterances": utterances,
        "responses": responses,
        "utterance_count": len(utterances) if isinstance(utterances, list) else 1,
        "response_count": len(responses),
        "model": model,
        "router_type": router_type
    })


def log_error(error_type, error_message, context=None):
    """Log error events"""
    return log_event("error", {
        "error_type": error_type,
        "error_message": str(error_message),
        "context": context
    })


def get_log_files():
    """List all log files"""
    return sorted(LOG_DIR.glob("*.jsonl"))


def get_log_stats():
    """Get statistics about logged data"""
    stats = {
        "total_files": 0,
        "total_events": 0,
        "events_by_type": {},
        "log_directory": str(LOG_DIR.absolute())
    }

    for log_file in get_log_files():
        stats["total_files"] += 1
        with open(log_file, "r") as f:
            for line in f:
                stats["total_events"] += 1
                try:
                    entry = json.loads(line)
                    event_type = entry.get("event_type", "unknown")
                    stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
                except json.JSONDecodeError:
                    pass

    return stats


if __name__ == "__main__":
    # Test logging
    print("Testing data logger...")
    log_event("test", {"message": "Hello from data logger!"})
    print(f"\nLog directory: {LOG_DIR.absolute()}")
    print(f"Stats: {get_log_stats()}")
