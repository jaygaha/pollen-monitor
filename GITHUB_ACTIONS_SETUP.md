# GitHub Actions CI/CD Setup Guide

This guide will help you set up continuous integration and continuous deployment (CI/CD) for the Pollen Monitor project using GitHub Actions.

## Prerequisites

- A GitHub repository with the Pollen Monitor code
- AWS EC2 instance running the application (for CD)
- SSH access to the EC2 instance
- Repository admin access to configure secrets

## Overview

The CI/CD pipeline consists of two workflows:

1. **CI Workflow** (`ci.yml`): Runs on every push/PR to `main` branch
   - Linting with `ruff`
   - Testing with `pytest`
   - Coverage reporting

2. **CD Workflow** (`cd.yml`): Deploys to EC2 after successful CI
   - SSH connection to EC2
   - Code pull and dependency update

## Step 1: Repository Setup

Ensure your repository has the following structure:

```
.github/
  workflows/
    ci.yml
    cd.yml
```

The workflow files should already be present in your repository.

## Step 2: Configure GitHub Secrets

Navigate to your repository on GitHub.com and go to:
**Settings** → **Secrets and variables** → **Actions**

Add the following repository secrets:

### Required Secrets for CD

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EC2_HOST` | EC2 instance public IP or DNS name | `54.123.45.67` |
| `EC2_USER` | SSH username | `ubuntu` |
| `EC2_SSH_KEY` | Private SSH key (entire key) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `DEPLOY_PATH` | Absolute path to app directory on EC2 | `/home/ubuntu/pollen-monitor` |

### How to Generate SSH Key Pair

If you don't have an SSH key pair for your EC2 instance:

1. **On your local machine**:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

2. **Copy public key to EC2**:
   ```bash
   ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@YOUR_EC2_IP
   ```

3. **Get private key content**:
   ```bash
   cat ~/.ssh/id_rsa
   ```

4. **Add the entire private key content to `EC2_SSH_KEY` secret**

## Step 3: EC2 Instance Preparation

Ensure your EC2 instance is ready for deployment:

### Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip curl

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Clone Repository

```bash
git clone https://github.com/jaygaha/pollen-monitor.git
cd pollen-monitor
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
nano .env
```

### Initial Setup

```bash
# Install dependencies
uv sync

# Test the application
uv run python -m pollen_monitor.main
```

### Set Up Cron Job

```bash
# Edit crontab
crontab -e

# Add daily execution at 7:00 AM
0 7 * * * cd /home/ubuntu/pollen-monitor && /home/ubuntu/.local/bin/uv run python -m pollen_monitor.main
```

## Step 4: Test CI Pipeline

1. **Make a small change** to trigger CI:
   ```bash
   echo "# Test CI" >> README.md
   ```

2. **Commit and push**:
   ```bash
   git add README.md
   git commit -m "Test CI pipeline"
   git push origin main
   ```

3. **Check Actions tab** on GitHub to see CI running

## Step 5: Test CD Pipeline

After CI passes, the CD workflow will automatically run.

### Monitor Deployment

1. Go to **Actions** tab on GitHub
2. Click on the latest workflow run
3. Check the **deploy** job logs

### Verify Deployment

SSH into your EC2 instance and check:

```bash
cd /home/ubuntu/pollen-monitor
git log --oneline -5  # Should show latest commit
uv run python -c "import pollen_monitor; print('Import successful')"
```

## Step 6: Troubleshooting

### CI Issues

**Tests failing?**
- Check test output in Actions logs
- Run tests locally: `uv run pytest`
- Ensure all dependencies are in `pyproject.toml`

**Linting errors?**
- Run locally: `uv run ruff check`
- Fix formatting: `uv run ruff format`

### CD Issues

**SSH connection failing?**
- Verify `EC2_HOST` is correct and accessible
- Check `EC2_USER` matches your EC2 username
- Ensure SSH key is correctly formatted (no extra spaces/newlines)
- Test SSH manually: `ssh -i ~/.ssh/id_rsa ubuntu@YOUR_EC2_IP`

**Deployment script failing?**
- Check `DEPLOY_PATH` exists on EC2
- Ensure `uv` is installed and in PATH
- Verify repository permissions

**Application not running?**
- Check cron jobs: `crontab -l`
- Review logs: `tail -f pollen_system.log`
- Test manually: `uv run python -m pollen_monitor.main`

### Common Issues

1. **Permission denied (publickey)**:
   - SSH key not added to EC2
   - Wrong username in `EC2_USER`

2. **uv command not found**:
   - PATH not set correctly
   - uv not installed on EC2

3. **Git pull fails**:
   - Repository not cloned in `DEPLOY_PATH`
   - Permission issues with git

## Step 7: Monitoring and Maintenance

### Health Checks

- **CI Status**: Check badge in README
- **CD Status**: Monitor Actions tab for failures
- **Application Logs**: Check `pollen_system.log` on EC2
- **Database**: Verify `pollen_monitor.db` is being updated

### Updating Workflows

When modifying `.github/workflows/*.yml`:

1. Test changes on a feature branch
2. Merge to `main` after verification
3. Monitor first deployment

### Security Best Practices

- Rotate SSH keys regularly
- Use least-privilege IAM roles
- Keep secrets encrypted
- Monitor for unauthorized access

## Support

If you encounter issues:

1. Check GitHub Actions logs for detailed error messages
2. Review this guide for common solutions
3. Test components locally before pushing
4. Create an issue in the repository with error details

## Workflow Files Reference

### ci.yml
- Triggers: Push/PR to main
- Tools: uv, ruff, pytest, codecov

### cd.yml
- Triggers: Successful CI on main
- Actions: SSH deploy, dependency update

The workflows are designed to be minimal and reliable for this Python application.