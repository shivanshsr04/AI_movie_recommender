#!/bin/bash
# AI Movie Recommender System - Quick Start Script
# Automates initial setup and deployment process

set -e  # Exit on error

echo "============================================================"
echo "🎬 AI MOVIE RECOMMENDER SYSTEM - QUICK START"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Check Python installation
print_info "Step 1: Checking Python installation..."
if ! command -v python &> /dev/null; then
    print_error "Python not found! Please install Python 3.8+"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION found"

# Step 2: Create virtual environment
print_info "Step 2: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
print_info "Step 3: Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    print_success "Virtual environment activated (Windows)"
else
    print_error "Could not activate virtual environment"
    exit 1
fi

# Step 4: Upgrade pip
print_info "Step 4: Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Step 5: Install dependencies
print_info "Step 5: Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 6: Check data files
print_info "Step 6: Checking data files..."
if [ ! -d "data/raw" ]; then
    mkdir -p data/raw
    print_success "Created data/raw directory"
fi

CSV_FILES=("movies_metadata.csv" "ratings_small.csv" "credits.csv" "keywords.csv")
MISSING_FILES=0

for file in "${CSV_FILES[@]}"; do
    if [ -f "data/raw/$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing $file - Place it in data/raw/"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    print_error "$MISSING_FILES CSV files are missing!"
    echo ""
    echo "Please place these files in 'data/raw/' directory:"
    echo "  - movies_metadata.csv"
    echo "  - ratings_small.csv"
    echo "  - credits.csv"
    echo "  - keywords.csv"
    exit 1
fi

# Step 7: Create directories
print_info "Step 7: Creating necessary directories..."
mkdir -p models
mkdir -p data/processed
mkdir -p notebooks
mkdir -p .streamlit
print_success "Directories created"

# Step 8: Train models
print_info "Step 8: Training recommendation models..."
print_info "This may take several minutes..."
python train_models.py

if [ $? -eq 0 ]; then
    print_success "Models trained successfully"
else
    print_error "Model training failed"
    exit 1
fi

# Step 9: Run Streamlit app
print_info "Step 9: Starting Streamlit application..."
echo ""
echo "============================================================"
echo "🚀 APPLICATION STARTING..."
echo "============================================================"
echo ""
echo "Your app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run streamlit_app.py