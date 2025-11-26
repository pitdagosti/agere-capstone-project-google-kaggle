#!/bin/bash
# setup_and_run.sh
# This script clones the repo, sets up a virtual environment, installs dependencies, and runs Streamlit

# --- 1. Clone repo ---
REPO_URL="https://github.com/pitdagosti/capstone-project-google-kaggle.git"
DIR_NAME="capstone-project-google-kaggle"

if [ ! -d "$DIR_NAME" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL"
else
    echo "Repository already exists, skipping clone."
fi

cd "$DIR_NAME" || exit

# --- 2. Create virtual environment ---
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
else
    echo "Virtual environment already exists."
fi

# --- 3. Activate virtual environment ---
echo "Activating virtual environment..."
source .venv/bin/activate

# --- 4. Install dependencies ---
echo "Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# --- 5. Download spaCy model ---
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# --- 6. Configure environment variables ---
if [ ! -f ".env" ]; then
    echo "Copying example .env file..."
    cp env.example .env
    echo "Please edit .env and add your GOOGLE_API_KEY"
fi

# --- 7. Test installation ---
echo "Testing installation..."
python -c "import streamlit; import google.adk; print('✅ Installation successful!')"

# --- 8. Run Streamlit app ---
echo "Running Streamlit..."
streamlit run main.py
