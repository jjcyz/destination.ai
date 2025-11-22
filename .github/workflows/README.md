# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. `ci.yml` - Continuous Integration

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- **Backend Tests**: Runs pytest on Python 3.8, 3.9, 3.10, 3.11, and 3.12
  - Generates coverage reports
  - Uploads coverage to Codecov (from Python 3.11 run)
  - Uploads HTML coverage report as artifact

- **Frontend Lint**: Runs ESLint and TypeScript type checking
  - Ensures code quality and type safety

- **Frontend Build**: Builds the frontend application
  - Verifies the build succeeds
  - Uploads build artifacts

- **Test Summary**: Aggregates test results from all jobs

### 2. `deploy.yml` - Deployment

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**
- **Deploy Backend**: Runs tests then deploys backend (configure your deployment platform)
- **Deploy Frontend**: Builds and deploys frontend (configure your deployment platform)

**Note:** Deployment steps are placeholders. Configure your deployment platform (Vercel, Heroku, Railway, etc.) in the workflow file.

### 3. `code-quality.yml` - Code Quality Checks

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly schedule (Mondays at 00:00 UTC)

**Jobs:**
- **Backend Lint**: Runs code quality tools (Black, isort, Flake8, Pylint)
  - Currently disabled (commented out)
  - Uncomment when ready to enforce code style

## Setup

### 1. Codecov (Optional but Recommended)

1. Sign up at [codecov.io](https://codecov.io) with your GitHub account
2. Add your repository
3. Get your upload token (or use GitHub integration)
4. Add `CODECOV_TOKEN` to your repository secrets (if using token-based upload)

The workflow will automatically upload coverage reports.

### 2. Deployment Configuration

Edit `.github/workflows/deploy.yml` and configure your deployment platform:

**For Vercel:**
```yaml
- name: Deploy to Vercel
  uses: amondnet/vercel-action@v25
  with:
    vercel-token: ${{ secrets.VERCEL_TOKEN }}
    vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
    vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
    working-directory: ./frontend
```

**For Heroku:**
```yaml
- name: Deploy to Heroku
  uses: akhileshns/heroku-deploy@v3.12.12
  with:
    heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    heroku_app_name: "your-app-name"
    heroku_email: "your-email@example.com"
```

**For Railway:**
```yaml
- name: Deploy to Railway
  uses: bervProject/railway-deploy@v1.0.0
  with:
    railway_token: ${{ secrets.RAILWAY_TOKEN }}
    service: backend
```

### 3. Code Quality Tools (Optional)

To enable code quality checks, uncomment the steps in `code-quality.yml`:

1. Install tools: `pip install flake8 black isort mypy pylint`
2. Uncomment the linting steps in the workflow
3. Optionally create configuration files:
   - `.flake8` for Flake8
   - `pyproject.toml` for Black/isort
   - `.pylintrc` for Pylint

## Environment Variables

The CI workflows use `DEMO_MODE=true` for tests, so no API keys are required.

For deployment, add your API keys as GitHub Secrets:
- `GOOGLE_MAPS_API_KEY`
- `OPENWEATHER_API_KEY`
- `TRANSLINK_API_KEY`
- `LIME_API_KEY` (optional)

