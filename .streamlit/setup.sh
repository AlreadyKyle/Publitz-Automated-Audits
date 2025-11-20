#!/bin/bash
# Setup script for Streamlit Cloud deployment
# This installs Playwright browsers

playwright install chromium
playwright install-deps chromium
