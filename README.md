# Mkaguzi - Internal Audit Management System

## Overview

Mkaguzi is a comprehensive Internal Audit Management System built on ERPNext/Frappe framework. It provides organizations with tools to manage internal audit processes, compliance tracking, risk assessment, and reporting.

## Features

- **Audit Trail Management:** Track all system changes with comprehensive audit trails
- **Compliance Tracking:** Monitor regulatory compliance with automated checks
- **Risk Assessment:** Identify and assess organizational risks
- **Audit Findings:** Track and manage audit findings and remediation
- **Advanced Reporting:** Generate comprehensive audit reports
- **Multi-Module Support:** Audit across financial, HR, inventory, and other modules

## Installation

```bash
# Navigate to your Frappe bench directory
cd /path/to/your/bench

# Get the app
bench get-app mkaguzi https://github.com/your-repo/mkaguzi.git

# Install the app
bench install-app mkaguzi

# Build assets
bench build

# Migrate database
bench migrate
```

## Configuration

After installation, configure the system:

Navigate to Audit Settings in Frappe Desk
Set up notification recipients
Configure sync intervals
Set up audit rules and triggers

## API Documentation

### Authentication
All API endpoints require Frappe session authentication or API key.

### Endpoints

#### System Status
```
GET /api/method/mkaguzi.api.audit_api.get_system_status
```
Get comprehensive system status information.

#### Get Audit Trail
```
GET /api/method/mkaguzi.api.audit_api.get_audit_trail
```
Parameters:
- `doctype` (optional): Filter by document type
- `docname` (optional): Filter by document name
- `limit` (default: 100): Maximum results
- `start` (default: 0): Pagination offset

#### Run Integrity Check
```
POST /api/method/mkaguzi.api.audit_api.run_integrity_check
```
Parameters:
- `check_type` (default: 'full'): 'full', 'data', or 'config'
- `target_module` (optional): Specific module to check

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
bench setup requirements --dev

# Enable developer mode
bench set-config developer_mode 1

# Run tests
bench run-tests --app mkaguzi
```

### Code Style
Follow PEP 8 for Python code
Use type hints for all public functions
Write docstrings for all classes and methods
Keep functions focused and modular

### Running Tests

```bash
# Run all tests
bench run-tests --app mkaguzi

# Run specific test module
bench run-tests --app mkaguzi --module mkaguzi.tests.test_security

# Run with coverage
bench run-tests --app mkaguzi --coverage
```

## Security Considerations

- All audit trail entries are immutable once created
- Deleted documents are archived before removal
- Sensitive information is sanitized in error messages
- SQL queries use whitelisted templates only
- Role-based access control for all operations

## License

MIT License - See LICENSE file for details

## Support

For support and documentation:

- Documentation: https://docs.mkaguzi.coale.tech
- Issues: https://github.com/your-repo/mkaguzi/issues
- Email: info@coale.tech
