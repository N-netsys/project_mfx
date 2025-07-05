# mfx: A Cloud-Native Microfinance Management Platform

This repository contains the source code for mfx, a multi-tenant platform for Microfinance Institutions.

## Project Overview

mfx provides a comprehensive suite of tools for managing clients, loans, savings, and field operations. Built as a modern cloud-native application, it aims to be scalable, secure, and cost-effective.

### Tech Stack

- **Frontend:** Next.js (React)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Deployment:** Vercel (Frontend), Render (Backend & DB)
- **Containerization:** Docker

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- Git

### Backend Setup

1. Navigate to the `backend` directory: `cd backend`
2. Create and activate a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file from the `.env.example` and fill in your database URL and a secret key.
5. Run database migrations: `alembic upgrade head`
6. Run the development server: `uvicorn app.main:app --reload`

---

## Deployment

The application is configured for automatic CI/CD deployment.
- Pushing to the `main` branch deploys the `frontend` to Vercel.
- Pushing to the `main` branch deploys the `backend` to Render.