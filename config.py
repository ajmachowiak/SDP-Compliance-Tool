# config.py
"""
Configuration file for Device Compliance & SDP Dispatch Tool.
Modify these settings to fit your organisation's environment and rules.
"""

# ==========================================
# 1. ADMIN & USER PERMISSIONS
# ==========================================
# authorised admin usernames/emails who can edit ticket templates within the app
ADMIN_USERS = [
    "admin1@yourdomain.com",
    "admin2@yourdomain.com",
    "itsupport@yourdomain.com",
]

# ==========================================
# 2. REPORT FORMATTING & CSV HEADER OFFSETS
# ==========================================
# number of metadata rows to skip at the top of raw CSV exports
UPDATES_SKIPROWS = 11           # updates required spreadsheet
SCAN_REPORT_SKIPROWS = 3        # endpoint scan time spreadsheet

# column target positions (1-based index mapped to 'H1', 'H2', etc.)
# Windows Updates Report
UPDATES_PC_NAME_COL = "H1"      # column A: hostname
UPDATES_COUNT_COL = "H10"       # column J: missing critical updates

# Device Endpoint Scan Report
SCAN_PC_NAME_COL = "H1"         # column A: hostname
SCAN_DAYS_COL = "H6"            # column F: days since last scan

# ==========================================
# 3. COMPLIANCE THRESHOLDS
# ==========================================
MIN_MISSING_UPDATES = 1         # minimum updates missing to flag a PC
MIN_INACTIVE_DAYS = 14          # minimum inactive days to flag a PC

# ==========================================
# 4. DISPATCH WORKER CONFIGURATION
# ==========================================
MAX_WORKERS = 5                 # concurrent API request threads for SDP

# ==========================================
# 5. DOMAIN & ASSET SEARCH
# ==========================================
DEFAULT_DOMAIN_SUFFIX = "yourdomain.com"    # modify with your organisation's domain name

def get_search_candidates(base_pc: str) -> list:
    """Generates AD FQDN and hostname search targets for SDP asset lookup."""
    return [
        f"{base_pc.upper()}.{DEFAULT_DOMAIN_SUFFIX}",
        f"{base_pc.lower()}.{DEFAULT_DOMAIN_SUFFIX}",
        base_pc.upper(),
        base_pc.lower(),
    ]

# ==========================================
# 6. SITE MAPPING LOGIC
# ==========================================
def get_site_from_pc(pc_name: str) -> str:
    """Determines SDP Site name based on hostname prefix/naming rules."""
    pc_upper = str(pc_name).strip().upper()

    if pc_upper.startswith("NY"):
        return "New York HQ"
    elif pc_upper.startswith("LON"):
        return "London Office"
    elif pc_upper.startswith("SYD"):
        return "Sydney Office"
    else:
        return "All Sites"

# ==========================================
# 7. SERVICEDESK PLUS (SDP) PAYLOAD DEFAULTS
# ==========================================
SDP_REQUESTER_EMAIL = "itsupport@yourdomain.com"    # this is the user you'd want the request to be made by (eg. a default IT Support email)
SDP_CATEGORY = "Compliance Checks"                  # modify this to the appropriate request category in your SDP config
SDP_REQUEST_TYPE = "Support"                        # modify this to the appropriate request type in your SDP config
SDP_MODE = "Web form"                               # modify this to the appropriate request mode in your SDP config
SDP_IMPACT = "Affects User"
SDP_URGENCY = "Medium"
SDP_PRIORITY = "Medium"

# ==========================================
# 8. DEFAULT TICKET TEMPLATES
# ==========================================
DEFAULT_TICKET_TEMPLATE = (
    "This is an automated notification regarding {PCName}.\n\n"
    "Compliance Findings:\n"
    "- Missing Critical Updates: {Updates}\n"
    "- Days since last check-in: {DeviceScan}\n\n"
    "Please connect to the network as soon as possible to receive outstanding updates.\n\n"
    "SDP Asset Register Info:\n"
    "- Assigned Site: {Site}\n"
    "- Asset State: {AssetState}\n"
    "- Assigned User: {AssignedUser}"
)

def get_note_template(updates, device_scan, asset_state, assigned_user) -> str:
    """Generates the HTML-formatted note appended to existing SDP tickets."""
    updates_str = updates if updates != "" else "0"
    scan_str = device_scan if device_scan != "" else "0"

    return (
        f"<b>Automated Compliance Check Update</b><br><br>"
        f"Compliance Findings:<br>"
        f"- Missing Critical Updates: {updates_str}<br>"
        f"- Days since last check-in: {scan_str}<br><br>"
        f"SDP Asset Status: <b>{asset_state}</b> | Assigned User: <b>{assigned_user}</b>"
    )