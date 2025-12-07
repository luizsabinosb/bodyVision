# BodyVision - Sistema de Análise de Poses de Fisiculturismo

Sistema de análise de poses de fisiculturismo em tempo real usando visão computacional com MediaPipe e OpenCV.

## 🎯 Poses Suportadas

- **Duplo Bíceps (Frente)** - Tecla `1`
- **Enquadramento** - Tecla `2`
- **Duplo Bíceps de Costas** - Tecla `3`
- **Side Chest** - Tecla `4`
- **Most Muscular** - Tecla `5`

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Câmera conectada ao computador
- macOS, Linux ou Windows

## 🚀 Como Executar

### ⚡ Método Rápido (macOS/Linux)

O projeto possui um script de execução automática. Basta executar:

```bash
./run.sh
```

### 📝 Método Manual

#### Opção 1: Usando o ambiente virtual existente (venv)

O projeto já possui um ambiente virtual configurado com todas as dependências instaladas. Para ativá-lo e executar:

**macOS/Linux:**
```bash
# Navegar até a pasta do projeto
cd /caminho/ate/diretorio/BodyVision

# Ativar o ambiente virtual
source venv/bin/activate

# Executar o programa
python BodyVision.py

# Quando terminar, desativar o ambiente (opcional)
deactivate
```

**Windows:**
```bash
# Navegar até a pasta do projeto
cd C:\caminho\para\BodyVision

# Ativar o ambiente virtual
venv\Scripts\activate

# Executar o programa
python BodyVision.py
```

#### Opção 2: Criar um novo ambiente virtual

Se preferir criar um novo ambiente virtual:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar o programa
python BodyVision.py
```

## 🎮 Controles

- **Tecla `Q`**: Sair do programa
- **Tecla `1`**: Modo Enquadramento
- **Tecla `2`**: Modo Duplo Bíceps (Frente)
- **Tecla `3`**: Modo Duplo Bíceps de Costas
- **Tecla `4`**: Modo Side Chest
- **Tecla `5`**: Modo Most Muscular

## 📝 Funcionalidades

O sistema analisa sua pose em tempo real e fornece feedback sobre:
- Posição correta dos braços e ângulos
- Alinhamento e simetria
- Altura dos cotovelos
- Postura geral
- Expansão do tórax e dorsais

## 🔧 Solução de Problemas

### Câmera não é detectada
- Verifique se a câmera está conectada e funcionando
- Tente fechar outros aplicativos que possam estar usando a câmera

### Erro ao importar bibliotecas
- Certifique-se de que o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

### Performance lenta
- Certifique-se de ter uma boa iluminação
- Fique a uma distância adequada da câmera (1-2 metros)
- Feche outros aplicativos que possam estar consumindo recursos

## 📦 Dependências

- `opencv-python`: Processamento de imagens e vídeo
- `mediapipe`: Detecção de poses humanas
- `numpy`: Operações matemáticas e arrays

## 📁 Estrutura do Projeto

```
BodyVision/
├── BodyVision.py          # Arquivo principal e classe da aplicação
├── pose_evaluator.py      # Classe PoseDetector e métodos de avaliação de poses
├── ui_helpers.py          # Funções auxiliares para desenho de interface
├── ui_renderer.py         # Funções de renderização da UI (painéis, feedback)
├── camera_utils.py        # Utilitários para gerenciamento de câmera
├── requirements.txt       # Dependências do projeto
├── run.sh                 # Script de execução rápida
└── README.md              # Documentação do projeto
```

### Descrição dos Módulos

- **BodyVision.py**: Classe principal `BodyVisionApp` que gerencia o loop da aplicação e coordena os módulos
- **pose_evaluator.py**: Contém a classe `PoseDetector` com métodos estáticos para avaliar cada tipo de pose
- **ui_helpers.py**: Funções básicas de desenho (painéis, gradientes, barras de progresso, separadores)
- **ui_renderer.py**: Funções de alto nível para renderizar componentes completos da interface
- **camera_utils.py**: Funções para detectar e configurar câmeras disponíveis

