# ServiceDesk Plus Compliance Automation Tool

A Streamlit web application that merges, cleans and processes endpoint compliance CSV reports to automate ticket creation in ServiceDesk Plus (SDP).

Built using Python, Streamlit, and concurrent batch processing (`ThreadPoolExecutor`), this tool eliminates manual CSV cross-referencing and automates ticket generation while enforcing real-time audit control and emergency-stop guardrails.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red.svg)](https://streamlit.io/)
[![ServiceDesk Plus](https://img.shields.io/badge/ServiceDesk%20Plus-REST%20API%20v3-orange.svg)](https://www.manageengine.com/products/service-desk/)

---

## Context & Impact

While working as an IT Support Engineer, weekly compliance checks were a massive operational bottleneck. The process required pulling two separate MCM reports, manually cross-referencing ~2,000 rows in Excel (~1,000 machines per report), checking ServiceDesk Plus (SDP) for existing open tickets, looking up device ownership data and filling out ticket templates line-by-line.

I built this Streamlit app to automate that entire workflow.
It cleans and merges both CSV reports, matches endpoints if in both reports and displays flagged devices in an interactive table. Then once you dispatch the structured tickets, via the SDP API, it will cross reference the SDP Asset register for device ownership (which will inject into the ticket body) and send back the created/updated ticket number on the Streamlit app.

### Impact
* Reduced total process time from ***0.5-3 days*** down to under ***15 minutes***.
* Reclaimed ***6-24 hours per week*** of engineering labour.
* Eliminated duplicate tickets and manual cross-referencing errors.

---

## Key Features

* Dispatches requests concurrently in batches of 5.
* Strips metadata header noise, normalises hostnames and matches records across report types.
* Identifies existing open tickets to append notes rather than creating duplicate tickets.
* Emergency button instantly stops outgoing API requests and outputs an audit log of all actions taken prior to cancellation.
* Session data runs in memory and clears automatically when the tab is closed or refreshed.

---

## Interface Preview

### 1. Upload CSVs
Upload raw CSV exports (e.g. Windows Updates & Endpoint Scan reports) to correlate missing updates and check-in activity.

![Upload CSVs](images/upload-view.png)

### 2. Merged Review
Interactive review table of the merged results.

![Merged Results Table](images/merged-table-view.png)

### 3. Concurrent Dispatch
Monitor real time ticket creation with progress indicators and emergency stop protection.

![Dispatch System](images/dispatch-tickets-view.png)

### 4. Audit Preview
View which endpoints have had a ticket created or updated.

![Audit System](images/audit-view.png)

---

## Logic Flow

```text
[ Raw CSV 1: Windows Updates      ] ────┐
                                        ├──> [ Normalise Hostnames & Filter ] ──> [ Parallel Dispatch (5 Workers) ] ──> [ ServiceDesk Plus API ]
[ Raw CSV 2: Endpoint Scan Report ] ────┘
```

1. Raw CSVs dropped into designated slots, automatically stripping metadata headers based on offset rules in `config.py`.
2. Normalises hostnames (uppercase, strips domain suffixes) to cross-reference data.
3. Flags devices with missing updates or inactive days above defined limits.
4. Submits concurrent API payload requests to SDP to fetch open tickets or create/update them dynamically.

---

## Repository Structure

```
sdp-compliance-tool/
├── app.py              # Streamlit dashboard UI and SDP dispatch logic
├── config.py           # app settings, site mappings and ticket templates
├── requirements.txt    # python package dependencies
└── README.md           # project documentation
```

---

## Prerequisites

* Python 3.10+
* ServiceDesk Plus instance with REST API v3 enabled
* Azure AD/SSO App Registration if enforcing organisational SSO.
* SDP OAuth2 credentials with specified scopes mentioned in the ***SDP API Scope*** section.
* This app is setup to work on Streamlit Cloud, which provides the UI.

---

## SDP API Scope

The scope required for the service account used by this application:
```text
SDPOnDemand.requests.CREATE,SDPOnDemand.requests.READ,SDPOnDemand.requests.UPDATE,SDPOnDemand.assets.READ
```
This allows the app to check if any tickets already exist (`SDPOnDemand.requests.READ`), create new tickets (`SDPOnDemand.requests.CREATE`), update existing tickets with new information (`SDPOnDemand.requests.UPDATE`) and read the asset register on SDP for asset state/user information (`SDPOnDemand.assets.READ`).

---

## Quick Start & Setup

### 1. Clone & Install
```bash
git clone https://github.com/ajmachowiak/sdp-compliance-tool.git
cd sdp-compliance-tool
pip install -r requirements.txt
```

### 2. Configure Local Secrets (`.streamlit/secrets.toml`)
Configure your local secrets file *(or Streamlit Cloud Secrets manager)*:

```toml
[azure]
client_id = "your-azure-client-id"
tenant_id = "your-azure-tenant-id"

[sdp]
client_id = "your-sdp-client-id"
client_secret = "your-sdp-client-secret"
refresh_token = "your-sdp-refresh-token"
accounts_url = "https://accounts.manageengine.com"
api_domain = "https://your-sdp-instance.com"
```

### 3. Run App Locally
```bash
streamlit run app.py
```

---

## Configuration (`config.py`)

All site-specific settings, thresholds and mappings are centralised in `config.py`.

### 1. Adjusting Compliance Thresholds
Update the default filtering logic to match your IT security policies:
* `MIN_MISSING_UPDATES = 1` - Minimum required missing critical updates to flag.
* `MIN_INACTIVE_DAYS = 14` - Minimum allowed days since last endpoint check-in/scan.

### 2. CSV Header Skip Logic
Adjust header row offsets based on how your reporting tools export reports:
* `UPDATES_SKIPROWS = 11` - Metadata rows skipped for the Windows Updates CSV.
* `SCAN_REPORT_SKIPROWS = 3` - Metadata rows skipped for the Endpoint Scan CSV.

### 3. SDP Ticket Template & Site Mapping
Customise site routing and default ticket content:
* `get_site_from_pc()` - Maps device hostname prefixes to their corresponding SDP Site names.
* `ADMIN_USERS` - List of engineer email addresses granted admin access to modify templates within the app interface.
* `DEFAULT_TICKET_TEMPLATE` - Template string sent to SDP containing dynamic tags like `{PCName}`, `{Updates}`, `{DeviceScan}`, `{Site}`, `{AssetState}`, and `{AssignedUser}`.

### 4. Parallel Worker Limits
`MAX_WORKERS = 5` - Defaults to 5 concurrent threads to balance speed with SDP rate limits. Adjust based on your API server capacity.

---

## Issues & Support

If you encounter a bug, have a feature request or run into issues with report formatting:

1. Search the GitHub Issues tab to see if it has already been reported.
2. Provide details about expected vs. actual behavior, along with relevant error logs (ensuring no sensitive data or credentials are included).
3. Contributions are welcome! Feel free to fork the repo and submit a PR.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
