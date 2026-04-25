# =====================================================
# SECTION: Imports
# Purpose: Import all required libraries and modules
# =====================================================
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import json

# =====================================================
# SECTION: Configuration
# Purpose: Initialize Jinja2 templates and project filters
# =====================================================
templates = Jinja2Templates(directory="app/templates")

# =====================================================
# SECTION: Custom Filters
# Purpose: Functions to format time and data for UI
# =====================================================

def time_ago_filter(dt):
    # Converts a datetime object into a user-friendly string (e.g., '2h ago')
    if not dt: return ""
    if not isinstance(dt, datetime): return str(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = datetime.now(timezone.utc) - dt
    seconds = diff.total_seconds()
    
    if seconds < 60: return "now"
    elif seconds < 3600: return f"{int(seconds // 60)}m ago"
    elif seconds < 86400: return f"{int(seconds // 3600)}h ago"
    elif seconds < 604800: return f"{int(seconds // 86400)}d ago"
    else: return dt.strftime("%b %d")

from typing import Any, Union, Optional
import json

def format_duration_filter(seconds: Any) -> str:
    # Formats a numerical duration into a readable string (e.g., '1.5h')
    if seconds is None or seconds == "": return "--"
    
    try:
        val: float = float(seconds)
    except (ValueError, TypeError):
        return str(seconds)

    if val < 60: 
        return f"{int(val)}s"
    elif val < 3600: 
        return f"{int(val // 60)} min"
    elif val < 86400: 
        # Using string formatting to avoid Pyre's round() overload confusion
        rounded_h: float = float(f"{val / 3600:.1f}")
        return f"{rounded_h}h"
    else: 
        # Using string formatting to avoid Pyre's round() overload confusion
        rounded_d: float = float(f"{val / 86400:.1f}")
        return f"{rounded_d} days"

# Register filters with the Jinja2 environment
templates.env.filters["time_ago"] = time_ago_filter
templates.env.filters["format_duration"] = format_duration_filter
templates.env.filters["tojson"] = lambda v: json.dumps(v)

def utc_iso_filter(dt) -> str:
    # Returns an ISO-8601 UTC string that JavaScript's new Date() can parse correctly.
    # Always appends 'Z' to signal UTC so browsers convert to local time automatically.
    if not dt: return ""
    if not isinstance(dt, datetime): return str(dt)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

templates.env.filters["utc_iso"] = utc_iso_filter

# =====================================================
# SECTION: Context Processors
# Purpose: Inject global variables into all templates
# =====================================================

def notification_context(request):
    # Provides notification counts and latest alerts globally to the layout
    return {
        "unread_count": getattr(request.state, "unread_count", 0),
        "recent_notifications": getattr(request.state, "recent_notifications", [])
    }

templates.context_processors.append(notification_context)


