"""
Instalador do Modpack Minecraft Guerra 2
=========================================

Este script fornece uma interface gráfica (GUI) para instalação automatizada
do modpack Minecraft Guerra 2 em diferentes launchers.

Características:
- Suporte para múltiplos launchers (TLauncher, SKLauncher, Modrinth, CurseForge)
- Três versões do modpack (Full, Intermediate, Lightweight)
- Download e extração automatizada
- Configuração automática de perfis de launcher
- Interface moderna com animações suaves
- Tema dark/light alternável

Dependências:
- customtkinter (pip install customtkinter)
- requests (pip install requests)
- Pillow (pip install Pillow)

Autor: BLMChoosen
Data: 2025
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
import os
import zipfile
import tempfile
import json
import datetime
import sqlite3

# Verifica e importa bibliotecas necessárias
try:
    import customtkinter as ctk
except ImportError:
    messagebox.showerror("Erro", "A biblioteca 'customtkinter' não está instalada.\nExecute: pip install customtkinter")
    exit()

try:
    import requests
except ImportError:
    messagebox.showerror("Erro", "A biblioteca 'requests' não está instalada.\nExecute: pip install requests")
    exit()

# Configuração global do CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class ModpackWizard(ctk.CTk):
    """
    Classe principal do instalador wizard do Modpack Minecraft Guerra 2.
    
    Herda de ctk.CTk para criar a janela principal da aplicação moderna.
    Implementa um wizard de 5 passos com animações e interface responsiva.
    """
    
    def __init__(self):
        """Inicializa a janela principal e configura os componentes da interface."""
        super().__init__()

        # Configurações da janela principal
        self.title("Instalador do Modpack Minecraft Guerra 2")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Centraliza a janela na tela
        self.center_window()
        
        # Ícone da janela (se disponível)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        # Centraliza a janela na tela
        self.center_window()
        
        # Ícone da janela (se disponível)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        # ==========================================
        # CONFIGURAÇÃO DE URLS DE DOWNLOAD
        # ==========================================
        # Dicionário contendo URLs de download para cada combinação de launcher e versão
        # Estrutura: {launcher: {versão: url}}
        self.DOWNLOAD_URLS = {
            "tlauncher": {
                "full": "https://api.bloodmoonbr.com/downloads/Guerra-2-Full.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Guerra-2-Intermediate.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Guerra-2-Light.zip"
            },
            "sklauncher": {
                "full": "https://api.bloodmoonbr.com/downloads/Guerra-2-Full.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Guerra-2-Intermediate.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Guerra-2-Light.zip"
            },
            "modrinth": {
                "full": "https://api.bloodmoonbr.com/downloads/Guerra-2-Full.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Guerra-2-Intermediate.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Guerra-2-Light.zip"
            },
            "curseforge": {
                "full": "https://api.bloodmoonbr.com/downloads/Guerra-2-Full.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Guerra-2-Intermediate.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Guerra-2-Light.zip"
            },
            "manual": {
                "full": "https://api.bloodmoonbr.com/downloads/Guerra-2-Full.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Guerra-2-Intermediate.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Guerra-2-Light.zip"
            }
        }

        # ==========================================
        # VARIÁVEIS DE CONTROLE DO WIZARD
        # ==========================================
        self.current_step = 1  # Passo atual do wizard (1-5)
        
        # Variáveis Tkinter para armazenar escolhas do usuário
        self.var_license_type = tk.StringVar(value="")   # "original" ou "pirata"
        self.var_launcher = tk.StringVar(value="")       # Launcher selecionado
        self.var_version = tk.StringVar(value="full")    # Versão do modpack (full/intermediate/lightweight)
        self.var_install_path = tk.StringVar(value="")   # Caminho de instalação manual
        
        # Animação
        self.animation_running = False

        # ==========================================
        # LAYOUT PRINCIPAL
        # ==========================================
        # Container principal com padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header com título e barra de progresso
        self.create_header()
        
        # Frame de conteúdo (onde as telas são renderizadas)
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both", pady=20)
        
        # Footer com botões de navegação
        self.create_footer()
        
        # Mostra a primeira tela
        self.show_step(1)
    
    def center_window(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        width = 800
        height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_header(self):
        """Cria o cabeçalho com título e indicador de progresso."""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Título principal
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="⚔️ Minecraft Guerra 2",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#1f538d", "#3a7ebf")
        )
        self.title_label.pack(pady=(0, 15))
        
        # Frame para indicadores de passo
        self.progress_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x")
        
        # Cria 5 indicadores de passo
        self.step_indicators = []
        step_names = ["Bem-vindo", "Licença", "Launcher", "Versão", "Instalação"]
        
        for i in range(5):
            step_container = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
            step_container.pack(side="left", expand=True, fill="x", padx=2)
            
            # Círculo indicador
            indicator = ctk.CTkFrame(
                step_container,
                width=40,
                height=40,
                corner_radius=20,
                fg_color=("gray70", "gray30")
            )
            indicator.pack(pady=(0, 5))
            
            # Número do passo
            num_label = ctk.CTkLabel(
                indicator,
                text=str(i + 1),
                font=ctk.CTkFont(size=16, weight="bold")
            )
            num_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Nome do passo
            name_label = ctk.CTkLabel(
                step_container,
                text=step_names[i],
                font=ctk.CTkFont(size=10)
            )
            name_label.pack()
            
            self.step_indicators.append({
                'container': step_container,
                'indicator': indicator,
                'number': num_label,
                'name': name_label
            })
    
    def create_footer(self):
        """Cria o rodapé com botões de navegação."""
        footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom")
        
        # Botão Cancelar (esquerda)
        self.btn_cancel = ctk.CTkButton(
            footer_frame,
            text="✖ Cancelar",
            command=self.on_cancel,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_cancel.pack(side="left")
        
        # Botão Anterior (direita)
        self.btn_prev = ctk.CTkButton(
            footer_frame,
            text="◀ Anterior",
            command=self.go_prev,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_prev.pack(side="right", padx=(10, 0))
        
        # Botão Próximo (direita)
        self.btn_next = ctk.CTkButton(
            footer_frame,
            text="Próximo ▶",
            command=self.go_next,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_next.pack(side="right")    # ==========================================
    # MÉTODOS DE NAVEGAÇÃO DO WIZARD
    # ==========================================
    
    def clear_content(self):
        """Remove todos os widgets do frame de conteúdo para preparar o próximo passo."""
        for widget in self.content_frame.winfo_children(): 
            widget.destroy()
    
    def update_step_indicators(self):
        """Atualiza os indicadores visuais de progresso."""
        for i, indicator_set in enumerate(self.step_indicators):
            step_num = i + 1
            
            if step_num < self.current_step:
                # Passo concluído - verde
                indicator_set['indicator'].configure(fg_color=("#2fa572", "#2fa572"))
                indicator_set['number'].configure(text="✓")
            elif step_num == self.current_step:
                # Passo atual - azul brilhante
                indicator_set['indicator'].configure(fg_color=("#1f538d",   "#3a7ebf"))
                indicator_set['number'].configure(text=str(step_num))
            else:
                # Passo futuro - cinza
                indicator_set['indicator'].configure(fg_color=("gray70", "gray30"))
                indicator_set['number'].configure(text=str(step_num))

    def update_nav_buttons(self):
        """Atualiza o estado dos botões de navegação baseado no passo atual."""
        # Desabilita botão "Anterior" no primeiro passo
        if self.current_step == 1: 
            self.btn_prev.configure(state="disabled")
        else: 
            self.btn_prev.configure(state="normal")

        # No último passo (instalação concluída), altera botão para "Fechar"
        if self.current_step == 5:
            self.btn_next.configure(text="🏁 Fechar", command=self.quit)
            self.btn_prev.configure(state="disabled")
            self.btn_cancel.configure(state="disabled")
        else:
            self.btn_next.configure(text="Próximo ▶", command=self.go_next)
            self.btn_cancel.configure(state="normal")

    def go_next(self):
        """
        Avança para o próximo passo do wizard.
        Realiza validações antes de avançar e inicia a instalação no passo 4.
        """
        # ==========================================
        # VALIDAÇÕES POR PASSO
        # ==========================================
        
        # Passo 2: Valida seleção do tipo de licença
        if self.current_step == 2 and not self.var_license_type.get():
            messagebox.showwarning("Atenção", "Selecione uma opção de licença.")
            return
        
        # Passo 3: Valida seleção do launcher e pasta (se manual)
        if self.current_step == 3:
            if not self.var_launcher.get():
                messagebox.showwarning("Atenção", "Selecione um launcher.")
                return
            if "manual" in self.var_launcher.get() and not self.var_install_path.get():
                messagebox.showwarning("Atenção", "Para instalação manual, selecione uma pasta.")
                return

        # Passo 4: Inicia processo de instalação em thread separada
        if self.current_step == 4:
            self.current_step += 1
            self.show_step(5)
            threading.Thread(target=self.run_installation_logic, daemon=True).start()
            return

        # Avança para o próximo passo
        if self.current_step < 5:
            self.current_step += 1
            self.show_step(self.current_step)

    def go_prev(self):
        """Volta para o passo anterior do wizard."""
        if self.current_step > 1:
            self.current_step -= 1
            self.show_step(self.current_step)

    def on_cancel(self):
        """Cancela a instalação após confirmação do usuário."""
        if messagebox.askyesno("Cancelar", "Sair da instalação?"):
            self.quit()

    def select_folder(self):
        """Abre diálogo para seleção de pasta de instalação manual."""
        f = filedialog.askdirectory()
        if f: 
            self.var_install_path.set(f)

    def show_step(self, step):
        """
        Exibe a tela correspondente ao passo especificado.
        
        Args:
            step (int): Número do passo (1-5)
        """
        self.clear_content()
        self.update_nav_buttons()
        self.update_step_indicators()
        
        # Fade in animation
        self.content_frame.configure(fg_color="transparent")
        
        # Renderiza a tela correspondente ao passo
        if step == 1: self.screen_welcome()
        elif step == 2: self.screen_license_type()
        elif step == 3: self.screen_launcher_select()
        elif step == 4: self.screen_version_select()
        elif step == 5: self.screen_installing_finished()

    def screen_welcome(self):
        """Tela 1: Boas-vindas ao instalador."""
        # Container centralizado
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ícone/Emoji grande
        icon_label = ctk.CTkLabel(
            container,
            text="🎮",
            font=ctk.CTkFont(size=80)
        )
        icon_label.pack(pady=(0, 20))
        
        # Título de boas-vindas
        welcome_label = ctk.CTkLabel(
            container,
            text="Bem-vindo ao Instalador",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        welcome_label.pack(pady=(0, 10))
        
        # Descrição
        desc_label = ctk.CTkLabel(
            container,
            text="Este assistente irá guiá-lo através da instalação\ndo Modpack Minecraft Guerra 2 de forma rápida e fácil.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        desc_label.pack(pady=(0, 30))
        
        # Features
        features_frame = ctk.CTkFrame(container, fg_color=("gray85", "gray20"), corner_radius=10)
        features_frame.pack(fill="x", padx=20)
        
        features = [
            "✓ Instalação automatizada",
            "✓ Múltiplos launchers suportados",
            "✓ Configuração de perfis automática"
        ]
        
        for feature in features:
            f_label = ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            f_label.pack(pady=8, padx=20, anchor="w")

    def screen_license_type(self):
        """Tela 2: Seleção do tipo de licença (Original/Pirata)."""
        # Container centralizado
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="Tipo de Minecraft",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=(0, 40))
        
        # Opções em cards
        options_frame = ctk.CTkFrame(container, fg_color="transparent")
        options_frame.pack()
        
        # Card Original
        original_card = ctk.CTkFrame(options_frame, corner_radius=15, fg_color=("gray85", "gray20"))
        original_card.pack(pady=10, padx=20, fill="x")
        
        original_radio = ctk.CTkRadioButton(
            original_card,
            text="",
            variable=self.var_license_type,
            value="original",
            font=ctk.CTkFont(size=16)
        )
        original_radio.pack(side="left", padx=20, pady=20)
        
        original_content = ctk.CTkFrame(original_card, fg_color="transparent")
        original_content.pack(side="left", fill="x", expand=True, pady=20, padx=(0, 20))
        
        ctk.CTkLabel(
            original_content,
            text="🎯 Original (Premium)",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            original_content,
            text="Para contas oficiais da Mojang/Microsoft",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))
        
        # Card Pirata
        pirata_card = ctk.CTkFrame(options_frame, corner_radius=15, fg_color=("gray85", "gray20"))
        pirata_card.pack(pady=10, padx=20, fill="x")
        
        pirata_radio = ctk.CTkRadioButton(
            pirata_card,
            text="",
            variable=self.var_license_type,
            value="pirata",
            font=ctk.CTkFont(size=16)
        )
        pirata_radio.pack(side="left", padx=20, pady=20)
        
        pirata_content = ctk.CTkFrame(pirata_card, fg_color="transparent")
        pirata_content.pack(side="left", fill="x", expand=True, pady=20, padx=(0, 20))
        
        ctk.CTkLabel(
            pirata_content,
            text="🏴‍☠️ Pirata (Alternativo)",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            pirata_content,
            text="Para launchers não-oficiais (TLauncher, SKLauncher)",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

    def screen_launcher_select(self):
        """
        Tela 3: Seleção do launcher.
        Opções variam conforme tipo de licença selecionado anteriormente.
        """
        # Container centralizado
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="Selecione o Launcher",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        license_type = self.var_license_type.get()
        
        # Define opções de launcher baseado no tipo de licença
        if license_type == "pirata":
            options = [
                ("🚀 TLauncher", "tlauncher", "Launcher popular para Minecraft pirata"),
                ("⚡ SKLauncher", "sklauncher", "Launcher leve e rápido"),
                ("📁 Manual", "manual_pirata", "Escolha sua própria pasta")
            ]
        else:  # original
            options = [
                ("🟣 Modrinth App", "modrinth", "Launcher moderno e open-source"),
                ("🔥 CurseForge", "curseforge", "Launcher da Overwolf/CurseForge"),
                ("📁 Manual", "manual_original", "Escolha sua própria pasta")
            ]
        
        # Cards de opções
        for emoji_title, value, description in options:
            card = ctk.CTkFrame(container, corner_radius=15, fg_color=("gray85", "gray20"))
            card.pack(pady=8, padx=20, fill="x")
            
            radio = ctk.CTkRadioButton(
                card,
                text="",
                variable=self.var_launcher,
                value=value,
                command=self.toggle_manual,
                font=ctk.CTkFont(size=16)
            )
            radio.pack(side="left", padx=20, pady=15)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(side="left", fill="x", expand=True, pady=15, padx=(0, 20))
            
            ctk.CTkLabel(
                content,
                text=emoji_title,
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                content,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))
        
        # Frame para seleção de pasta manual
        self.manual_frame = ctk.CTkFrame(container, corner_radius=10, fg_color=("gray90", "gray15"))
        self.manual_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        manual_label = ctk.CTkLabel(
            self.manual_frame,
            text="📂 Pasta de instalação:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        manual_label.pack(side="left", padx=15, pady=12)
        
        self.path_entry = ctk.CTkEntry(
            self.manual_frame,
            textvariable=self.var_install_path,
            placeholder_text="Selecione uma pasta...",
            width=300,
            height=35
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=12)
        
        self.browse_btn = ctk.CTkButton(
            self.manual_frame,
            text="Procurar",
            command=self.select_folder,
            width=100,
            height=35
        )
        self.browse_btn.pack(side="left", padx=(0, 15), pady=12)
        
        self.toggle_manual()

    def toggle_manual(self):
        """Habilita/desabilita controles de seleção de pasta conforme opção de launcher."""
        # Habilita controles apenas se opção manual foi selecionada
        if "manual" in self.var_launcher.get():
            self.manual_frame.configure(fg_color=("gray90", "gray15"))
            self.path_entry.configure(state="normal")
            self.browse_btn.configure(state="normal")
        else:
            self.manual_frame.configure(fg_color=("gray80", "gray25"))
            self.path_entry.configure(state="disabled")
            self.browse_btn.configure(state="disabled")

    def screen_version_select(self):
        """Tela 4: Seleção da versão do modpack (Full/Intermediate/Lightweight)."""
        # Container centralizado
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="Versão do Modpack",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # Opções de versão
        versions = [
            ("💪 Full (Pesado)", "full", "Todos os mods e recursos", "~550MB", "#e74c3c"),
            ("⚖️ Intermediate (Médio)", "intermediate", "Balanceado para maioria dos PCs", "~300MB", "#f39c12"),
            ("🪶 Lightweight (Leve)", "lightweight", "Otimizado para PCs mais fracos", "~150MB", "#2ecc71")
        ]
        
        for emoji_title, value, description, size, color in versions:
            card = ctk.CTkFrame(container, corner_radius=15, fg_color=("gray85", "gray20"))
            card.pack(pady=8, padx=20, fill="x")
            
            radio = ctk.CTkRadioButton(
                card,
                text="",
                variable=self.var_version,
                value=value,
                font=ctk.CTkFont(size=16)
            )
            radio.pack(side="left", padx=20, pady=20)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(side="left", fill="x", expand=True, pady=20)
            
            ctk.CTkLabel(
                content,
                text=emoji_title,
                font=ctk.CTkFont(size=17, weight="bold"),
                anchor="w"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                content,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))
            
            # Badge de tamanho
            size_badge = ctk.CTkLabel(
                card,
                text=size,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=color,
                corner_radius=8,
                padx=12,
                pady=6
            )
            size_badge.pack(side="right", padx=20)

    def screen_installing_finished(self):
        """Tela 5: Exibe progresso da instalação e resultado final."""
        # Container centralizado
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ícone animado
        self.status_icon = ctk.CTkLabel(
            container,
            text="⏳",
            font=ctk.CTkFont(size=60)
        )
        self.status_icon.pack(pady=(0, 20))
        
        # Título de status
        self.lbl_status_title = ctk.CTkLabel(
            container,
            text="Preparando instalação...",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_status_title.pack(pady=(0, 20))
        
        # Barra de progresso moderna
        self.progress = ctk.CTkProgressBar(
            container,
            width=500,
            height=20,
            corner_radius=10
        )
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        # Label de detalhes
        self.lbl_details = ctk.CTkLabel(
            container,
            text="Iniciando...",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.lbl_details.pack(pady=(0, 10))
        
        # Label de porcentagem
        self.lbl_percentage = ctk.CTkLabel(
            container,
            text="0%",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_percentage.pack()

    # ==========================================
    # GERENCIAMENTO DE DIRETÓRIOS E CONFIGURAÇÃO
    # ==========================================
    
    def get_version_suffix(self):
        """
        Retorna o sufixo do nome baseado na versão selecionada.
        
        Returns:
            str: Sufixo formatado (ex: 'Full', 'Intermediate', 'Lightweight')
        """
        version_map = {
            "full": "Full",
            "intermediate": "Intermediate",
            "lightweight": "Lightweight"
        }
        return version_map.get(self.var_version.get(), "Full")
    
    def get_profile_name(self):
        """
        Retorna o nome completo do perfil incluindo a versão.
        
        Returns:
            str: Nome do perfil (ex: 'Minecraft Guerra 2 Full')
        """
        return f"Minecraft Guerra 2 {self.get_version_suffix()}"
    
    def get_folder_name(self):
        """
        Retorna o nome da pasta de instalação incluindo a versão.
        
        Returns:
            str: Nome da pasta (ex: 'Minecraft Guerra 2 Full')
        """
        return f"Minecraft Guerra 2 {self.get_version_suffix()}"
    
    def get_target_directory(self):
        """
        Determina o diretório de instalação baseado no launcher selecionado.
        
        Returns:
            str: Caminho absoluto do diretório de instalação
        """
        launcher = self.var_launcher.get()
        
        # Se instalação manual, retorna caminho selecionado pelo usuário
        if "manual" in launcher: 
            return self.var_install_path.get()

        # Obtém diretório AppData do Windows
        appdata = os.getenv('APPDATA')
        minecraft_default = os.path.join(appdata, ".minecraft")
        
        # Nome da pasta específico para cada versão
        folder_name = self.get_folder_name()
        profile_name = self.get_profile_name()

        # TLauncher: Instala como versão do Minecraft
        if launcher == "tlauncher":
            return os.path.join(minecraft_default, "versions", folder_name)
        
        # SKLauncher: Usa sistema de instâncias
        elif launcher == "sklauncher":
            return os.path.join(minecraft_default, "instances", folder_name)
        
        # Modrinth App: Diretório próprio de perfis
        elif launcher == "modrinth":
            return os.path.join(appdata, "ModrinthApp", "profiles", profile_name)

        # CurseForge: Usa diretório do perfil de usuário
        elif launcher == "curseforge":
            user_profile = os.getenv('USERPROFILE') or os.path.expanduser("~")
            return os.path.join(user_profile, "curseforge", "minecraft", "Instances", profile_name)

        # Fallback para diretório padrão do Minecraft
        return minecraft_default

    def configure_sklauncher_profile(self):
        """
        Configura perfil do SKLauncher no arquivo launcher_profiles.json.
        Cria ou atualiza o perfil 'Minecraft Guerra 2' com as configurações apropriadas.
        
        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            # Localiza arquivo de perfis do Minecraft
            appdata = os.getenv('APPDATA')
            minecraft_dir = os.path.join(appdata, ".minecraft")
            profiles_path = os.path.join(minecraft_dir, "launcher_profiles.json")
            
            # Caminho dinâmico onde o modpack foi instalado (inclui versão)
            game_dir_installed = os.path.join(minecraft_dir, "instances", self.get_folder_name())

            # Lê ou cria arquivo de perfis
            if not os.path.exists(profiles_path):
                print("Arquivo launcher_profiles.json não encontrado. Criando um novo.")
                data = {"profiles": {}}
            else:
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"profiles": {}}

            if "profiles" not in data: 
                data["profiles"] = {}

            # ID único para cada versão do modpack
            profile_ids = {
                "Full": "686d1a5248c548dca11bfc1d256b1784",
                "Intermediate": "786d1a5248c548dca11bfc1d256b1785",
                "Lightweight": "886d1a5248c548dca11bfc1d256b1786"
            }
            profile_id = profile_ids.get(self.get_version_suffix(), "686d1a5248c548dca11bfc1d256b1784")
            
            # Cria objeto de perfil com todas as configurações necessárias
            new_profile = {
                "name": self.get_profile_name(),  # Nome incluindo versão
                "gameDir": game_dir_installed,  # Caminho dinâmico
                "lastVersionId": "1.20.1-forge-47.4.6",  # Versão do Minecraft + Forge
                "resolution": {
                    "width": 854,
                    "height": 480,
                    "fullscreen": False
                },
                "type": "custom",
                "created": datetime.datetime.now().isoformat(),
                "lastUsed": datetime.datetime.now().isoformat()
            }

            # Adiciona/atualiza perfil no dicionário
            data["profiles"][profile_id] = new_profile

            # Salva arquivo de perfis atualizado
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            print(f"Perfil SKLauncher configurado em: {profiles_path}")
            return True

        except Exception as e:
            print(f"Erro ao configurar perfil SKLauncher: {e}")
            return False

    def configure_modrinth_profile(self):
        """
        Configura perfil do Modrinth App no banco de dados SQLite (app.db).
        Cria ou atualiza o perfil 'Minecraft Guerra' com as configurações apropriadas.
        
        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            # Localiza banco de dados do Modrinth App
            appdata = os.getenv('APPDATA')
            db_path = os.path.join(appdata, "ModrinthApp", "app.db")
            
            if not os.path.exists(db_path):
                print("Banco de dados do Modrinth não encontrado.")
                return False

            # Conecta ao banco de dados SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Nome do perfil com versão
            profile_name = self.get_profile_name()

            # Verifica se o perfil já existe
            cursor.execute("SELECT path FROM profiles WHERE path = ?", (profile_name,))
            if cursor.fetchone():
                # Perfil existe - atualiza apenas timestamp de modificação
                print(f"Perfil Modrinth '{profile_name}' já existe. Atualizando timestamps.")
                now = int(time.time())
                cursor.execute("UPDATE profiles SET modified = ? WHERE path = ?", (now, profile_name))
            else:
                # Perfil não existe - cria novo
                print(f"Criando novo perfil Modrinth '{profile_name}'...")
                now = int(time.time())
                
                # Query de inserção com todos os campos necessários
                query = """
                    INSERT INTO profiles (
                        path, install_stage, name, icon_path, game_version, mod_loader, mod_loader_version, 
                        groups, linked_project_id, linked_version_id, locked, created, modified, last_played, 
                        submitted_time_played, recent_time_played, override_java_path, override_extra_launch_args, 
                        override_custom_env_vars, override_mc_memory_max, override_mc_force_fullscreen, 
                        override_mc_game_resolution_x, override_mc_game_resolution_y, override_hook_pre_launch, 
                        override_hook_wrapper, override_hook_post_exit, protocol_version, launcher_feature_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # Valores do perfil
                values = (
                    profile_name,          # path
                    "installed",           # install_stage
                    profile_name,          # name
                    None,                  # icon_path
                    "1.20.1",             # game_version
                    "forge",              # mod_loader
                    "47.4.6",             # mod_loader_version
                    "11",                 # groups
                    None,                 # linked_project_id
                    None,                 # linked_version_id
                    None,                 # locked
                    now,                  # created
                    now,                  # modified
                    None,                 # last_played
                    0,                    # submitted_time_played
                    0,                    # recent_time_played
                    None,                 # override_java_path
                    0,                    # override_extra_launch_args
                    0,                    # override_custom_env_vars
                    None,                 # override_mc_memory_max
                    None,                 # override_mc_force_fullscreen
                    None,                 # override_mc_game_resolution_x
                    None,                 # override_mc_game_resolution_y
                    None,                 # override_hook_pre_launch
                    None,                 # override_hook_wrapper
                    None,                 # override_hook_post_exit
                    763,                  # protocol_version (1.20.1)
                    "migrated_launch_hooks"  # launcher_feature_version
                )
                cursor.execute(query, values)

            # Salva alterações e fecha conexão
            conn.commit()
            conn.close()
            print(f"Perfil Modrinth configurado em: {db_path}")
            return True

        except Exception as e:
            print(f"Erro ao configurar perfil Modrinth: {e}")
            return False

    # ==========================================
    # LÓGICA PRINCIPAL DE INSTALAÇÃO
    # ==========================================
    
    def run_installation_logic(self):
        """
        Executa o processo completo de instalação em thread separada.
        
        Etapas:
        1. Fecha processos conflitantes (launchers e Minecraft)
        2. Faz download do modpack
        3. Extrai arquivos para o diretório apropriado
        4. Configura perfil do launcher (se aplicável)
        5. Finaliza e exibe resultado
        """
        try:
            # ==========================================
            # PASSO 1: FECHAR PROCESSOS CONFLITANTES
            # ==========================================
            self.update_status("Fechando launchers e Minecraft...", 5)
            kill_list = ["Modrinth App.exe", "minecraft.exe", "CurseForge.exe", "java.exe", "javaw.exe"]
            for proc in kill_list:
                # Executa taskkill silenciosamente para cada processo
                os.system(f'taskkill /F /IM "{proc}" >nul 2>&1')
            time.sleep(2)  # Aguarda finalização dos processos  # Aguarda finalização dos processos

            version = self.var_version.get()
            launcher = self.var_launcher.get()

            # ==========================================
            # PASSO 2: RESOLVER URL DE DOWNLOAD
            # ==========================================
            # Normaliza chave do launcher (manual_pirata/manual_original -> manual)
            launcher_key = "manual" if "manual" in launcher else launcher
            
            # Busca URL apropriada no dicionário
            if launcher_key in self.DOWNLOAD_URLS and version in self.DOWNLOAD_URLS[launcher_key]:
                url = self.DOWNLOAD_URLS[launcher_key][version]
            else:
                # Fallback para caso URL não esteja configurada
                url = "http://example.com" 
                if "LINK_" in str(self.DOWNLOAD_URLS.get(launcher_key, {}).get(version, "")):
                     self.after(0, lambda: messagebox.showerror("Erro", "Links de download não configurados no código!"))
                     self.finish_installation_ui(success=False)
                     return

            # ==========================================
            # MODO SIMULAÇÃO (URLs de placeholder)
            # ==========================================
            # Usado para testes quando links reais não estão disponíveis
            if "LINK_" in url or "example.com" in url:
                self.update_status("Modo Simulação (Links não reais)...", 50)
                time.sleep(2)
                
                # Cria pasta de destino para SKLauncher funcionar
                target_dir = self.get_target_directory()
                if not os.path.exists(target_dir): 
                    os.makedirs(target_dir)
                
                # Configura perfil do launcher (simulação)
                if launcher == "sklauncher":
                    self.update_status("Configurando perfil SKLauncher...", 90)
                    self.configure_sklauncher_profile()
                elif launcher == "modrinth":
                    self.update_status("Configurando perfil Modrinth...", 90)
                    self.configure_modrinth_profile()
                
                self.finish_installation_ui(success=True)
                return

            target_dir = self.get_target_directory()

            # ==========================================
            # PASSO 3: DOWNLOAD E EXTRAÇÃO DO MODPACK
            # ==========================================
            # Usa diretório temporário para download (limpo automaticamente)
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "modpack.zip")

                # --- Download ---
                self.update_status(f"Baixando {version}...", 0)
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                wrote = 0

                # Escreve arquivo em chunks e atualiza progresso
                with open(zip_path, 'wb') as f:
                    for data in response.iter_content(1024):
                        wrote += len(data)
                        f.write(data)
                        # Atualiza barra de progresso a cada ~200KB para não sobrecarregar UI
                        if total_size > 0 and wrote % (1024*200) == 0:
                            percent = (wrote / total_size) * 100
                            self.after(0, lambda p=percent: self.update_status(f"Baixando... {int(p)}%", p))

                # --- Extração ---
                self.update_status("Extraindo arquivos...", 100)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # Extrai todos os arquivos do ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    for index, file in enumerate(file_list):
                        zip_ref.extract(file, target_dir)
                        # Atualiza status a cada 50 arquivos para não travar a UI
                        if index % 50 == 0:
                            percent = (index / total_files) * 100
                            filename = file.split('/')[-1] if '/' in file else file
                            self.after(0, lambda p=percent, f=filename: self.update_status(f"Extraindo: {f}", p))

            # ==========================================
            # PASSO 4: CONFIGURAÇÃO PÓS-INSTALAÇÃO
            # ==========================================
            # Configura perfil do launcher (SKLauncher e Modrinth)
            if launcher == "sklauncher":
                self.update_status("Atualizando perfis do Launcher...", 100)
                self.configure_sklauncher_profile()
            elif launcher == "modrinth":
                self.update_status("Atualizando banco de dados do Modrinth...", 100)
                self.configure_modrinth_profile()

            # Finaliza com sucesso
            self.finish_installation_ui(success=True)

        except Exception as e:
            # Tratamento de erros: exibe mensagem e finaliza com falha
            print(e)
            self.after(0, lambda err=str(e): messagebox.showerror("Erro Fatal", f"{err}"))
            self.finish_installation_ui(success=False)

    def update_status(self, text, val):
        """
        Atualiza o texto de status e a barra de progresso durante a instalação.
        
        Args:
            text (str): Texto descritivo do status atual
            val (int): Valor da barra de progresso (0-100)
        """
        self.lbl_details.configure(text=text)
        self.progress.set(val / 100)  # CustomTkinter usa valores de 0 a 1
        self.lbl_percentage.configure(text=f"{int(val)}%")
        
        # Anima o ícone baseado no progresso
        if val < 100:
            icons = ["⏳", "⌛"]
            current_icon = icons[int(val / 10) % 2]
            self.status_icon.configure(text=current_icon)

    def finish_installation_ui(self, success):
        """
        Finaliza a interface de instalação exibindo resultado.
        
        Args:
            success (bool): True se instalação foi bem-sucedida, False caso contrário
        """
        self.btn_next.configure(state="normal")
        
        if success:
            self.status_icon.configure(text="✅")
            self.lbl_status_title.configure(text="Instalação Concluída!", text_color="#2ecc71")
            self.lbl_details.configure(text=f"📁 Instalado em:\n{self.get_target_directory()}")
            self.progress.set(1)
            self.lbl_percentage.configure(text="100%")
            
            # Card de sucesso
            success_card = ctk.CTkFrame(
                self.content_frame,
                fg_color=("#d4edda", "#1e4620"),
                corner_radius=10
            )
            success_card.place(relx=0.5, rely=0.85, anchor="center")
            
            ctk.CTkLabel(
                success_card,
                text="🎉 Pronto para jogar! Inicie seu launcher.",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#155724", "#90ee90")
            ).pack(padx=30, pady=15)
        else:
            self.status_icon.configure(text="❌")
            self.lbl_status_title.configure(text="Instalação Falhou", text_color="#e74c3c")
            self.lbl_details.configure(text="Ocorreu um erro durante a instalação.\nVerifique sua conexão e tente novamente.")
            self.lbl_percentage.configure(text="Erro")

# ==========================================
# PONTO DE ENTRADA DA APLICAÇÃO
# ==========================================
if __name__ == "__main__":
    # Cria e executa a aplicação
    app = ModpackWizard()
    app.mainloop()