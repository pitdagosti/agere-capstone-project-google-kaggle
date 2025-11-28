#!/bin/bash
# setup_and_run.sh
# This script clones the repo, sets up a virtual environment, installs dependencies, and runs Streamlit


# --- 1. Create virtual environment ---
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
else
    echo "Virtual environment already exists."
fi

# --- 2. Activate virtual environment ---
echo "Activating virtual environment..."
source .venv/bin/activate

# --- 3. Install dependencies ---
echo "Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# --- 4. Download spaCy model ---
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# --- 5. Configure environment variables ---
if [ ! -f ".env" ]; then
    echo "Copying example .env file..."
    cp env.example .env
    echo "Please edit .env and add your GOOGLE_API_KEY"
fi

# --- 6. Test installation ---
echo "Testing installation..."
python -c "import streamlit; import google.adk; print('✅ Installation successful!')"
