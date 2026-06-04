# Re Jobs

A job board platform where all resume reviews are performed by human staff — no automated screening, no AI scoring. Employers post jobs, candidates apply, and internal reviewers manually evaluate every application.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Application Architecture](#application-architecture)
  - [accounts](#accounts-app)
  - [jobs](#jobs-app)
  - [applications](#applications-app)
  - [reviews](#reviews-app)
  - [billing](#billing-app)
- [URL Structure](#url-structure)
- [Review Workflow](#review-workflow)
- [Billing and Subscriptions](#billing-and-subscriptions)
- [Frontend](#frontend)
- [Production Deployment](#production-deployment)
- [Running Tests](#running-tests)

---

## Overview

Re Jobs is a freemium job board. Employers subscribe to post listings. Job seekers apply with either an uploaded resume (PDF/DOCX) or a resume built directly on-site. Applications are routed to human reviewers who record notes and recommendations. Admins oversee the entire pipeline.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 5.2 |
| Database | PostgreSQL (SQLite for local dev) |
| Frontend | Bootstrap 5.3, Bootstrap Icons 1.11 |
| Payments | Stripe Checkout Sessions |
| Static files | WhiteNoise (production) |
| App server | Gunicorn |
| Web server | Nginx |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Email | django-environ console backend (dev) / SMTP (prod) |

---

## User Roles

| Role | Description |
|---|---|
| Admin | Full system access. Assigns applications to reviewers. Manages all users via Django admin. |
| Reviewer | Internal staff. Receives review assignments. Writes notes and recommendations. |
| Employer | Company accounts. Posts job listings. Views applicants for their own listings. Subscribes to a billing plan. |
| Job Seeker | Candidates. Browses and applies for jobs. Tracks their own application statuses. |

Admins are Django superusers. Reviewers are created by admins via the Django admin panel. Employers and Job Seekers self-register via the public registration form.

---

## Project Structure

```
rejobs/
├── config/                     # Django project package
│   ├── settings/
│   │   ├── base.py             # Shared settings (all environments)
│   │   ├── development.py      # Debug mode, console email, SQLite optional
│   │   └── production.py       # SSL, HSTS, SMTP, compressed static
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/               # Users, profiles, dashboards
│   ├── jobs/                   # Job categories and listings
│   ├── applications/           # Applications, work history, education, skills
│   ├── reviews/                # Review assignments and notes
│   └── billing/                # Subscription plans and Stripe integration
├── templates/                  # All Django HTML templates
│   ├── base.html
│   ├── partials/               # Navbar, footer
│   ├── accounts/
│   ├── applications/
│   ├── billing/
│   ├── dashboard/
│   ├── jobs/
│   └── reviews/
├── static/
│   ├── css/main.css
│   └── js/main.js
├── deploy/
│   ├── nginx.conf
│   ├── gunicorn.service
│   └── setup.sh
├── requirements.txt
├── manage.py
└── .env.example
```

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL (or use SQLite for local dev — see below)
- A Stripe account (optional; billing pages render without it but Stripe calls will fail)

### Steps

```bash
# Clone the repo
git clone https://github.com/lord3nd3r/rejobs.git
cd rejobs

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in values
cp .env.example .env

# Create the database (PostgreSQL)
createdb rejobs_dev

# Apply migrations
python manage.py migrate

# Create an admin account
python manage.py createsuperuser

# Seed billing plans
python manage.py shell -c "
from apps.billing.models import Plan
Plan.objects.get_or_create(tier='free', defaults={'name':'Free','price_monthly':0,'max_active_listings':1,'featured_listings_per_month':0})
Plan.objects.get_or_create(tier='starter', defaults={'name':'Starter','price_monthly':29,'max_active_listings':5,'featured_listings_per_month':1})
Plan.objects.get_or_create(tier='professional', defaults={'name':'Professional','price_monthly':79,'max_active_listings':20,'featured_listings_per_month':5})
"

# Start the dev server
python manage.py runserver
```

App runs at `http://127.0.0.1:8000/`. Django admin at `http://127.0.0.1:8000/admin/`.

### Using SQLite instead of PostgreSQL

In your `.env` file, set:

```
DATABASE_URL=sqlite:///db.sqlite3
```

No `createdb` step needed. Everything else is the same.

---

## Environment Variables

All configuration lives in `.env`. Copy `.env.example` and fill in values.

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Django secret key. Generate with `python -c "import secrets; print(secrets.token_hex(50))"` |
| `DJANGO_DEBUG` | No | `True` for development. Never `True` in production. |
| `DATABASE_URL` | Yes | Database connection string. e.g. `postgres://user:pass@localhost/rejobs_dev` or `sqlite:///db.sqlite3` |
| `ALLOWED_HOSTS` | Yes | Comma-separated hostnames. e.g. `127.0.0.1,localhost` |
| `STRIPE_PUBLISHABLE_KEY` | For billing | Stripe publishable key (`pk_...`) |
| `STRIPE_SECRET_KEY` | For billing | Stripe secret key (`sk_...`) |
| `STRIPE_WEBHOOK_SECRET` | For billing | Stripe webhook signing secret (`whsec_...`) |
| `EMAIL_URL` | No | Email backend URL. Defaults to console output in development. |
| `DEFAULT_FROM_EMAIL` | No | From address for outgoing email. |

---

## Application Architecture

### accounts app

**Models:**

- `CustomUser` — extends `AbstractUser`. Email is the login field (`USERNAME_FIELD = 'email'`). Has a `role` field: `admin`, `reviewer`, `employer`, `job_seeker`. Properties: `is_admin_user`, `is_reviewer_user`, `is_employer_user`, `is_job_seeker_user`.
- `EmployerProfile` — OneToOne to `CustomUser`. Stores company name, description, website, address.
- `JobSeekerProfile` — OneToOne to `CustomUser`. Stores phone, city, summary, LinkedIn URL.

**Key views:**

- `register_view` — Creates user, auto-creates the appropriate profile (employer or job seeker), logs in, redirects to profile completion.
- `login_view` — Email-based authentication using `EmailAuthenticationForm`.
- `complete_profile_view` — Employer or job seeker profile edit form.
- Dashboard views — `dashboard_home` routes each role to its own dashboard view.

**Dashboard views by role:**

| Role | URL | View |
|---|---|---|
| Admin | `/dashboard/admin/` | User counts, unassigned applications table, recent assignments |
| Reviewer | `/dashboard/reviewer/` | Assignment queue: Pending, In Progress, Completed |
| Employer | `/dashboard/employer/` | Listings table with applicant counts and edit links |
| Job Seeker | `/dashboard/jobseeker/` | Application history with statuses |

---

### jobs app

**Models:**

- `JobCategory` — name and slug.
- `JobListing` — full job post. Fields include: `employer` (FK to EmployerProfile), `category`, `title`, `slug` (auto-generated, unique), `description`, `requirements`, `responsibilities`, `job_type` (full_time/part_time/contract/temporary/internship), `work_mode` (onsite/remote/hybrid), `location`, `salary_min`, `salary_max`, `is_salary_public`, `status` (draft/active/paused/closed/expired), `is_featured`, `application_deadline`, `expires_at`.

**Key views:**

- `job_list` — Homepage. Full-text search across title, company, description. Filters by job type, work mode, category. Featured listings appear first. Paginated 20 per page.
- `job_detail` — Shows full listing. Displays apply button if the viewer is a job seeker who hasn't already applied.
- `post_job` — Employer-only. Creates a new listing linked to the employer's profile.
- `edit_job` — Employer-only. Ownership check before allowing edits.

---

### applications app

**Models:**

- `Application` — FK to `JobListing` and `CustomUser`. Fields: `cover_letter`, `resume_file` (uploaded to `media/resumes/<user_id>/`), `resume_headline`, `resume_summary`, `status` (pending/under_review/reviewed/shortlisted/rejected/hired). Unique together on `(job, applicant)` — one application per job per person.
- `WorkExperience` — FK to `Application`. Job title, company, dates, description.
- `Education` — FK to `Application`. Institution, degree, field of study, years.
- `Skill` — FK to `Application`. Name and proficiency level.

**Resume submission methods:**

Applicants choose one of two methods on the apply form:
1. **Upload** — PDF, DOC, or DOCX. Maximum 5 MB. Validated in `ApplicationForm.clean_resume_file`.
2. **Build on-site** — Django inline formsets for work experience, education, and skills. JavaScript toggles which section is visible.

**Key views:**

- `apply` — Enforces job seeker role, prevents duplicate applications, handles both submission methods.
- `my_applications` — Job seeker's own applications.
- `application_detail` — Viewable by the applicant, any reviewer or admin, and the employer who owns the job.
- `job_applicants` — Employer-only. All applicants for a specific listing.

---

### reviews app

**Models:**

- `ReviewAssignment` — FK to `Application`, FK to `CustomUser` (reviewer). Fields: `status` (pending/in_progress/completed), `assigned_at`, `due_date`, `completed_at`. Unique together on `(application, reviewer)`. Method: `mark_complete()`.
- `ReviewNote` — FK to `ReviewAssignment`. Fields: `note`, `recommendation` (recommend/reject/hold/neutral), `is_final`.

**Key views:**

- `assign_review` — Admin-only. Creates a `ReviewAssignment` and sets the application status to `under_review`.
- `review_application` — Reviewer/admin. Adds a `ReviewNote`. If `is_final` is checked, calls `assignment.mark_complete()` and sets application status to `reviewed`.

---

### billing app

**Models:**

- `Plan` — Tiers: free, starter, professional, enterprise. Fields: `price_monthly`, `max_active_listings`, `featured_listings_per_month`, `stripe_price_id`.
- `EmployerSubscription` — OneToOne to `EmployerProfile`. Tracks `stripe_subscription_id`, `stripe_customer_id`, `status`, billing period dates. Properties: `is_active`, `is_expired`.

**Stripe integration:**

- Employers select a plan at `/billing/plans/`.
- Free plan: subscription is recorded locally with no Stripe interaction.
- Paid plans: server creates a `stripe.checkout.Session` and redirects the employer to Stripe-hosted checkout.
- Webhook at `/billing/webhook/` listens for `checkout.session.completed` and upserts the `EmployerSubscription` record. The webhook validates the Stripe signature using `STRIPE_WEBHOOK_SECRET`.
- `/billing/success/` is the post-payment return URL.

---

## URL Structure

| Pattern | Namespace | Description |
|---|---|---|
| `/` | `jobs` | Job listing homepage |
| `/jobs/post/` | `jobs` | Post a new job (employer) |
| `/jobs/<slug>/` | `jobs` | Job detail page |
| `/accounts/register/` | `accounts` | Registration |
| `/accounts/login/` | `accounts` | Login |
| `/accounts/logout/` | `accounts` | Logout (POST) |
| `/accounts/profile/` | `accounts` | Edit profile |
| `/apply/<job_slug>/` | `applications` | Submit an application |
| `/apply/mine/` | `applications` | My applications (job seeker) |
| `/apply/detail/<pk>/` | `applications` | Application detail |
| `/apply/job/<pk>/applicants/` | `applications` | Applicants for a job (employer) |
| `/reviews/` | `reviews` | Reviewer queue |
| `/reviews/assign/<pk>/` | `reviews` | Assign reviewer (admin) |
| `/reviews/<pk>/` | `reviews` | Review an application |
| `/billing/plans/` | `billing` | Pricing page |
| `/billing/checkout/<tier>/` | `billing` | Start Stripe checkout |
| `/billing/webhook/` | `billing` | Stripe webhook endpoint |
| `/billing/success/` | `billing` | Post-payment success page |
| `/dashboard/` | `dashboard` | Dashboard router (redirects by role) |
| `/admin/` | — | Django admin panel |

---

## Review Workflow

```
Job Seeker applies
       |
       v
Application created (status: pending)
       |
       v
Admin views unassigned applications on dashboard
       |
       v
Admin assigns reviewer via /reviews/assign/<application_pk>/
       |
       v
Application status -> under_review
ReviewAssignment created (status: pending)
       |
       v
Reviewer sees assignment in their queue
       |
       v
Reviewer opens application, writes ReviewNote(s)
       |
       v
Reviewer marks a note as final
       |
       v
ReviewAssignment status -> completed
Application status -> reviewed
       |
       v
Admin or employer can view recommendation
```

---

## Billing and Subscriptions

**Plans seeded at startup:**

| Tier | Price | Max Active Listings | Featured/Month |
|---|---|---|---|
| Free | $0 | 1 | 0 |
| Starter | $29/mo | 5 | 1 |
| Professional | $79/mo | 20 | 5 |

Seed command:

```bash
python manage.py shell -c "
from apps.billing.models import Plan
Plan.objects.get_or_create(tier='free', defaults={'name':'Free','price_monthly':0,'max_active_listings':1,'featured_listings_per_month':0})
Plan.objects.get_or_create(tier='starter', defaults={'name':'Starter','price_monthly':29,'max_active_listings':5,'featured_listings_per_month':1})
Plan.objects.get_or_create(tier='professional', defaults={'name':'Professional','price_monthly':79,'max_active_listings':20,'featured_listings_per_month':5})
"
```

For Stripe webhooks in local development, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/billing/webhook/
```

---

## Frontend

- Bootstrap 5.3 via CDN. No build pipeline required.
- Dark/light theme toggle in the navbar. Preference saved in `localStorage`. Applied before first paint to avoid flash.
- All forms use `django-crispy-forms` with the `crispy-bootstrap5` template pack.
- `static/css/main.css` — custom CSS variables, dark mode card/table overrides, form focus states.
- `static/js/main.js` — Django message level mapping, auto-dismiss success alerts, theme toggle logic.

---

## Production Deployment

### First-time VPS setup

```bash
# On the server as root:
bash deploy/setup.sh
```

The setup script handles: system packages, Python virtualenv, database creation, migrations, static file collection, systemd service for Gunicorn, and Nginx config symlink.

### SSL

```bash
sudo certbot --nginx -d your-domain.com
```

### Gunicorn

Managed by systemd via `deploy/gunicorn.service`. Runs 4 sync workers bound to `127.0.0.1:8000`.

```bash
sudo systemctl start rejobs
sudo systemctl enable rejobs
sudo systemctl status rejobs
```

### Nginx

Config at `deploy/nginx.conf`. Terminates SSL, serves `/static/` and `/media/` directly, proxies all other traffic to Gunicorn. Uploaded media files are served with `Content-Disposition: attachment` to prevent execution.

### Collecting static files

```bash
python manage.py collectstatic --noinput
```

Output goes to `staticfiles/` (served by WhiteNoise in the app, or Nginx directly in production).

---

## Running Tests

```bash
python manage.py test apps
```

Test files are located at `apps/<name>/tests.py` in each app.
