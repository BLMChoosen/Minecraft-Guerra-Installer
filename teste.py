import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import os
import zipfile
import tempfile
import shutil

# Tente importar requests, se não tiver, avisa o usuário
try:
    import requests
except ImportError:
    messagebox.showerror("Erro", "A biblioteca 'requests' não está instalada.\nExecute: pip install requests")
    exit()

class ModpackWizard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Instalador do Modpack Minecraft")
        self.geometry("600x450")
        self.resizable(False, False)

        # ==========================================
            # CONFIGURAÇÃO DE LINKS (Coloque seus links aqui)
            # ==========================================
        self.DOWNLOAD_URLS = {
            "full": "https://api.bloodmoonbr.com/downloads/Full-Curseforge.zip",
            "intermediate": "https://example.com/modpack_intermediate.zip",
            "lightweight": "https://example.com/modpack_light.zip"
        }

        # Variáveis de Controle
        self.current_step = 1
        
        self.var_license_type = tk.StringVar(value="") 
        self.var_launcher = tk.StringVar(value="")     
        self.var_version = tk.StringVar(value="full")  
        self.var_install_path = tk.StringVar(value="") 
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TRadiobutton', font=('Helvetica', 11))

        # Layout
        self.content_frame = ttk.Frame(self, padding="20 20 20 20")
        self.content_frame.pack(expand=True, fill="both")

        self.nav_frame = ttk.Frame(self, padding="10 10 10 10")
        self.nav_frame.pack(fill="x", side="bottom")

        # Botões
        self.btn_cancel = ttk.Button(self.nav_frame, text="Cancelar", command=self.on_cancel)
        self.btn_cancel.pack(side="left")

        self.btn_next = ttk.Button(self.nav_frame, text="Próximo >", command=self.go_next)
        self.btn_next.pack(side="right")

        self.btn_prev = ttk.Button(self.nav_frame, text="< Anterior", command=self.go_prev)
        self.btn_prev.pack(side="right", padx=10)

        self.show_step(1)

    # ... (Métodos de navegação mantidos iguais) ...
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_nav_buttons(self):
        if self.current_step == 1:
            self.btn_prev.state(['disabled'])
        else:
            self.btn_prev.state(['!disabled'])

        if self.current_step == 5:
            self.btn_next.config(text="Fechar", command=self.quit)
            self.btn_prev.pack_forget()
            self.btn_cancel.pack_forget()
        else:
            self.btn_next.config(text="Próximo >", command=self.go_next)

    def go_next(self):
        if self.current_step == 2:
            if not self.var_license_type.get():
                messagebox.showwarning("Atenção", "Selecione uma opção de licença.")
                return

        if self.current_step == 3:
            if not self.var_launcher.get():
                messagebox.showwarning("Atenção", "Selecione um launcher.")
                return
            if "manual" in self.var_launcher.get() and not self.var_install_path.get():
                messagebox.showwarning("Atenção", "Para instalação manual, selecione uma pasta.")
                return

        if self.current_step == 4:
            self.current_step += 1
            self.show_step(5)
            # Inicia thread de instalação real
            threading.Thread(target=self.run_installation_logic, daemon=True).start()
            return

        if self.current_step < 5:
            self.current_step += 1
            self.show_step(self.current_step)

    def go_prev(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.show_step(self.current_step)

    def on_cancel(self):
        if messagebox.askyesno("Cancelar", "Sair da instalação?"):
            self.quit()

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.var_install_path.set(folder_selected)

    # ==========================================
    # TELAS
    # ==========================================
    def show_step(self, step):
        self.clear_content()
        self.update_nav_buttons()
        if step == 1: self.screen_welcome()
        elif step == 2: self.screen_license_type()
        elif step == 3: self.screen_launcher_select()
        elif step == 4: self.screen_version_select()
        elif step == 5: self.screen_installing_finished()

    def screen_welcome(self):
        ttk.Label(self.content_frame, text="Instalador do Modpack", style='Title.TLabel').pack(pady=(40, 20))
        ttk.Label(self.content_frame, text="Este assistente baixará e instalará o modpack automaticamente.\nClique em Próximo.", justify="center").pack(pady=10)

    def screen_license_type(self):
        ttk.Label(self.content_frame, text="Tipo de Minecraft", style='Title.TLabel').pack(pady=20)
        ttk.Radiobutton(self.content_frame, text="Original (Premium)", variable=self.var_license_type, value="original").pack(anchor='w', pady=5, padx=50)
        ttk.Radiobutton(self.content_frame, text="Pirata (Alternativo)", variable=self.var_license_type, value="pirata").pack(anchor='w', pady=5, padx=50)

    def screen_launcher_select(self):
        ttk.Label(self.content_frame, text="Selecione o Launcher", style='Title.TLabel').pack(pady=20)
        
        license_type = self.var_license_type.get()
        if license_type == "pirata":
            options = [("TLauncher", "tlauncher"), ("SKLauncher", "sklauncher"), ("Manual", "manual_pirata")]
        else:
            options = [("Modrinth App", "modrinth"), ("CurseForge", "curseforge"), ("Launcher Oficial", "official"), ("Manual", "manual_original")]

        for text, value in options:
            ttk.Radiobutton(self.content_frame, text=text, variable=self.var_launcher, value=value, command=self.toggle_manual_path).pack(anchor='w', pady=5, padx=50)

        self.frame_manual = ttk.Frame(self.content_frame)
        self.frame_manual.pack(fill='x', padx=50, pady=20)
        ttk.Label(self.frame_manual, text="Pasta:").pack(side='left')
        ttk.Entry(self.frame_manual, textvariable=self.var_install_path).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(self.frame_manual, text="...", width=3, command=self.select_folder).pack(side='left')
        self.toggle_manual_path()

    def toggle_manual_path(self):
        state = 'normal' if "manual" in self.var_launcher.get() else 'disabled'
        for child in self.frame_manual.winfo_children(): child.configure(state=state)

    def screen_version_select(self):
        ttk.Label(self.content_frame, text="Versão do Modpack", style='Title.TLabel').pack(pady=20)
        ttk.Radiobutton(self.content_frame, text="Full (Pesado)", variable=self.var_version, value="full").pack(anchor='w', pady=10, padx=50)
        ttk.Radiobutton(self.content_frame, text="Intermediate (Médio)", variable=self.var_version, value="intermediate").pack(anchor='w', pady=10, padx=50)
        ttk.Radiobutton(self.content_frame, text="Lightweight (Leve)", variable=self.var_version, value="lightweight").pack(anchor='w', pady=10, padx=50)

    def screen_installing_finished(self):
        self.lbl_status_title = ttk.Label(self.content_frame, text="Iniciando Download...", style='Title.TLabel')
        self.lbl_status_title.pack(pady=(40, 20))
        self.progress = ttk.Progressbar(self.content_frame, length=400, mode='determinate')
        self.progress.pack(pady=30)
        self.lbl_details = ttk.Label(self.content_frame, text="Conectando...", font=('Helvetica', 9))
        self.lbl_details.pack()

    # ==========================================
    # LÓGICA REAL DE DOWNLOAD E EXTRAÇÃO
    # ==========================================
    def get_target_directory(self):
        """Determina onde instalar baseado no launcher escolhido"""
        launcher = self.var_launcher.get()
        
        # 1. Se for manual, usa o caminho que o usuário digitou
        if "manual" in launcher:
            return self.var_install_path.get()

        # 2. Caminho padrão do Minecraft (%appdata%/.minecraft)
        appdata = os.getenv('APPDATA')
        minecraft_default = os.path.join(appdata, ".minecraft")

        # Lógica de destino baseada no launcher (Exemplos)
        if launcher in ["tlauncher", "sklauncher", "official"]:
            # Geralmente instalam na .minecraft ou criam versões lá dentro
            return minecraft_default
        
        elif launcher == "curseforge":
            # Curseforge: C:\Users\{USER}\curseforge\minecraft\Instances\Minecraft Guerra
            user_profile = os.getenv('USERPROFILE') # Mais seguro no Windows que expanduser("~") as vezes
            if not user_profile:
                user_profile = os.path.expanduser("~")
            return os.path.join(user_profile, "curseforge", "minecraft", "Instances", "Minecraft Guerra")
            
        elif launcher == "modrinth":
             return os.path.join(appdata, "com.modrinth.theseus", "profiles", "MeuModpack")

        return minecraft_default # Fallback

    def run_installation_logic(self):
        try:
            # 1. Obter URL e Caminho
            version = self.var_version.get()
            url = self.DOWNLOAD_URLS.get(version, self.DOWNLOAD_URLS["full"]) # Fallback para full
            target_dir = self.get_target_directory()
            
            # Nota: Para teste, se o link não for real, vai dar erro.
            # Vou usar um link dummy ou verificar se é exemplo
            if "example.com" in url:
                self.update_status("Modo de Simulação (Links não configurados)", 0)
                time.sleep(2)
                self.finish_installation_ui(success=True)
                return

            # Cria diretório temporário para baixar o zip
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "modpack_temp.zip")

                # 2. Download
                self.update_status(f"Baixando versão {version.upper()}...", 0)
                
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024 # 1 Kibibyte
                wrote = 0

                with open(zip_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        wrote = wrote + len(data)
                        f.write(data)
                        # Atualiza barra de progresso
                        if total_size > 0:
                            percent = (wrote / total_size) * 100
                            # Atualiza UI a cada pedaço (pode ser frequente demais, mas ok pra exemplo)
                            if wrote % (1024*100) == 0: # Atualiza a cada 100kb
                                self.after(0, lambda p=percent: self.progress.configure(value=p))

                self.update_status("Download concluído. Extraindo...", 100)
                
                # 3. Extração
                # Garante que a pasta de destino existe
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Opcional: Calcular progresso da extração contando arquivos
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    
                    for index, file in enumerate(file_list):
                        zip_ref.extract(file, target_dir)
                        # Atualiza progresso da extração
                        percent = (index / total_files) * 100
                        self.after(0, lambda p=percent, f=file: self.update_status(f"Extraindo: {f}", p))

            self.finish_installation_ui(success=True)

        except Exception as e:
            print(e)
            self.after(0, lambda err=str(e): messagebox.showerror("Erro na Instalação", f"Ocorreu um erro:\n{err}"))
            self.finish_installation_ui(success=False)

    def update_status(self, text, progress_val):
        self.lbl_details.config(text=text)
        self.progress.configure(value=progress_val)

    def finish_installation_ui(self, success):
        self.btn_next.state(['!disabled'])
        if success:
            self.lbl_status_title.config(text="Instalação Concluída!")
            self.lbl_details.config(text=f"Arquivos instalados em:\n{self.get_target_directory()}")
            self.progress.configure(value=100)
        else:
            self.lbl_status_title.config(text="Falha na Instalação")
            self.lbl_details.config(text="Verifique sua internet ou o link do arquivo.")

if __name__ == "__main__":
    app = ModpackWizard()
    app.mainloop()