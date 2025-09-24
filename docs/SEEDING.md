# Data Seeding Guide

This document explains how to seed your application with realistic test data using various scalable approaches.

## Overview

The application provides multiple seeding strategies:

1. **Django Management Commands** - For development and testing
2. **Docker-based Seeding** - For production and containerized environments
3. **Data Export/Import** - For backup and restore operations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Basic Seeding (Development)

```bash
# Seed with default data (100 records each)
python manage.py seed_data

# Seed with custom amounts
python manage.py seed_data --companies=50 --users=200 --jobs=500

# Reset and seed (WARNING: Deletes all data)
python manage.py seed_data --reset
```

### 3. Production-like Seeding

```bash
# Seed with realistic, interconnected data
python manage.py seed_production_data --companies=50 --users=200 --jobs=500

# Reset and seed production data
python manage.py seed_production_data --reset
```

## Management Commands

### `seed_data`

Basic seeding command with configurable amounts.

**Usage:**
```bash
python manage.py seed_data [options]
```

**Options:**
- `--reset`: Delete all existing data before seeding
- `--sample-size`: Number of records for each model (default: 100)
- `--companies`: Number of companies to create (default: 20)
- `--users`: Number of users to create (default: 50)

**Example:**
```bash
python manage.py seed_data --reset --companies=100 --users=500 --sample-size=200
```

### `seed_production_data`

Advanced seeding with realistic, interconnected data.

**Usage:**
```bash
python manage.py seed_production_data [options]
```

**Options:**
- `--reset`: Delete all existing data before seeding
- `--companies`: Number of companies to create (default: 50)
- `--users`: Number of users to create (default: 200)
- `--jobs`: Number of jobs to create (default: 500)

**Features:**
- Realistic skill categories and relationships
- Tech-focused companies and job postings
- Proper user-skill and job-skill relationships
- Geographic distribution across major tech cities

### `export_data`

Export application data to JSON files for backup.

**Usage:**
```bash
python manage.py export_data [options]
```

**Options:**
- `--output-dir`: Directory to save exported data (default: ./data_exports)
- `--models`: Specific models to export (e.g., user.User company.Company)

**Example:**
```bash
python manage.py export_data --output-dir=./backups --models=user.User company.Company
```

## Docker-based Seeding

### Using Docker Compose

```bash
# Start services and seed data
docker-compose --profile seed up

# Reset and seed data
RESET_DATA=true docker-compose --profile seed up

# Seed data only (services already running)
docker-compose run --rm seed
```

### Manual Docker Seeding

```bash
# Build the image
docker build -t alx-app .

# Run seeding container
docker run --rm --env-file .env \
  --network host \
  alx-app /docker/seed-data.sh
```

## Data Structure

### Skills
- **Programming Languages**: Python, JavaScript, Java, TypeScript, Go, Rust, etc.
- **Frameworks**: Django, React, FastAPI, Spring Boot, etc.
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, etc.
- **Cloud & DevOps**: AWS, Docker, Kubernetes, Terraform, etc.
- **Data Science**: Machine Learning, TensorFlow, PyTorch, etc.
- **Soft Skills**: Leadership, Communication, Project Management, etc.

### Companies
- Realistic company names and descriptions
- Various industries (Technology, Finance, Healthcare, etc.)
- Different sizes (Startup, Small, Medium, Large, Enterprise)
- Geographic distribution across major tech cities

### Users
- **Talent Users (70%)**: Developers, designers, data scientists
- **Recruiters (30%)**: HR professionals, hiring managers
- Realistic profiles with skills and experience

### Jobs
- Tech-focused job postings
- Various types (Full-time, Part-time, Contract, Internship)
- Experience levels (Entry, Mid, Senior, Lead, Principal)
- Realistic salary ranges and requirements

## Scalability Considerations

### 1. **Batch Processing**
- All seeding operations use database transactions
- Large datasets are processed in batches to avoid memory issues

### 2. **Memory Management**
- Faker library generates data on-demand
- No large data structures held in memory

### 3. **Database Optimization**
- Uses `get_or_create()` to avoid duplicates
- Proper foreign key relationships
- Indexed fields for performance

### 4. **Docker Optimization**
- Multi-stage builds for smaller images
- Volume mounts for persistent data
- Health checks for service dependencies

## Environment Variables

### Required
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

### Optional
- `RESET_DATA`: Set to "true" to reset data before seeding
- `DJANGO_DEBUG`: Set to "false" for production

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure database is running and accessible
   - Check connection parameters in environment variables

2. **Memory Issues with Large Datasets**
   - Reduce batch sizes in management commands
   - Use `--sample-size` parameter to limit data

3. **Docker Build Failures**
   - Check Dockerfile syntax
   - Ensure all dependencies are in requirements.txt

4. **Permission Errors**
   - Ensure seed-data.sh is executable: `chmod +x docker/seed-data.sh`

### Performance Tips

1. **For Large Datasets**
   - Use `seed_production_data` for better performance
   - Consider running seeding in background

2. **For Development**
   - Use smaller sample sizes for faster iteration
   - Use `--reset` sparingly to avoid data loss

3. **For Production**
   - Run seeding during maintenance windows
   - Monitor database performance during seeding

## Best Practices

1. **Always backup data before resetting**
2. **Use appropriate seeding command for your use case**
3. **Monitor database performance during large seeding operations**
4. **Test seeding in development before production**
5. **Use Docker profiles for different environments**

## Examples

### Development Setup
```bash
# Quick development setup
python manage.py seed_data --companies=10 --users=50 --sample-size=50
```

### Staging Environment
```bash
# Realistic staging data
python manage.py seed_production_data --companies=100 --users=500 --jobs=1000
```

### Production Seeding
```bash
# Docker-based production seeding
RESET_DATA=true docker-compose --profile seed up
```

### Data Backup
```bash
# Export all data
python manage.py export_data --output-dir=./backups/$(date +%Y%m%d)

# Export specific models
python manage.py export_data --models=user.User company.Company job.Job
```
