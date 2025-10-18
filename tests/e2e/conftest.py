"""
Playwright Test Fixtures for Dashboard E2E Testing

This file provides reusable pytest fixtures for end-to-end testing
of the Streamlit dashboard using Playwright.
"""

import pytest
import subprocess
import time
import requests
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def api_server(project_root):
    """
    Start the API server for testing.

    Starts the FastAPI backend server and ensures it's ready before tests run.
    Automatically stops the server after all tests complete.
    """
    # Start API server
    process = subprocess.Popen(
        ["python", "dashboard/api_server.py"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to be ready
    max_wait = 10  # seconds
    api_url = "http://127.0.0.1:8000"

    for _ in range(max_wait * 2):
        try:
            response = requests.get(f"{api_url}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("API server failed to start")

    yield api_url

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="session")
def dashboard_server(project_root, api_server):
    """
    Start the Streamlit dashboard for testing.

    Starts the dashboard and waits for it to be ready.
    Automatically stops after all tests complete.
    """
    # Start Streamlit dashboard
    process = subprocess.Popen(
        ["streamlit", "run", "dashboard/streamlit_dashboard.py",
         "--server.port=8501", "--server.headless=true"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for dashboard to be ready
    max_wait = 15  # seconds
    dashboard_url = "http://localhost:8501"

    for _ in range(max_wait * 2):
        try:
            response = requests.get(dashboard_url, timeout=1)
            if response.status_code == 200:
                time.sleep(2)  # Extra wait for Streamlit to fully initialize
                break
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("Dashboard server failed to start")

    yield dashboard_url

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="function")
def page(playwright, dashboard_server):
    """
    Create a new browser page for each test.

    Provides a fresh browser context for each test to avoid state pollution.
    Automatically cleans up after test completes.
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to dashboard
    page.goto(dashboard_server, wait_until="networkidle")

    yield page

    # Cleanup
    context.close()
    browser.close()


@pytest.fixture
def api_url(api_server):
    """Provide API URL to tests."""
    return api_server


@pytest.fixture
def dashboard_url(dashboard_server):
    """Provide dashboard URL to tests."""
    return dashboard_server
