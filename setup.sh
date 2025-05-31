#!/bin/bash

# ShortTune API Setup Script
echo "🎵 Configurando ShortTune API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Verificando versão do Python..."
python_version=$(python --version 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python_version" ]]; then
    print_error "Python não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

required_version="3.8"
if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]]; then
    print_status "Python $python_version encontrado ✓"
else
    print_error "Python $python_version não suportado. Mínimo: Python 3.8"
    exit 1
fi

# Check FFmpeg
print_status "Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1)
    print_status "FFmpeg encontrado ✓"
else
    print_warning "FFmpeg não encontrado. Instale FFmpeg para funcionalidade completa."
    echo "Windows: https://ffmpeg.org/download.html"
    echo "Ubuntu: sudo apt install ffmpeg"
    echo "macOS: brew install ffmpeg"
fi

# Create virtual environment
print_status "Criando ambiente virtual..."
if [[ ! -d "venv" ]]; then
    python -m venv venv
    print_status "Ambiente virtual criado ✓"
else
    print_status "Ambiente virtual já existe ✓"
fi

# Activate virtual environment
print_status "Ativando ambiente virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
print_status "Atualizando pip..."
pip install --upgrade pip

# Install dependencies
print_status "Instalando dependências..."
pip install -r requirements.txt

# Create directories
print_status "Criando diretórios necessários..."
mkdir -p temp logs

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_status "Criando arquivo .env..."
    cp .env.example .env
    print_warning "Edite o arquivo .env com suas configurações antes de executar a API."
else
    print_status "Arquivo .env já existe ✓"
fi

# Run tests
print_status "Executando testes básicos..."
python -m pytest tests/ -v --tb=short

if [[ $? -eq 0 ]]; then
    print_status "Testes passaram ✓"
else
    print_warning "Alguns testes falharam. Verifique a configuração."
fi

echo ""
print_status "🎉 Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Execute: python main.py"
echo "3. Acesse: http://localhost:8000/docs"
echo ""
echo "📚 Comandos úteis:"
echo "• Desenvolvimento: python main.py"
echo "• Testes: python -m pytest"
echo "• Docker: docker-compose up"
echo ""
print_status "Happy coding! 🚀"
