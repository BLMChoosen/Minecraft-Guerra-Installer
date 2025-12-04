import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import os
import zipfile
import tempfile
import json
import datetime
import sqlite3

# Tente importar requests
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
        # CONFIGURAÇÃO DE LINKS
        # ==========================================
        self.DOWNLOAD_URLS = {
            "tlauncher": {
                "full": "LINK_TLAUNCHER_FULL",
                "intermediate": "LINK_TLAUNCHER_INTERMEDIATE",
                "lightweight": "LINK_TLAUNCHER_LIGHT"
            },
            "sklauncher": {
                "full": "https://api.bloodmoonbr.com/downloads/Full-Curseforge.zip",
                "intermediate": "LINK_SKLAUNCHER_INTERMEDIATE",
                "lightweight": "LINK_SKLAUNCHER_LIGHT"
            },
            "modrinth": {
                "full": "https://api.bloodmoonbr.com/downloads/Full-Curseforge.zip",
                "intermediate": "LINK_MODRINTH_INTERMEDIATE",
                "lightweight": "LINK_MODRINTH_LIGHT"
            },
            "curseforge": {
                "full": "https://api.bloodmoonbr.com/downloads/Full-Curseforge.zip",
                "intermediate": "https://api.bloodmoonbr.com/downloads/Intermediate-Curseforge.zip",
                "lightweight": "https://api.bloodmoonbr.com/downloads/Light-Curseforge.zip"
            },
            "manual": {
                "full": "https://api.bloodmoonbr.com/downloads/Full-Curseforge.zip",
                "intermediate": "LINK_MANUAL_INTERMEDIATE",
                "lightweight": "LINK_MANUAL_LIGHT"
            }
        }

        # Variáveis de Controle
        self.current_step = 1
        
        self.var_license_type = tk.StringVar(value="") 
        self.var_launcher = tk.StringVar(value="")     
        self.var_version = tk.StringVar(value="full")  
        self.var_install_path = tk.StringVar(value="") 
        
        # Estilo e Layout
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('TButton', font=('Helvetica', 10))

        self.content_frame = ttk.Frame(self, padding="20 20 20 20")
        self.content_frame.pack(expand=True, fill="both")

        self.nav_frame = ttk.Frame(self, padding="10 10 10 10")
        self.nav_frame.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(self.nav_frame, text="Cancelar", command=self.on_cancel)
        self.btn_cancel.pack(side="left")

        self.btn_next = ttk.Button(self.nav_frame, text="Próximo >", command=self.go_next)
        self.btn_next.pack(side="right")

        self.btn_prev = ttk.Button(self.nav_frame, text="< Anterior", command=self.go_prev)
        self.btn_prev.pack(side="right", padx=10)

        self.show_step(1)

    # ... Navegação Básica ...
    def clear_content(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()

    def update_nav_buttons(self):
        if self.current_step == 1: self.btn_prev.state(['disabled'])
        else: self.btn_prev.state(['!disabled'])

        if self.current_step == 5:
            self.btn_next.config(text="Fechar", command=self.quit)
            self.btn_prev.pack_forget()
            self.btn_cancel.pack_forget()
        else:
            self.btn_next.config(text="Próximo >", command=self.go_next)

    def go_next(self):
        # Validações
        if self.current_step == 2 and not self.var_license_type.get():
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
        f = filedialog.askdirectory()
        if f: self.var_install_path.set(f)

    # ... Telas ...
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
        ttk.Label(self.content_frame, text="Este assistente configurará o modpack automaticamente.", justify="center").pack(pady=10)

    def screen_license_type(self):
        ttk.Label(self.content_frame, text="Tipo de Minecraft", style='Title.TLabel').pack(pady=20)
        ttk.Radiobutton(self.content_frame, text="Original (Premium)", variable=self.var_license_type, value="original").pack(anchor='w', pady=5, padx=50)
        ttk.Radiobutton(self.content_frame, text="Pirata (Alternativo)", variable=self.var_license_type, value="pirata").pack(anchor='w', pady=5, padx=50)

    def screen_launcher_select(self):
        ttk.Label(self.content_frame, text="Selecione o Launcher", style='Title.TLabel').pack(pady=20)
        license_type = self.var_license_type.get()
        options = [("TLauncher", "tlauncher"), ("SKLauncher", "sklauncher"), ("Manual", "manual_pirata")] if license_type == "pirata" else [("Modrinth App", "modrinth"), ("CurseForge", "curseforge"), ("Manual", "manual_original")]
        
        for text, value in options:
            ttk.Radiobutton(self.content_frame, text=text, variable=self.var_launcher, value=value, command=self.toggle_manual).pack(anchor='w', pady=5, padx=50)

        self.frame_manual = ttk.Frame(self.content_frame)
        self.frame_manual.pack(fill='x', padx=50, pady=20)
        ttk.Label(self.frame_manual, text="Pasta:").pack(side='left')
        ttk.Entry(self.frame_manual, textvariable=self.var_install_path).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(self.frame_manual, text="...", width=3, command=self.select_folder).pack(side='left')
        self.toggle_manual()

    def toggle_manual(self):
        state = 'normal' if "manual" in self.var_launcher.get() else 'disabled'
        for c in self.frame_manual.winfo_children(): c.configure(state=state)

    def screen_version_select(self):
        ttk.Label(self.content_frame, text="Versão do Modpack", style='Title.TLabel').pack(pady=20)
        ttk.Radiobutton(self.content_frame, text="Full (Pesado)", variable=self.var_version, value="full").pack(anchor='w', pady=10, padx=50)
        ttk.Radiobutton(self.content_frame, text="Intermediate (Médio)", variable=self.var_version, value="intermediate").pack(anchor='w', pady=10, padx=50)
        ttk.Radiobutton(self.content_frame, text="Lightweight (Leve)", variable=self.var_version, value="lightweight").pack(anchor='w', pady=10, padx=50)

    def screen_installing_finished(self):
        self.lbl_status_title = ttk.Label(self.content_frame, text="Iniciando...", style='Title.TLabel')
        self.lbl_status_title.pack(pady=(40, 20))
        self.progress = ttk.Progressbar(self.content_frame, length=400, mode='determinate')
        self.progress.pack(pady=30)
        self.lbl_details = ttk.Label(self.content_frame, text="Preparando...", font=('Helvetica', 9))
        self.lbl_details.pack()

    # ==========================================
    # LÓGICA DE DIRETÓRIOS E CONFIGURAÇÃO
    # ==========================================
    def get_target_directory(self):
        launcher = self.var_launcher.get()
        if "manual" in launcher: return self.var_install_path.get()

        appdata = os.getenv('APPDATA')
        minecraft_default = os.path.join(appdata, ".minecraft")

        if launcher == "tlauncher":
            return os.path.join(minecraft_default, "versions", "Minecraft_Guerra_2")
        
        elif launcher == "sklauncher":
            # Caminho específico solicitado para SKLauncher
            return os.path.join(minecraft_default, "instances", "Minecraft_Guerra_2")
        
        elif launcher == "modrinth":
            return os.path.join(appdata, "ModrinthApp", "profiles", "Minecraft Guerra")

        elif launcher == "curseforge":
            user_profile = os.getenv('USERPROFILE') or os.path.expanduser("~")
            return os.path.join(user_profile, "curseforge", "minecraft", "Instances", "Minecraft Guerra")

        return minecraft_default

    def configure_sklauncher_profile(self):
        """ Edita o launcher_profiles.json para adicionar o perfil do Guerra """
        try:
            appdata = os.getenv('APPDATA')
            minecraft_dir = os.path.join(appdata, ".minecraft")
            profiles_path = os.path.join(minecraft_dir, "launcher_profiles.json")
            
            # Caminho onde os arquivos foram instalados (Dinâmico, não fixo no usuário Choosen)
            game_dir_installed = os.path.join(minecraft_dir, "instances", "Minecraft_Guerra_2")

            if not os.path.exists(profiles_path):
                print("Arquivo launcher_profiles.json não encontrado. Criando um novo.")
                data = {"profiles": {}}
            else:
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"profiles": {}}

            if "profiles" not in data: data["profiles"] = {}

            # ID Fixo solicitado
            profile_id = "686d1a5248c548dca11bfc1d256b1784"
            
            # Dados do perfil
            new_profile = {
                "name": "Minecraft Guerra 2",
                "gameDir": game_dir_installed, # Caminho dinâmico importante!
                "lastVersionId": "1.20.1-forge-47.4.6",
                "resolution": {
                    "width": 854,
                    "height": 480,
                    "fullscreen": False
                },
                "type": "custom",
                "created": datetime.datetime.now().isoformat(),
                "lastUsed": datetime.datetime.now().isoformat()
            }

            data["profiles"][profile_id] = new_profile

            # Salva o arquivo com backup de segurança é uma boa prática, mas vamos salvar direto
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            print(f"Perfil SKLauncher configurado em: {profiles_path}")
            return True

        except Exception as e:
            print(f"Erro ao configurar perfil SKLauncher: {e}")
            return False

    def configure_modrinth_profile(self):
        """ Configura o perfil no banco de dados do Modrinth App """
        try:
            appdata = os.getenv('APPDATA')
            db_path = os.path.join(appdata, "ModrinthApp", "app.db")
            
            if not os.path.exists(db_path):
                print("Banco de dados do Modrinth não encontrado.")
                return False

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Verifica se já existe
            cursor.execute("SELECT path FROM profiles WHERE path = ?", ("Minecraft Guerra",))
            if cursor.fetchone():
                print("Perfil Modrinth já existe. Atualizando timestamps.")
                now = int(time.time())
                cursor.execute("UPDATE profiles SET modified = ? WHERE path = ?", (now, "Minecraft Guerra"))
            else:
                print("Criando novo perfil Modrinth...")
                now = int(time.time())
                # Query baseada no exemplo do usuário
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
                values = (
                    "Minecraft Guerra", "installed", "Minecraft Guerra", None, "1.20.1", "forge", "47.4.6", 
                    "11", None, None, None, now, now, None, 
                    0, 0, None, 0, 0, None, None, None, None, None, None, None, 763, "migrated_launch_hooks"
                )
                cursor.execute(query, values)

            conn.commit()
            conn.close()
            print(f"Perfil Modrinth configurado em: {db_path}")
            return True

        except Exception as e:
            print(f"Erro ao configurar perfil Modrinth: {e}")
            return False

    def run_installation_logic(self):
        try:
            # Fechar processos conflitantes antes de tudo
            self.update_status("Fechando launchers e Minecraft...", 5)
            kill_list = ["Modrinth App.exe", "minecraft.exe", "CurseForge.exe", "java.exe", "javaw.exe"]
            for proc in kill_list:
                # Executa taskkill silenciosamente
                os.system(f'taskkill /F /IM "{proc}" >nul 2>&1')
            time.sleep(2)

            version = self.var_version.get()
            launcher = self.var_launcher.get()

            # 1. Resolver URL
            launcher_key = "manual" if "manual" in launcher else launcher
            
            if launcher_key in self.DOWNLOAD_URLS and version in self.DOWNLOAD_URLS[launcher_key]:
                url = self.DOWNLOAD_URLS[launcher_key][version]
            else:
                # Fallback para teste
                url = "http://example.com" 
                if "LINK_" in str(self.DOWNLOAD_URLS.get(launcher_key, {}).get(version, "")):
                     self.after(0, lambda: messagebox.showerror("Erro", "Links de download não configurados no código!"))
                     self.finish_installation_ui(success=False)
                     return

            # Modo Simulação (se o link for placeholder)
            if "LINK_" in url or "example.com" in url:
                self.update_status("Modo Simulação (Links não reais)...", 50)
                time.sleep(2)
                
                # Simula criação da pasta para o SKLauncher funcionar
                target_dir = self.get_target_directory()
                if not os.path.exists(target_dir): os.makedirs(target_dir)
                
                if launcher == "sklauncher":
                    self.update_status("Configurando perfil SKLauncher...", 90)
                    self.configure_sklauncher_profile()
                elif launcher == "modrinth":
                    self.update_status("Configurando perfil Modrinth...", 90)
                    self.configure_modrinth_profile()
                
                self.finish_installation_ui(success=True)
                return

            target_dir = self.get_target_directory()

            # 2. Download e Extração
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "modpack.zip")

                # Download
                self.update_status(f"Baixando {version}...", 0)
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                wrote = 0

                with open(zip_path, 'wb') as f:
                    for data in response.iter_content(1024):
                        wrote += len(data)
                        f.write(data)
                        if total_size > 0 and wrote % (1024*200) == 0:
                            percent = (wrote / total_size) * 100
                            self.after(0, lambda p=percent: self.progress.configure(value=p))

                # Extração
                self.update_status("Extraindo arquivos...", 100)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    for index, file in enumerate(file_list):
                        zip_ref.extract(file, target_dir)
                        if index % 50 == 0: # Atualiza a cada 50 arquivos para não travar a UI
                            percent = (index / total_files) * 100
                            self.after(0, lambda p=percent, f=file: self.update_status(f"Extraindo: {f}", p))

            # 3. Configuração Pós-Instalação (SKLauncher)
            if launcher == "sklauncher":
                self.update_status("Atualizando perfis do Launcher...", 100)
                self.configure_sklauncher_profile()
            elif launcher == "modrinth":
                self.update_status("Atualizando banco de dados do Modrinth...", 100)
                self.configure_modrinth_profile()

            self.finish_installation_ui(success=True)

        except Exception as e:
            print(e)
            self.after(0, lambda err=str(e): messagebox.showerror("Erro Fatal", f"{err}"))
            self.finish_installation_ui(success=False)

    def update_status(self, text, val):
        self.lbl_details.config(text=text)
        self.progress.configure(value=val)

    def finish_installation_ui(self, success):
        self.btn_next.state(['!disabled'])
        if success:
            self.lbl_status_title.config(text="Sucesso!")
            self.lbl_details.config(text=f"Instalado em:\n{self.get_target_directory()}")
            self.progress.configure(value=100)
        else:
            self.lbl_status_title.config(text="Erro")
            self.lbl_details.config(text="A instalação falhou.")

if __name__ == "__main__":
    app = ModpackWizard()
    app.mainloop()