import urllib.request
import re
from datetime import datetime, date, timedelta

CALENDAR_URL = "https://outlook.office365.com/owa/calendar/8252775f384440778c40dea39da6b29a@rbtautomate.com/d1969139dcfb43a29f8fe347b57e672317692357886224327392/calendar.ics"
OUTPUT_FILE = "docs/jordan_oncall.ics"

def fetch_calendar(url):
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")

def parse_events(raw):
    """Split raw ICS into individual VEVENT blocks."""
    events = []
    in_event = False
    current = []
    for line in raw.splitlines():
        if line.strip() == "BEGIN:VEVENT":
            in_event = True
            current = [line]
        elif line.strip() == "END:VEVENT":
            current.append(line)
            events.append("\n".join(current))
            in_event = False
            current = []
        elif in_event:
            current.append(line)
    return events

def get_summary(event_text):
    for line in event_text.splitlines():
        if line.startswith("SUMMARY:"):
            return line[len("SUMMARY:"):].strip()
    return ""

def get_dtstart(event_text):
    for line in event_text.splitlines():
        if line.startswith("DTSTART"):
            # Handle both DATE and DATETIME formats
            val = line.split(":")[-1].strip()
            return val
    return ""

def is_jordan_oncall(event_text):
    summary = get_summary(event_text).lower()
    has_jordan = "jordan" in summary
    has_oncall = "on call" in summary or "oncall" in summary
    return has_jordan and has_oncall

def is_jordan_vacation(event_text):
    summary = get_summary(event_text).lower()
    has_jordan = "jordan" in summary
    has_vacation = "vacation" in summary
    return has_jordan and has_vacation

def expand_rrule(event_text, rrule_until_cutoff=None):
    """
    For recurring events, expand them into individual date occurrences.
    Returns a list of DTSTART date strings.
    """
    dtstart = None
    rrule = None
    exdates = []

    for line in event_text.splitlines():
        if line.startswith("DTSTART"):
            dtstart = line.split(":")[-1].strip()
        elif line.startswith("RRULE:"):
            rrule = line[len("RRULE:"):]
        elif line.startswith("EXDATE"):
            # EXDATE;TZID=...:20250926T000000
            val = line.split(":")[-1].strip()
            # Normalize to date only
            exdates.append(val[:8])

    if not dtstart or not rrule:
        return [dtstart] if dtstart else []

    # Parse RRULE components
    freq = None
    interval = 1
    until = None

    for part in rrule.split(";"):
        if part.startswith("FREQ="):
            freq = part[5:]
        elif part.startswith("INTERVAL="):
            interval = int(part[9:])
        elif part.startswith("UNTIL="):
            until_str = part[6:].replace("Z", "")
            try:
                until = datetime.strptime(until_str[:8], "%Y%m%d").date()
            except:
                until = None

    if freq != "DAILY":
        return [dtstart]

    # Parse start date
    try:
        start = datetime.strptime(dtstart[:8], "%Y%m%d").date()
    except:
        return [dtstart]

    if until is None:
        # Default cutoff: 2 years from today
        until = date.today() + timedelta(days=730)

    dates = []
    current = start
    while current <= until:
        date_str = current.strftime("%Y%m%d")
        if date_str not in exdates:
            dates.append(date_str)
        current += timedelta(days=interval)

    return dates

def make_single_event(event_text, date_str, uid_suffix=""):
    """Create a single non-recurring VEVENT for a specific date."""
    lines = []
    skip_keys = {"RRULE", "EXDATE"}
    
    # Parse the date
    try:
        event_date = datetime.strptime(date_str[:8], "%Y%m%d").date()
        next_date = event_date + timedelta(days=1)
        dtstart_val = event_date.strftime("%Y%m%d")
        dtend_val = next_date.strftime("%Y%m%d")
    except:
        dtstart_val = date_str[:8]
        dtend_val = date_str[:8]

    lines.append("BEGIN:VEVENT")
    for line in event_text.splitlines():
        if line == "BEGIN:VEVENT" or line == "END:VEVENT":
            continue
        key = line.split(":")[0].split(";")[0]
        if key in skip_keys:
            continue
        if key == "DTSTART":
            lines.append(f"DTSTART;VALUE=DATE:{dtstart_val}")
        elif key == "DTEND":
            lines.append(f"DTEND;VALUE=DATE:{dtend_val}")
        elif key == "UID":
            uid_val = line.split(":", 1)[-1].strip()
            lines.append(f"UID:{uid_val}-{date_str}{uid_suffix}")
        elif key == "RRULE" or key == "EXDATE":
            continue
        else:
            lines.append(line)
    lines.append("END:VEVENT")
    return "\n".join(lines)

def process_event(event_text, output_events):
    """Expand and append a single event (handles RRULE or one-off)."""
    has_rrule = any(line.startswith("RRULE:") for line in event_text.splitlines())
    if has_rrule:
        dates = expand_rrule(event_text)
        for i, d in enumerate(dates):
            output_events.append(make_single_event(event_text, d, uid_suffix=f"-{i}"))
    else:
        dtstart = ""
        for line in event_text.splitlines():
            if line.startswith("DTSTART"):
                dtstart = line.split(":")[-1].strip()[:8]
                break
        if dtstart:
            output_events.append(make_single_event(event_text, dtstart))

def build_jordan_ics(events):
    output_events = []

    for event_text in events:
        if is_jordan_oncall(event_text) or is_jordan_vacation(event_text):
            process_event(event_text, output_events)

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Jordan On Call//EN",
        "CALNAME:Jordan Schedule",
        "X-WR-CALNAME:Jordan Schedule",
        "X-WR-CALDESC:Jordan on-call and vacation schedule from RBT Work Calendar",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for ev in output_events:
        ics_lines.append(ev)

    ics_lines.append("END:VCALENDAR")

    return "\n".join(ics_lines)

def main():
    import os
    os.makedirs("docs", exist_ok=True)

    print("Fetching RBT calendar...")
    raw = fetch_calendar(CALENDAR_URL)

    print("Parsing events...")
    events = parse_events(raw)
    print(f"  Found {len(events)} total events")

    oncall_events = [e for e in events if is_jordan_oncall(e)]
    vacation_events = [e for e in events if is_jordan_vacation(e)]
    print(f"  Found {len(oncall_events)} Jordan on-call events (before expansion)")
    print(f"  Found {len(vacation_events)} Jordan vacation events")

    print("Building ICS...")
    ics_content = build_jordan_ics(events)

    with open(OUTPUT_FILE, "w") as f:
        f.write(ics_content)

    print(f"Written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
