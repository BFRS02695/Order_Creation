#!/bin/bash

# Setup script for installing and configuring Ollama with Llama 3 8B model
# This script will install Ollama and download the Llama 3 8B model
# for use with the invoice processing application

echo "=== Invoice to Order Processing System Setup ==="
echo "This script will install Ollama and the Llama 3 8B model"
echo "for local LLM processing of invoices."
echo ""

# Check operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Ollama on Linux..."
    
    # Install Ollama on Linux
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Check if installation was successful
    if ! command -v ollama &> /dev/null; then
        echo "Failed to install Ollama. Please visit https://ollama.com/download for manual installation."
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing Ollama on macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Ollama using Homebrew
    brew install ollama
    
    # Check if installation was successful
    if ! command -v ollama &> /dev/null; then
        echo "Failed to install Ollama. Please visit https://ollama.com/download for manual installation."
        exit 1
    fi
    
else
    echo "Unsupported operating system. Please visit https://ollama.com/download to manually install Ollama."
    echo "After installation, run: ollama pull llama3:8b"
    exit 1
fi

echo "Starting Ollama service..."
# Start Ollama service (if not already running)
if pgrep -x "ollama" > /dev/null; then
    echo "Ollama is already running."
else
    # Start Ollama in the background
    ollama serve &
    
    # Wait for Ollama to start
    echo "Waiting for Ollama to start..."
    sleep 5
fi

# Pull the Llama 3 8B model
echo "Downloading Llama 3 8B model (this may take a while)..."
ollama pull llama3:8b

# Check if model was downloaded successfully
if [ $? -eq 0 ]; then
    echo "Llama 3 8B model downloaded successfully."
else
    echo "Failed to download Llama 3 8B model. Please run 'ollama pull llama3:8b' manually."
    exit 1
fi

# Test the model
echo "Testing the Llama 3 8B model..."
echo "Testing connection to Llama 3 8B..." | ollama run llama3:8b

# Create virtual environment for Python
echo "Setting up Python virtual environment..."
python3 -m venv invoice_env
source invoice_env/bin/activate

# Install required Python packages
echo "Installing required Python packages..."
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo "You can now run the application with:"
echo "source invoice_env/bin/activate"
echo "python main.py"
echo ""
echo "The application will be available at: http://localhost:8000"
echo "API documentation is available at: http://localhost:8000/docs"
echo ""
echo "Make sure Ollama is running by checking: ollama ps"
echo "If Ollama is not running, start it with: ollama serve" 