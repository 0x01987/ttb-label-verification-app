# TTB Label Verification App

## Overview

The TTB Label Verification App is an AI-assisted prototype designed to help Alcohol and Tobacco Tax and Trade Bureau (TTB) compliance agents review alcohol beverage labels more efficiently.

The application automates portions of the label review process by extracting information from uploaded label images, validating required fields, and comparing extracted values against application data submitted by an applicant.

The goal is to reduce manual verification effort while providing a simple and intuitive user experience for compliance reviewers.

---

## Live Demo

### Frontend Application

https://ttb-label-verification-app.vercel.app

### Backend API

https://ttb-label-verification-app-api.onrender.com

### Source Code Repository

https://github.com/0x01987/ttb-label-verification-app

---

## Screenshots

### Upload & Verification

![Upload](docs/screenshots/upload.png)

### Verification Results

![Results](docs/screenshots/results.png)

### Batch Verification

![Batch](docs/screenshots/batch.png)

---

## Features

### OCR-Based Label Analysis

Extracts text from alcohol beverage labels using OCR technology.

### Required Label Element Detection

The application identifies and validates:

* Brand Name
* Class / Type Designation
* Alcohol Content (ABV)
* Net Contents
* Producer / Bottler Information
* Country of Origin
* Government Health Warning Statement

### Application Verification

Compares extracted label information against expected values provided by the user.

### Fuzzy Matching

Supports minor variations in capitalization, punctuation, and formatting to reduce false mismatches.

Examples:

* STONE'S THROW
* Stone's Throw

### Compliance Scoring

Generates:

* Field-level validation results
* Compliance score
* PASS / REVIEW recommendation

### Batch Verification

Supports uploading multiple labels for batch processing and review.

---

## Technology Stack

### Frontend

* Next.js
* TypeScript
* React
* Tailwind CSS

### Backend

* FastAPI
* Python
* RapidFuzz

### OCR

Development Environment:

* EasyOCR

Hosted Demonstration Environment:

* Lightweight OCR simulation mode

### Deployment

Frontend:

* Vercel

Backend:

* Render

---

## Architecture

User Uploads Label Image

↓

Frontend (Next.js)

↓

Backend API (FastAPI)

↓

OCR Extraction

↓

Field Parsing & Validation

↓

Compliance Scoring

↓

PASS / REVIEW Result

---

## Validation Workflow

1. User uploads a label image.
2. OCR extracts text from the label.
3. Application identifies required label elements.
4. Extracted values are compared against submitted application data.
5. Compliance score is calculated.
6. PASS or REVIEW recommendation is returned.

---

## Supported Fields

| Field                        | Supported |
| ---------------------------- | --------- |
| Brand Name                   | Yes       |
| Class / Type Designation     | Yes       |
| Alcohol Content              | Yes       |
| Net Contents                 | Yes       |
| Producer / Bottler           | Yes       |
| Country of Origin            | Yes       |
| Government Warning Statement | Yes       |
| Batch Verification           | Yes       |

---

## Local Development Setup

### Prerequisites

* Python 3.11+
* Node.js 20+
* npm

---

## Backend Setup

Navigate to backend directory:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

Windows:

```bash
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

API Documentation:

```text
http://127.0.0.1:8001/docs
```

---

## Frontend Setup

Navigate to frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run development server:

```bash
npm run dev
```

Application URL:

```text
http://localhost:3000
```

---

## Assumptions

The following assumptions were made during development:

* Labels are submitted as image files.
* OCR text quality is sufficient for extraction.
* Government warning validation focuses on required content presence.
* Fuzzy matching is appropriate for minor formatting variations.
* Prototype focuses on common TTB-required label elements.
* This application is intended as a proof-of-concept and does not integrate directly with the COLA system.

---

## Deployment Notes

The local development environment uses EasyOCR for actual OCR extraction and label analysis.

The hosted demonstration environment uses a lightweight OCR simulation mode due to free-tier hosting memory limitations associated with EasyOCR and PyTorch dependencies.

This tradeoff allows reviewers to test the full application workflow while keeping the solution deployable on free cloud infrastructure.

---

## Future Enhancements

Potential future improvements include:

* Production-grade OCR deployment
* Image preprocessing using OpenCV
* Confidence scoring per extracted field
* Label image quality assessment
* Advanced TTB rule validation
* COLA workflow integration
* User authentication and audit logging
* Azure Government deployment
* Agent review dashboard
* Historical review analytics

---

## Design Considerations

The user interface was intentionally designed to support users with varying levels of technical proficiency.

Key goals included:

* Minimal clicks
* Large upload area
* Clear PASS / REVIEW indicators
* Simple data entry
* Fast response times
* Easy batch processing

These design choices were informed by stakeholder interviews and intended to support both experienced and less technical compliance reviewers.

---

## Author

Dinel Bun

TTB Label Verification App Prototype
