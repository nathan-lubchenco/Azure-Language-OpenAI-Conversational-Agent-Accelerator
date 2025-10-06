#!/usr/bin/env python3
"""
HACKDAY: View and analyze logged conversation data
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

LOG_DIR = Path("./hackday_logs")


def print_separator(char="=", length=80):
    print(char * length)


def view_latest_logs(count=10, event_type=None):
    """View the most recent log entries"""
    log_files = sorted(LOG_DIR.glob("*.jsonl"), reverse=True)

    if not log_files:
        print("❌ No log files found in", LOG_DIR.absolute())
        return

    print(f"\n📂 Reading from: {LOG_DIR.absolute()}")
    print_separator()

    entries = []
    for log_file in log_files:
        with open(log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if event_type is None or entry.get("event_type") == event_type:
                        entries.append(entry)
                except json.JSONDecodeError:
                    pass

    # Sort by timestamp, most recent first
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Display requested number
    for i, entry in enumerate(entries[:count], 1):
        print(f"\n📝 Entry {i}/{min(count, len(entries))}")
        print(f"⏰ {entry.get('timestamp', 'N/A')}")
        print(f"🏷️  Type: {entry.get('event_type', 'unknown')}")

        if entry.get("event_type") == "utterance_extraction":
            print(f"📥 Original: {entry.get('original_message', '')}")
            print(f"🔍 Extracted: {entry.get('extracted_utterances', [])}")
            print(f"🤖 Model: {entry.get('model', 'N/A')}")

        elif entry.get("event_type") == "orchestration":
            print(f"💬 Message: {entry.get('message', '')}")
            print(f"🎯 Route: {entry.get('route', 'N/A')}")
            print(f"🔧 Router: {entry.get('router_type', 'N/A')}")

        elif entry.get("event_type") == "chat_completion":
            print(f"📥 Original: {entry.get('original_message', '')}")
            print(f"🔢 Utterances ({entry.get('utterance_count', 0)}): {entry.get('utterances', [])}")
            print(f"💬 Responses ({entry.get('response_count', 0)}): {entry.get('responses', [])}")
            print(f"🤖 Model: {entry.get('model', 'N/A')}")
            print(f"🔧 Router: {entry.get('router_type', 'N/A')}")

        elif entry.get("event_type") == "error":
            print(f"❌ Error Type: {entry.get('error_type', 'N/A')}")
            print(f"💥 Message: {entry.get('error_message', 'N/A')}")

        print_separator("-")

    if len(entries) > count:
        print(f"\n... and {len(entries) - count} more entries")

    print(f"\n✅ Total entries: {len(entries)}")


def show_stats():
    """Show statistics about logged data"""
    log_files = sorted(LOG_DIR.glob("*.jsonl"))

    if not log_files:
        print("❌ No log files found in", LOG_DIR.absolute())
        return

    print(f"\n📊 Log Statistics")
    print_separator()

    total_events = 0
    event_types = Counter()
    models_used = Counter()
    routes_used = Counter()

    for log_file in log_files:
        print(f"📁 {log_file.name}")
        with open(log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_events += 1
                    event_types[entry.get("event_type", "unknown")] += 1

                    if "model" in entry:
                        models_used[entry.get("model")] += 1
                    if "route" in entry:
                        routes_used[entry.get("route")] += 1
                except json.JSONDecodeError:
                    pass

    print(f"\n📈 Summary:")
    print(f"  Total events: {total_events}")
    print(f"  Log files: {len(log_files)}")

    print(f"\n🏷️  Event Types:")
    for event_type, count in event_types.most_common():
        print(f"  {event_type}: {count}")

    if models_used:
        print(f"\n🤖 Models Used:")
        for model, count in models_used.most_common():
            print(f"  {model}: {count}")

    if routes_used:
        print(f"\n🎯 Routes Taken:")
        for route, count in routes_used.most_common():
            print(f"  {route}: {count}")


def search_logs(query):
    """Search for messages containing a specific query"""
    log_files = sorted(LOG_DIR.glob("*.jsonl"), reverse=True)

    if not log_files:
        print("❌ No log files found in", LOG_DIR.absolute())
        return

    print(f"\n🔍 Searching for: '{query}'")
    print_separator()

    matches = []
    for log_file in log_files:
        with open(log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Search in all string fields
                    entry_str = json.dumps(entry).lower()
                    if query.lower() in entry_str:
                        matches.append(entry)
                except json.JSONDecodeError:
                    pass

    if not matches:
        print(f"❌ No matches found for '{query}'")
        return

    print(f"✅ Found {len(matches)} matches\n")

    for i, entry in enumerate(matches, 1):
        print(f"📝 Match {i}/{len(matches)}")
        print(f"⏰ {entry.get('timestamp', 'N/A')}")
        print(f"🏷️  Type: {entry.get('event_type', 'unknown')}")
        print(json.dumps(entry, indent=2))
        print_separator("-")


def main():
    if not LOG_DIR.exists():
        print(f"❌ Log directory not found: {LOG_DIR.absolute()}")
        print("💡 Start the app and make some queries first!")
        return

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            show_stats()
        elif command == "search" and len(sys.argv) > 2:
            search_logs(sys.argv[2])
        elif command == "utterances":
            view_latest_logs(count=20, event_type="utterance_extraction")
        elif command == "orchestration":
            view_latest_logs(count=20, event_type="orchestration")
        elif command == "completions":
            view_latest_logs(count=20, event_type="chat_completion")
        elif command == "errors":
            view_latest_logs(count=20, event_type="error")
        elif command.isdigit():
            view_latest_logs(count=int(command))
        else:
            print("❌ Unknown command")
            print_usage()
    else:
        view_latest_logs(count=10)


def print_usage():
    print("""
Usage: python view_logs.py [command]

Commands:
  (no args)           View 10 most recent log entries
  <number>            View N most recent log entries (e.g., 20)
  stats               Show statistics about logged data
  utterances          Show only utterance extraction logs
  orchestration       Show only orchestration logs
  completions         Show only chat completion logs
  errors              Show only error logs
  search <query>      Search logs for a specific string

Examples:
  python view_logs.py                    # View latest 10 entries
  python view_logs.py 50                 # View latest 50 entries
  python view_logs.py stats              # Show statistics
  python view_logs.py search "return"    # Search for "return" in logs
  python view_logs.py utterances         # View utterance extractions
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
