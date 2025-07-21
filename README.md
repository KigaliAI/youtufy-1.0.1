Youtufy — Your Personalized YouTube Dashboard
Youtufy is a full-stack web app that helps users connect their YouTube account, analyze their channel subscriptions,
and view insightful video/channel data via a clean, intuitive dashboard.

Features

- 🔐 OAuth 2.0 authentication via Google
- 🎯 Fetch YouTube subscriptions, stats, and latest uploads
- 📊 Dashboard for personal insights
- 🗃️ PostgreSQL for data storage
- 🐳 Fully Dockerized for easy development and deployment


Tech Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Auth: Google OAuth2 (via `google-auth`)
- Frontend: Deployed via 
- Database: PostgreSQL (local via Docker, or managed on GCP Cloud SQL)
- Deployment: Docker + Docker Compose
