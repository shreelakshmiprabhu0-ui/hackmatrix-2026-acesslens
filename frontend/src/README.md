AccessLens Frontend

Overview

The AccessLens frontend provides a user-friendly dashboard for analyzing website accessibility and displaying accessibility reports.

Features

- Website URL input
- Accessibility score display
- Accessibility issue summary
- Severity-based issue classification
- Charts and visualizations
- Detailed accessibility results
- Responsive dashboard UI

Tech Stack

- React.js
- Vite
- JavaScript
- CSS
- Recharts

Project Structure

frontend/
├── src/
│   ├── components/
│   │   ├── charts/
│   │   └── dashboard/
│   ├── pages/
│   │   └── Results.jsx
│   ├── mocks/
│   ├── utils/
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
|
└── README.md

Installation

Clone the repository and move into the frontend directory:

cd frontend

Install dependencies:

npm install

Run the Frontend

Start the development server:

npm run dev

The application will then be available at the local URL shown in the terminal.

Purpose

The frontend is designed to make accessibility analysis easier to understand by presenting accessibility scores, issues, severity levels, and recommendations through a clear visual dashboard.
