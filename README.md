# AETIS 2.0

A comprehensive system for anomaly detection and monitoring with integrated dashboard, machine learning models, and real-time data processing.

## Overview

AETIS 2.0 is a full-stack application designed to detect, analyze, and visualize anomalies in complex systems. It combines hardware integration, advanced machine learning models, and a responsive web dashboard to provide real-time insights into system behavior and anomalies.

## Project Structure

```
aetis-2.0/
├── dashboard/          # Web-based visualization and monitoring interface
├── detection/          # Core anomaly detection algorithms and logic
├── hardware/           # Hardware integration and sensor management
├── models/             # Pre-trained ML models and model utilities
├── scripts/            # Utility scripts for setup and maintenance
├── server/             # Backend API and data processing server
├── docker-compose.yml  # Container orchestration configuration
├── requirements.txt    # Python dependencies
└── .gitignore         # Git exclusion rules
```

## Key Components

### Dashboard

The user-facing web interface for monitoring and analyzing detected anomalies. Provides real-time visualization of system metrics, historical trends, and anomaly reports.

### Detection Engine

Core module handling anomaly detection logic. Processes incoming data and applies machine learning models to identify unusual patterns and potential issues.

### Hardware Integration

Manages connections to physical sensors and hardware devices. Handles data ingestion from various hardware sources and ensures reliable communication.

### ML Models

Collection of pre-trained machine learning models optimized for anomaly detection. Includes model loading, inference, and performance utilities.

### Server

Backend API built on Python. Handles data persistence, request processing, and coordination between frontend and detection components.

### Scripts

Utility scripts for system setup, database initialization, data processing, and maintenance tasks.

## Technology Stack

* **Backend**: Python

* **Database**: PostgreSQL with PostGIS extension (geospatial support)

* **Caching**: Redis

* **Containerization**: Docker & Docker Compose

* **Frontend**: Web-based dashboard (JavaScript/framework TBD)

## Getting Started

### Prerequisites

* Docker and Docker Compose

* Python 3.8+

* Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/pragati2809/aetis-2.0.git
cd aetis-2.0
```

20. Start the services using Docker Compose:

```bash
docker-compose up -d
```

This will start:

* Redis server on port 6379

* PostgreSQL database on port 5433

* Database name: `aetis`

* Default credentials: `postgres` / `admin1515`

* Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Update the following environment variables as needed:

* `POSTGRES_DB`: Database name (default: aetis)

* `POSTGRES_USER`: Database user (default: postgres)

* `POSTGRES_PASSWORD`: Database password (default: admin1515)

* Redis connection details for caching

## Development

### Running the Server

```bash
python -m server.main
```

### Running Detection

```bash
python -m detection.main
```

### Accessing the Dashboard

Navigate to the dashboard URL (typically `http://localhost:3000` or similar - check dashboard documentation for exact port).

### Database Access

* **Host**: localhost

* **Port**: 5433

* **Database**: aetis

* **User**: postgres

* **Password**: admin1515

## Project Status

**Current Version**: 2.0 (Final MVP) **Last Updated**: March 28, 2026

The project has reached MVP status with core functionality implemented across all major components.

## Architecture Highlights

* **Scalable Design**: Containerized services allow easy scaling

* **Real-time Processing**: Redis caching for fast data access

* **Geospatial Support**: PostGIS integration for location-based analysis

* **Modular Structure**: Clear separation of concerns between components

* **ML-Driven**: Advanced anomaly detection using trained models

## Contributing

To contribute to this project:

1. Create a feature branch

2. Make your changes

3. Test thoroughly

4. Submit a pull request with a clear description

## Database Schema

The PostgreSQL database includes PostGIS extensions for geospatial capabilities. Key tables are designed to support:

* Anomaly records and metadata

* Historical time-series data

* Hardware sensor information

* User interactions and alerts

## Deployment

For production deployment:

1. Update database credentials in `docker-compose.yml`

2. Configure environment variables for security

3. Set up persistent volumes for data durability

4. Configure appropriate network policies

5. Implement backup and recovery procedures

## Troubleshooting

### Database Connection Issues

* Verify PostgreSQL is running: `docker-compose ps`

* Check connection string and credentials

* Ensure port 5433 is not blocked

### Redis Connection Issues

* Verify Redis is running: `docker-compose ps`

* Check Redis is accessible on port 6379

### Missing Dependencies

* Reinstall Python packages: `pip install -r requirements.txt`

* Check Python version compatibility

## License

Check the repository for license information.

## Support

For issues, questions, or contributions, please refer to the GitHub repository: https://github.com/pragati2809/aetis-2.0

---

**Project Owner**: pragati2809 **Repository**: https://github.com/pragati2809/aetis-2.0
