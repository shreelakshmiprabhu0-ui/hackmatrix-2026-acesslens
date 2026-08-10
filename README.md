# ♿ AccessLens

### AI-Powered Web Accessibility Assistant

**Making the web understandable, actionable, and accessible — one website at a time.**

**HackMatrix 2K26 · Team NEXORA**

> AccessLens scans websites for accessibility violations, translates complex WCAG findings into plain English, prioritizes what matters most, and provides actionable code-level fixes — so developers can actually fix accessibility issues instead of just receiving another technical report.

---

## 🌐 Live Demo

🚀 **[Launch AccessLens](https://accesslens-nine.vercel.app/)**

---

## 📊 Project Presentation

📄 **[View / Download Project PPT](AcessLens.pptx)**

---

## 🎥 Demo Video

▶️ **[Watch the AccessLens Demo Video](YOUR_DEMO_VIDEO_LINK)**

> The demo video provides a walkthrough of the complete AccessLens workflow, from website scanning to accessibility analysis, AI explanations, recommendations, and report generation.

---

# 🎯 The Problem

Millions of websites remain inaccessible to people with visual, motor, and cognitive disabilities.

Although tools such as accessibility auditors can detect technical violations, their reports are often difficult for beginners, students, startups, and small development teams to understand.

Developers are left with questions like:

- What does this violation actually mean?
- Why does it matter?
- How serious is it?
- What should I change in my code?
- How do I make sure the fix follows WCAG guidelines?

As a result, accessibility issues can remain unresolved even after being detected.

### The gap

**Detection is not the same as understanding.**

AccessLens bridges that gap.

---

# 💡 Our Solution

**AccessLens** is an AI-powered accessibility assistant that converts technical accessibility audit results into **clear, prioritized, developer-friendly actions**.

Instead of simply saying:

> ❌ `Image elements do not have [alt] attributes`

AccessLens helps the developer understand:

> 🧠 What the issue means  
> ⚠️ Why it matters  
> 📌 How severe it is  
> 💻 How to fix it  
> 📚 What accessibility principle it relates to

### The core idea

```text
Technical Accessibility Data
            ↓
      AccessLens Engine
            ↓
   AI-Powered Explanation
            ↓
   Prioritized Recommendations
            ↓
       Code-Level Fixes
            ↓
   More Accessible Websites
⚙️ How AccessLens Works
Step 1 — Enter Website URL

The developer provides the URL of a publicly accessible website.

Step 2 — Accessibility Scan

AccessLens performs an automated accessibility audit using the accessibility scanning infrastructure.

Step 3 — Detect Violations

The system identifies accessibility violations and maps them to relevant WCAG criteria.

Step 4 — AI Explanation

The detected issues are passed through the AI-powered accessibility assistant.

Technical findings are transformed into understandable explanations.

Step 5 — Prioritize Issues

Issues are organized according to severity:

🔴 Critical
🟠 Moderate
🔵 Minor

This helps developers focus on the problems that matter most first.

Step 6 — Generate Fixes

AccessLens provides practical, code-level recommendations to help developers resolve the detected issue.

Step 7 — Accessibility Dashboard

The dashboard presents:

Accessibility score
Issue count
Severity distribution
WCAG criteria
Affected elements
AI-powered explanations
Recommended fixes
Step 8 — Export Report

Developers can export the accessibility analysis as a downloadable report for documentation, review, or further development.

✨ Key Features
Feature	Description
🔍 Automated Accessibility Scan	Scan a public website for accessibility issues
🤖 AI-Powered Explanations	Converts technical findings into plain English
⚠️ Severity Prioritization	Separates critical, moderate, and minor issues
💻 Code-Level Fix Suggestions	Provides actionable recommendations for developers
📊 Accessibility Score	Gives an easy-to-understand overview of website accessibility
📋 WCAG Mapping	Connects violations to relevant WCAG criteria
🎯 Affected Element Details	Shows which elements are responsible for each issue
📚 Accessibility Guidance	Helps developers understand accessibility concepts
📄 Exportable Reports	Generate downloadable accessibility reports
🌐 Web-Based Interface	No local accessibility tooling required for end users
🧠 AI-Powered Accessibility Assistance

Traditional accessibility tools are excellent at finding problems.

AccessLens focuses on the next question:

"Okay... now what do I do about it?"

For every detected issue, AccessLens can provide:

What it means

A plain-English explanation of the accessibility problem.

Why it matters

Explains how the issue can affect users, especially people using assistive technologies.

How to fix it

Provides practical guidance and code-level recommendations.

Accessibility context

Connects the issue to relevant accessibility and WCAG concepts.

This makes AccessLens useful not only as an auditing tool, but also as an accessibility learning assistant.

🏗️ Architecture
                         ┌─────────────────────┐
                         │     Developer       │
                         │   Website URL       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   AccessLens        │
                         │     Frontend        │
                         │ React + Tailwind CSS│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend        │
                         │       Python        │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
       ┌─────────────────────┐             ┌─────────────────────┐
       │ Accessibility       │             │     Gemini API      │
       │ Scanning Engine     │             │  AI Explanation     │
       │ Lighthouse /        │             │  & Recommendations  │
       │ PageSpeed Insights  │             └──────────┬──────────┘
       └──────────┬──────────┘                        │
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  Analysis &         │
                         │  Prioritization     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ AccessLens          │
                         │ Results Dashboard   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                ┌────────────────┐    ┌────────────────┐
                │ AI Fix         │    │ Export Report  │
                │ Suggestions    │    │                │
                └────────────────┘    └────────────────┘
🛠️ Technology Stack
Frontend
React
JavaScript
JSX
HTML5
CSS3
Tailwind CSS
Vite
Backend
Python
FastAPI
Uvicorn
REST APIs
Accessibility Engine
Lighthouse
Google PageSpeed Insights API
WCAG
Accessibility audit data
AI Layer
Google Gemini API
AI-powered explanation
Accessibility guidance
Fix recommendations
Deployment
Vercel — Frontend
Render — Backend
Development & Configuration
Git
GitHub
JSON
Environment Variables
Markdown
💻 Languages Used
Language / Format	Usage
🐍 Python	Backend, FastAPI APIs, accessibility processing
🟨 JavaScript	Frontend application logic and API integration
⚛️ JSX	React components and UI
🌐 HTML5	Web structure
🎨 CSS3	Styling
🟦 JSON	API data, configuration, mock data
📝 Markdown	Documentation and README
📸 Screenshots
🏠 AccessLens Home

The landing interface allows developers to enter a public website URL and start an accessibility scan.

📊 Accessibility Results

The results dashboard provides:

Overall accessibility score
Critical issues
Moderate issues
Minor issues
WCAG criteria
Affected elements
Issue descriptions
🤖 AI-Powered Explanation

AccessLens translates technical accessibility findings into plain-English explanations and actionable guidance.

📄 Accessibility Report

Developers can review and export the accessibility analysis as a structured report.

🚀 Running AccessLens Locally
1. Clone the repository
git clone https://github.com/shreelakshmiprabhu0-ui/hackmatrix-2026-acesslens.git
cd hackmatrix-2026-acesslens
🔹 Backend Setup

Navigate to the backend:

cd backend

Create a virtual environment:

Windows
python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the backend:

uvicorn app.main:app --reload --port 8000

The backend will run locally at:

http://localhost:8000
🔹 Frontend Setup

Open another terminal.

Navigate to the frontend:

cd frontend

Install dependencies:

npm install

Create/configure the environment file:

VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false

Start the development server:

npm run dev

The frontend will normally be available at:

http://localhost:5173
🔐 Environment Variables
Frontend
VITE_API_BASE_URL=<BACKEND_URL>
VITE_USE_MOCK_DATA=false
Backend

Configure the required API credentials through environment variables.

⚠️ Never commit API keys or other secrets to GitHub.

📁 Repository Structure
hackmatrix-2026-acesslens/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── mocks/
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── requirements.txt
│   └── ...
│
├── screenshots/
│   ├── home.png
│   ├── results.png
│   ├── ai-explanation.png
│   └── report.png
│
├── AcessLens.pptx
├── README.md
└── .gitignore
📦 Deliverables
Deliverable	Details
🌐 Live Application	Deployed AccessLens web application
📄 Project PPT	AcessLens.pptx
🎥 Demo Video	Complete product walkthrough
💻 Source Code	Frontend + backend available in this repository
📸 Screenshots	Product workflow and dashboard screenshots
🌍 Deployment
Frontend

The AccessLens frontend is deployed using Vercel.

Backend

The AccessLens backend is deployed using Render.

Production Flow
User
 │
 ▼
AccessLens Frontend
 │
 │ REST API
 ▼
AccessLens Backend
 │
 ├── Accessibility Audit
 │
 └── Gemini AI
       │
       ▼
Accessibility Analysis
 │
 ▼
Frontend Dashboard
 │
 ├── AI Explanation
 ├── Fix Suggestions
 └── Export Report
🎯 Why AccessLens?

Accessibility tools should not stop at:

"Here is what's wrong."

They should help developers reach:

"Here is why it matters — and here is how to fix it."

AccessLens reduces the gap between accessibility detection and accessibility action.

It makes accessibility:

Easier to understand
Easier to prioritize
Easier to fix
Easier to learn
🌱 Social Impact

AccessLens aims to contribute to a more inclusive digital ecosystem by helping developers build websites that work better for everyone.

Impact
♿ Promotes digital inclusion
🌐 Encourages accessible web development
📚 Makes accessibility easier for beginners to learn
⚡ Reduces the time required to understand accessibility issues
📋 Encourages WCAG-aware development
💻 Helps developers turn audit results into actionable fixes
🔮 Future Scope

AccessLens can evolve beyond a standalone web application.

Planned possibilities
🌐 Browser Extension
Scan the current webpage directly from the browser.
💻 VS Code Extension
Detect accessibility issues while developers write code.
🔄 CI/CD Integration
Automatically scan websites during development and deployment pipelines.
🏢 Enterprise Dashboard
Track accessibility across multiple websites and projects.
📈 Accessibility History
Track accessibility scores and improvements over time.
🤖 AI-Assisted Remediation
Move from recommending fixes toward generating safer, developer-reviewed patches.
👥 Team NEXORA
Member	Role
Shreelakshmi Prabhu	Development & Integration
Shivani B	Development
Minvitha	Development
Diya Sajin	Development
🏁 Conclusion

AccessLens is more than an accessibility scanner.

It is an accessibility assistant designed to turn:

Audit Results
      ↓
Understanding
      ↓
Prioritization
      ↓
Actionable Fixes
      ↓
Accessible Websites

Because accessibility should not be a checkbox.

It should be built into the web. ♿🌐
📚 Standards & Technologies
WCAG — Web Content Accessibility Guidelines
Lighthouse accessibility auditing
Google PageSpeed Insights
FastAPI
React
Tailwind CSS
Google Gemini
Vercel
Render
⭐ Support the Project

If AccessLens helped you understand or improve web accessibility, consider giving the repository a ⭐.

Built with ❤️ by Team NEXORA
HackMatrix 2K26

### ⚠️ Two things you MUST change before committing

**1. Demo video**

I don't have your actual video URL, so I deliberately used:

```text
YOUR_DEMO_VIDEO_LINK

Don't leave that in the final README. Replace it with your YouTube/Google Drive link.
