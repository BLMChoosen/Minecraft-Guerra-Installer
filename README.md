# 🎮 Instalador Minecraft Guerra 2

Instalador moderno e intuitivo para o Modpack Minecraft Guerra 2 com interface gráfica responsiva e animada.

## ✨ Características

- 🎨 **Interface Moderna** - Design limpo e profissional usando CustomTkinter
- � **Atualização Inteligente** - Atualiza mods e configs mantendo seus saves, screenshots e opções
- �📊 **Barra de Progresso Visual** - Indicadores de passo com animações
- 🚀 **Instalação Automática** - Configure perfis automaticamente em múltiplos launchers
- 📦 **Múltiplas Versões** - Escolha entre Full, Intermediate ou Lightweight
- 🎯 **Launchers Suportados**:
  - **Pirata**: TLauncher, SKLauncher
  - **Original**: Modrinth App, CurseForge
  - **Manual**: Escolha sua própria pasta

## 📋 Requisitos

- Python 3.8 ou superior
- Windows 10/11
- Conexão com a internet

## 🔧 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/BLMChoosen/Minecraft-Guerra-Installer.git
cd Minecraft-Guerra-Installer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o instalador:
```bash
python Installer.py
```

## 📦 Dependências

- `customtkinter` - Interface moderna e responsiva
- `requests` - Download de arquivos
- `Pillow` - Processamento de imagens

## 🎯 Como Usar

1. **Bem-vindo** - Leia a introdução
2. **Tipo de Licença** - Escolha entre Original ou Pirata
3. **Launcher** - Selecione seu launcher favorito
4. **Versão** - Escolha entre Full, Intermediate ou Lightweight
5. **Instalação** - Aguarde o download e configuração automática

## 🎨 Interface

A interface utiliza CustomTkinter para proporcionar:
- Animações suaves entre telas
- Cards visuais com informações claras
- Indicadores de progresso por passo
- Feedback visual em tempo real
- Design responsivo e moderno

## 🔄 Funcionalidades Técnicas

- Instalação isolada por versão (permite instalar múltiplas versões no mesmo launcher)
- Configuração automática de perfis SKLauncher (JSON)
- Configuração automática de perfis Modrinth (SQLite)
- Fechamento automático de processos conflitantes
- Download com barra de progresso em tempo real
- Extração com feedback visual
- Preservação de dados do usuário (saves, screenshots, options.txt) durante atualizações

## 🔨 Compilando para .exe

Para gerar um executável standalone:

1. Instale o PyInstaller:
```bash
pip install pyinstaller
```

2. Execute o comando de build (ajuste o caminho do customtkinter se necessário):
```bash
python -m PyInstaller --noconsole --onefile --clean --add-data "CAMINHO_DO_PYTHON\Lib\site-packages\customtkinter;customtkinter" Installer.py
```

## 🛠️ Desenvolvimento

Desenvolvido por **BLMChoosen** em 2025

## 📄 Licença

Este projeto é de código aberto e está disponível para uso pessoal e comercial.

---

**Feito com ❤️ para o Minecraft Guerra 2**
