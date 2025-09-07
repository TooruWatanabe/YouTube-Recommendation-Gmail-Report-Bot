# YouTube-Recommendation-Gmail-Report-Bot
This project is an automated reporting system that integrates the YouTube Data API, OpenAI API, and Gmail API—combining data engineering and AI skills.
It fetches the latest videos for selected interests (e.g., EVs, autonomous driving, AI, data engineering, CRM, overseas job search), then uses AI to score and summarize them, sending only the most relevant items by email.
The automation helps prevent missing important updates.

# Problem & Solution
Problem: It’s difficult to efficiently surface valuable content from the huge volume of videos uploaded every day.
Solution: Automate the pipeline—collection, summarization, scoring, and notification—using APIs and LLMs.
Outcome: A daily Gmail report delivers high-value videos so you can keep up without missing key information.

# Tech Stack
Language: Python 3.10
APIs:
YouTube Data API v3 (search & metadata)
OpenAI GPT-4o-mini (summarization & relevance scoring)
Gmail API (email delivery)
Other: OAuth2 authentication, cron for scheduled runs, optional CSV logging for history

# Key Features
YouTube search across multiple keywords (up to 50 results per query)
LLM-based summaries and profile-aware relevance scores
Threshold filter (e.g., include only score ≥ 70)
Automated email report via Gmail API
Daily execution via cron to continuously collect fresh content
