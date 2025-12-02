### Mkaguzi

Internal Audit Management System

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app mkaguzi
```

### Dependencies

After installing the app, install the required Python dependencies:

#### Option 1: Using the installation script (Recommended)

```bash
cd apps/mkaguzi
./install_dependencies.sh
```

Or using Python:

```bash
cd apps/mkaguzi
python3 install_dependencies.py
```

#### Option 2: Manual installation

```bash
cd apps/mkaguzi
pip3 install -r requirements.txt
```

**Note:** Frappe framework is installed and managed by bench, so it's not included in requirements.txt.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/mkaguzi
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
