#!/bin/bash
# Navi Gym Environment Setup Script
# This script creates a virtual environment and installs all required dependencies

set -e  # Exit on any error

echo "🎌 Navi Gym Environment Setup"
echo "=" * 50

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Found Python $PYTHON_VERSION"

if [ "$(python3 -c "import sys; print(sys.version_info.major >= 3 and sys.version_info.minor >= 10)")" != "True" ]; then
    echo "❌ Python 3.10+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️ Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing core dependencies first..."
pip install numpy>=1.26.4 scipy>=1.7.0 torch>=2.0.0

echo "📚 Installing Genesis prerequisites..."
pip install trimesh>=3.9.0 Pillow>=8.0.0 pyyaml>=5.4.0 py-cpuinfo>=9.0.0 psutil>=7.0.0 taichi>=1.7.0 cython>=3.0.0

echo "📚 Installing remaining dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the VRM display:"
echo "  source venv/bin/activate"
echo "  python3 ichika_vrm_rigged_display_WORKING.py"
echo ""
echo "✅ Setup finished successfully!"
