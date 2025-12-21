# Property AI Agent

An intelligent, event-driven AI system designed to act as a proactive real estate representative. Unlike passive search engines, this system automates the entire "top-of-funnel" real estate process—from finding listings and extracting granular data to physically calling agents and owners on your behalf.


## Project Vision

We are building an intelligent, event-driven AI system that automates the complete real estate discovery and engagement process through five distinct phases:


### 1. The Deep Discovery Phase (Data Extraction)
The system initiates by deploying research agents to scrape real estate platforms based on your specific criteria (e.g., "3-bedroom apartments in Lagos" or "distressed properties for sale"). It extracts structured, rich data including full image galleries, listing agent names and phone numbers, and specific property specs.

### 2. The Human Decision Gate (Quality Control)
Before any costs are incurred on calls or advanced APIs, the workflow pauses. The system presents the sourced properties—complete with the extracted images and specs—to you through a frontend interface where you act as the final decision-maker.

### 3. The Intelligence Phase (Location Analytics)
For every approved property, the system performs a geospatial analysis using Google Maps data to identify "invisible" factors that listing photos hide, such as traffic congestion, noise pollution, proximity to industrial zones, or distance from essential amenities.

### 4. The Engagement Phase (Voice AI Branching)
Based on your initial intent, the workflow splits into specialized paths:
- **Path A: The Inspector** (Rent/Buy): Calls property agents, navigates phone menus, books inspections, and asks your pre-defined questions
- **Path B: The Negotiator** (Acquisition): Calls property owners with persuasion techniques to gauge selling interest and initiate negotiations

### 5. The Delivery Phase (Reporting)
The system compiles all data into a unified report stored in your user account, with notifications sent via Email or WhatsApp when ready.

## Key Technical Components

- **Orchestration:** CrewAI Flows (for state management, pausing, and branching logic)
- **Data Extraction:** Firecrawl (for rendering dynamic websites and capturing hidden data)
- **Voice Interface:** Vapi or Retell AI (for low-latency, human-like voice interactions)
- **Geospatial Intelligence:** Google Maps Platform (Places & Geocoding APIs)
- **Structured Data:** Pydantic models for strict data formatting across all agents

## Features

- ✅ Autonomous property discovery and data extraction
- ✅ Human-in-the-loop approval workflow via frontend interface
- ✅ Advanced location intelligence analysis
- ✅ AI-powered voice calls for inspections and negotiations
- ✅ Background operations that continue when you're offline
- ✅ Comprehensive reporting with multi-channel notifications
- ✅ Privacy-compliant call recording and data handling

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installation

```bash
# Install dependencies
uv sync
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# LLM Provider (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key

# Retell AI Voice Calls
RETELL_API_KEY=your_retell_api_key
RETELL_FROM_NUMBER=+1234567890          # Your Retell-purchased phone number
RETELL_INSPECTOR_AGENT_ID=agent_xxx     # Retell agent for property inspections
RETELL_NEGOTIATOR_AGENT_ID=agent_xxx    # Retell agent for acquisition calls
```

## Project Structure

```
├── src/real_ai_agents/
│   ├── crews/
│   │   ├── call_agent_crew/             # Voice AI call orchestration
│   │   ├── location_analyzer_crew/      # Geospatial analysis
│   │   └── research_crew/               # Property discovery
│   ├── tools/
│   │   └── retell_tools.py              # Retell AI voice call tools
│   └── main.py
├── .kiro/specs/                         # Project specifications
└── README.md
```

## Contributing

This is a private project currently under active development. More information about contributing will be available soon.

## License

Private project - All rights reserved.