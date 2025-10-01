# Outlook MCP Server

A Model Context Protocol (MCP) server that integrates with Microsoft Outlook through Azure Entra ID authentication. This server enables AI assistants to interact with your Outlook email and calendar data securely using Microsoft Graph API.

## Overview

The Outlook MCP server provides a bridge between AI assistants (like Claude) and your Microsoft Outlook account. It uses Azure Entra ID (formerly Azure AD) for secure OAuth authentication and exposes both resources and tools for interacting with your emails and calendar events.

## Features

### 📧 Email Capabilities

- **Search emails** by sender, subject, body content, or date range
- **Access recent emails** from your inbox
- **View unread emails** with full content
- Parse HTML email content into clean, readable text

### 📅 Calendar Capabilities

- **Search calendar events** by title, attendees, or date range
- **Create new calendar events** with attendees, location, and descriptions
- **View today's events** for quick daily planning
- **View this week's events** for weekly overview
- Support for all-day events and timezone management

### 🔐 Security

- OAuth 2.0 authentication via Azure Entra ID
- Secure token-based access to Microsoft Graph API
- User identity information (whoami resource)
- Scoped permissions (Mail.Read, Calendars.ReadWrite)

## What This MCP Tool Can Achieve

The Outlook MCP server enables AI assistants to become your intelligent personal assistant for email and calendar management. Here are some example workflows:

### Workflow 1: Email Triage and Summarization

**Scenario:** You want to catch up on important emails after a vacation.

```text
User: "Show me emails from my manager from the last week"
Assistant: [Uses search_emails tool with sender and date filters]

User: "Summarize the unread emails"
Assistant: [Uses get_unread_mail resource and provides a summary]

User: "Are there any action items I need to follow up on?"
Assistant: [Analyzes email content and identifies action items]
```

**What the tool does:** Searches your mailbox using flexible criteria (sender, date, subject, body), retrieves email content, and enables the AI to analyze and summarize information intelligently.

### Workflow 2: Meeting Scheduling and Coordination

**Scenario:** You need to schedule a meeting with multiple attendees.

```text
User: "Schedule a team meeting next Tuesday at 2pm for 1 hour"
Assistant: [Uses create_calendar_event tool with the specified details]

User: "What meetings do I have tomorrow?"
Assistant: [Uses search_calendar_events with tomorrow's date]

User: "Do I have any conflicts with John between 2-5pm on Friday?"
Assistant: [Uses search_calendar_events with attendee and time filters]
```

**What the tool does:** Creates calendar events with attendees, locations, and descriptions. Searches your calendar to find meetings, check availability, and avoid scheduling conflicts.

### Workflow 3: Daily Planning Assistant

**Scenario:** You want to start your day prepared.

```text
User: "What's on my agenda today?"
Assistant: [Uses get_today_events resource to show all meetings]

User: "Prepare me for today's meetings"
Assistant: [Retrieves event details and provides context for each meeting]

User: "Check if I got any emails from the attendees of my 10am meeting"
Assistant: [Combines calendar and email search to find relevant communications]
```

**What the tool does:** Provides quick access to your daily schedule through pre-configured resources, enabling rapid context gathering for meeting preparation.

### Workflow 4: Event Discovery and Analysis

**Scenario:** You need to understand your schedule patterns or find specific events.

```text
User: "Find all meetings about the Product Launch project this month"
Assistant: [Uses search_calendar_events with title filter]

User: "Who have I been meeting with most frequently?"
Assistant: [Uses search_calendar_events and analyzes attendee patterns]

User: "Show me all-day events in my calendar next week"
Assistant: [Searches calendar with date range filter]
```

**What the tool does:** Enables sophisticated calendar querying based on event titles, attendees, dates, and event types for analytics and discovery.

### Workflow 5: Cross-Reference Communications

**Scenario:** You need to correlate emails and calendar events.

```text
User: "Show me the email thread related to tomorrow's board meeting"
Assistant: [Uses calendar search to find the meeting, then email search for related messages]

User: "Did anyone send me their slides for the presentation?"
Assistant: [Searches emails with context from calendar events]
```

**What the tool does:** Combines email and calendar data to provide context-aware assistance, helping you find related information across both domains.

## Architecture

The server is built using:

- **FastMCP**: MCP server framework with HTTP transport support
- **Microsoft Graph SDK**: Official SDK for accessing Outlook data
- **Azure Identity**: OAuth 2.0 authentication
- **BeautifulSoup**: HTML email parsing

### Components

```text
server/
├── main.py              # Server initialization and setup
├── tools/               # MCP tools (user-invoked actions)
│   ├── calendar.py      # Calendar search and creation tools
│   └── mail.py          # Email search tools
├── resources/           # MCP resources (contextual data)
│   ├── calendar.py      # Today/week calendar views
│   └── mail.py          # Recent/unread email views
└── utils/
    ├── auth.py          # Azure authentication & Graph client
    ├── config.py        # Configuration management
    └── parser.py        # Email HTML parsing
```

## Setup

### Prerequisites

- Python 3.10+
- Azure App Registration with Microsoft Graph API permissions
- Required scopes: `User.Read`, `Mail.Read`, `Calendars.ReadWrite`, `email`, `openid`, `profile`

### Installation

1. Clone the repository:

```bash
git clone https://github.com/MykalMachon/outlook-mcp.git
cd outlook-mcp
```

2. Install dependencies:

```bash
cd server
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` file):

```env
AZURE_CLIENT_ID=your_client_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_SECRET=your_client_secret
BASE_URL=http://localhost:8000
HOST=localhost
PORT=8000
```

4. Run the server:

```bash
python main.py
```

## MCP Resources

Resources provide contextual information that can be automatically included:

- `config://whoami` - Current user information
- `outlook://mail/recent/{count}` - Recent emails (default: 20)
- `outlook://mail/unread/{count}` - Unread emails (default: 20)
- `outlook://calendar/today` - Today's calendar events
- `outlook://calendar/week` - This week's calendar events

## MCP Tools

Tools are functions the AI can invoke to perform actions:

### Email Tools

- `search_emails(sender, subject, body, start_date, end_date, max_results)` - Search for specific emails

### Calendar Tools

- `search_calendar_events(title, attendee, start_date, end_date, max_results)` - Find calendar events
- `create_calendar_event(subject, start_datetime, end_datetime, timezone, location, body, attendees, is_all_day)` - Create new events

## Use Cases

- **Personal Productivity**: Let AI help manage your schedule and emails
- **Executive Assistance**: Automated meeting coordination and email triage
- **Research**: Analyze communication patterns and calendar data
- **Integration**: Connect Outlook data with other AI-powered workflows
- **Accessibility**: Voice-controlled email and calendar management through AI

## Security Considerations

- All authentication goes through Azure Entra ID OAuth 2.0
- Tokens are managed securely and not stored persistently
- The server requires explicit user consent for accessing Outlook data
- Runs with minimum required permissions for specified scopes

## License

MIT; [see the license file](./LICENSE)
