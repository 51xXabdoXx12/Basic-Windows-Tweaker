#pyinstaller --onefile --noconsole --icon=icon.ico --uac-admin --add-data "LLG-CΞRT1F1ΞD.pow;." --add-data "icon.ico;." --name "Basic Tweaker V4.5" "Basic_Tweaker_V4.5Github.py"
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import winreg
import ctypes
import os
import sys
from PIL import Image, ImageTk
import customtkinter as ctk
import psutil
import platform
import re
import winreg as _wr

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class WindowsOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.after(200, lambda: self.root.iconbitmap(resource_path("icon.ico")))
        self.root.title("Basic Tweaker V4.5")
        self.root.geometry("720x860")
        self.root.minsize(720, 860)
        self.root.configure(bg='#0a0e1a')
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TNotebook', background='#05091a', borderwidth=0, highlightthickness=0)
        style.configure('TNotebook.Tab', background='#05091a', foreground='#00aaff', padding=[10, 5])
        style.configure('TFrame', background='#05091a')
        style.configure('TScrollbar', background='#05091a', troughcolor='#05091a', borderwidth=0)
        style.map('TNotebook.Tab',
            background=[('selected', '#05091a'), ('active', '#05091a')],
            foreground=[('selected', 'white'), ('active', '#00aaff')]
        )
        style.layout('TNotebook', [('Notebook.client', {'sticky': 'nswe'})])
        if not self.is_admin():
            ctk.CTkToplevel(self.root)  # force focus
            messagebox.showwarning("Admin Required", "Please run as Administrator for all tweaks to work.")

        self.installed_packages = self.get_installed_packages()
        self.setup_ui()
    def resize_background(self, event):
        new_width = event.width
        new_height = event.height
        if new_width > 0 and new_height > 0:
            resized = self.bg_image.resize((new_width, new_height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.bg_on_canvas, image=self.bg_photo)




    def get_installed_packages(self):
        try:
            cmd = "Get-AppxPackage | Select-Object -ExpandProperty Name"
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            return result.stdout.splitlines()
        except:
            pass

    def is_package_installed(self, partial_name):
        """التحقق الذكي إذا كانت الحزمة موجودة ضمن القائمة المثبتة"""
        for package in self.installed_packages:
            if partial_name.lower() in package.lower():
                return True
        return False
    def is_tweak_applied(self, hkey, path, name, expected_value):
        """التحقق الذكي مع معالجة حالات عدم وجود المفتاح"""
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return str(value).strip().lower() == str(expected_value).strip().lower()
        except FileNotFoundError:

            return str(expected_value) == "0"
        except Exception:
            return False
        
    def render_bloatware_list(self):
        self.bloatware_vars = []
        for widget in self.tab_bloatware.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self.tab_bloatware, fg_color="transparent", scrollbar_button_color="#1a2540")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        found_any = False
        for text, package in self.bloatware_items:
            if self.is_package_installed(package):
                found_any = True
                var = tk.BooleanVar()
                ctk.CTkCheckBox(
                    scroll,
                    text=f"Remove  {text}",
                    variable=var,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#cdd6f4",
                    fg_color="#00aaff",
                    hover_color="#0077cc",
                    checkmark_color="white",
                    border_color="#1a2540",
                    corner_radius=5
                ).pack(anchor="w", padx=12, pady=3)
                self.bloatware_vars.append((var, package))

        if not found_any:
            ctk.CTkLabel(
                scroll,
                text="✅  System is clean — no bloatware found!",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#00ff88"
            ).pack(pady=30)



    def render_tweaks_list(self):
        for widget in self.tab_tweaks.winfo_children():
            widget.destroy()
        self.tweak_vars = []

        scroll = ctk.CTkScrollableFrame(self.tab_tweaks, fg_color="transparent", scrollbar_button_color="#1a2540")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        for text, func, reg_info in self.tweaks_list:
            should_show = False
            if reg_info == "ALWAYS" or reg_info is None:
                should_show = True
            elif isinstance(reg_info, tuple):
                if not self.is_tweak_applied(*reg_info):
                    should_show = True

            if should_show:
                var = tk.BooleanVar()
                ctk.CTkCheckBox(
                    scroll,
                    text=text,
                    variable=var,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#cdd6f4",
                    fg_color="#00aaff",
                    hover_color="#0077cc",
                    checkmark_color="white",
                    border_color="#1a2540",
                    corner_radius=5
                ).pack(anchor="w", padx=12, pady=5)
                self.tweak_vars.append((var, func))

    def render_permanent_list(self):
        for widget in self.tab_permanent.winfo_children():
            widget.destroy()
        self.permanent_vars = []

        scroll = ctk.CTkScrollableFrame(self.tab_permanent, fg_color="transparent", scrollbar_button_color="#1a2540")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        for text, func, reg_info in self.permanent_list:
            show_option = False
            if reg_info == "ALWAYS" or reg_info is None:
                show_option = True
            elif isinstance(reg_info, tuple):
                hkey, path, name, expected_val = reg_info
                if not self.is_tweak_applied(hkey, path, name, expected_val):
                    show_option = True

            if show_option:
                var = tk.BooleanVar()
                ctk.CTkCheckBox(
                    scroll,
                    text=text,
                    variable=var,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#f5c2e7",
                    fg_color="#cc3355",
                    hover_color="#991133",
                    checkmark_color="white",
                    border_color="#1a2540",
                    corner_radius=5
                ).pack(anchor="w", padx=12, pady=5)
                self.permanent_vars.append((var, func))

    def render_restore_list(self):
        for widget in self.tab_restore.winfo_children():
            widget.destroy()
        self.restore_vars = []

        scroll = ctk.CTkScrollableFrame(self.tab_restore, fg_color="transparent", scrollbar_button_color="#1a2540")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        for text, func, reg_info in self.restore_list:
            show_option = False
            if reg_info is None or reg_info == "ALWAYS":
                show_option = True
            elif isinstance(reg_info, tuple):
                hkey, path, name, default_val = reg_info
                if not self.is_tweak_applied(hkey, path, name, default_val):
                    show_option = True

            if show_option:
                var = tk.BooleanVar()
                ctk.CTkCheckBox(
                    scroll,
                    text=text,
                    variable=var,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#fab387",
                    fg_color="#e06c00",
                    hover_color="#b35500",
                    checkmark_color="white",
                    border_color="#1a2540",
                    corner_radius=5
                ).pack(anchor="w", padx=12, pady=5)
                self.restore_vars.append((var, func))

        if not self.restore_vars:
            ctk.CTkLabel(
                scroll,
                text="✅  All settings are at Windows defaults.",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#00ff88"
            ).pack(pady=30)

    def refresh_system_tab(self):
        # Clear the tab
        for child in self.tab_system.winfo_children():
            child.destroy()
        # Re-build the content
        self.build_system_info_tab()
    def render_About_List(self):
            for widget in self.tab_About.winfo_children():
                widget.destroy()

            main_frame = ctk.CTkFrame(self.tab_About, fg_color="transparent")
            main_frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(
                main_frame,
                text="💡",
                font=ctk.CTkFont(size=50)
            ).pack(pady=(0, 10))

            ctk.CTkLabel(
                main_frame,
                text="IMPORTANT NOTE",
                font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                text_color="#00aaff" # نفس لون تطبيقك الأساسي
            ).pack(pady=10)

            note_text = "When U Disable Gaming Tweaks The Mouse\nAnd Animation Will Back To default"
            
            self.label_note = ctk.CTkLabel(
                main_frame,
                text=note_text,
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="normal"),
                text_color="#cdd6f4", 
                justify="center",
                wraplength=500    
            )
            self.label_note.pack(pady=20)

            ctk.CTkFrame(
                main_frame, 
                height=2, 
                width=200, 
                fg_color="#1a2540"
            ).pack(pady=10)
    def set_reg(self, hkey, path, name, value, reg_type):
        try:
            key = winreg.CreateKeyEx(hkey, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, name, 0, reg_type, value)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to set registry {name}: {e}")
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def setup_ui(self):

        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(14, 0))


        # Tab Control

        self.tabview = ctk.CTkTabview(
            self.root,
            fg_color="#0d1220",
            segmented_button_fg_color="#0a0e1a",
            segmented_button_selected_color="#00aaff",
            segmented_button_selected_hover_color="#0088cc",
            segmented_button_unselected_color="#0a0e1a",
            segmented_button_unselected_hover_color="#111827",
            text_color="white",
            text_color_disabled="#445566",
            corner_radius=12,
            border_width=1,
            border_color="#1a2540"
        )
        self.tabview.pack(expand=True, fill="both", padx=16, pady=(0, 8))

        self.tabview.add("💻  System")
        self.tab_system = self.tabview.tab("💻  System")
        self.tab_system.configure(fg_color="#0d1220")
        self.build_system_info_tab()
        self.tabview.add("🗑  Bloatware")
        self.tabview.add("⚙  Tweaks")
        self.tabview.add("🔒  Permanent")
        self.tabview.add("♻  Restore")
        self.tabview.add("About Tweaks")

        self.tab_bloatware = self.tabview.tab("🗑  Bloatware")
        self.tab_tweaks    = self.tabview.tab("⚙  Tweaks")
        self.tab_permanent = self.tabview.tab("🔒  Permanent")
        self.tab_restore   = self.tabview.tab("♻  Restore")
        self.tab_About = self.tabview.tab("About Tweaks")
        ctk.CTkLabel(
            header_frame,
            text="⚡  Basic Tweaker",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#00aaff"
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="V4.5",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#445566"
        ).pack(side="left", padx=(6, 0), pady=(6, 0))

        ctk.CTkFrame(self.root, height=2, fg_color="#00aaff", corner_radius=0).pack(fill="x", padx=20, pady=(6, 8))

        for tab in [self.tab_bloatware, self.tab_tweaks, self.tab_permanent, self.tab_restore, self.tab_About]:
            tab.configure(fg_color="#0d1220")


        # --- Bloatware Tab ---
        self.bloatware_vars = []
        self.bloatware_items = [
            ("Cortana", "Microsoft.549981C3F5F10"),
            ("Microsoft News", "Microsoft.BingNews"),
            ("Weather App", "Microsoft.BingWeather"),
            ("Xbox App", "Microsoft.XboxApp"),
            ("Your Phone", "Microsoft.YourPhone"),
            ("Solitaire", "Microsoft.MicrosoftSolitaireCollection"),
            ("Maps", "Microsoft.WindowsMaps"),
            ("Get Help", "Microsoft.GetHelp"),
            ("Office Hub", "Microsoft.MicrosoftOfficeHub"),
            ("OneNote", "Microsoft.Office.OneNote"),
            ("Skype", "Microsoft.SkypeApp"),
            ("Mixed Reality", "Microsoft.MixedReality.Portal"),
            ("Feedback Hub", "Microsoft.WindowsFeedbackHub"),
            ("Wallet", "Microsoft.Wallet"),
            ("People", "Microsoft.People"),
            ("Groove Music", "Microsoft.ZuneMusic"),
            ("Movies & TV", "Microsoft.ZuneVideo"),
            ("Paint 3D", "Microsoft.MSPaint"),
            ("3D Viewer", "Microsoft.Microsoft3DViewer"),
            ("Sticky Notes", "Microsoft.MicrosoftStickyNotes"),
            ("Tips", "Microsoft.Getstarted"),
            ("Power Automate", "Microsoft.PowerAutomateDesktop"),
            ("Clipchamp", "Microsoft.Clipchamp"),
            ("To Do", "Microsoft.Todos"),
            ("Bing Sports", "Microsoft.BingSports"),
            ("Bing Finance", "Microsoft.BingFinance"),
            ("Mail and Calendar", "microsoft.windowscommunicationsapps"),
            ("Outlook", "Microsoft.OutlookForWindows"),
            ("Xbox Game Speech", "Microsoft.XboxGameSpeechWindow"),
            ("OneNote Windows 10", "Microsoft.Office.OneNote"),

            ("Disney+", "DisneyPlus"),
            ("Spotify", "SpotifyAB.SpotifyMusic"),
            ("Netflix", "4DF9E0F8.Netflix"),
            ("Instagram", "Facebook.Instagram"),
            ("TikTok", "TikTok"),
            ("Amazon", "AmazonVideo.PrimeVideo"),
            ("McAfee Personal Security", "McAfeeInc.McAfeePersonalSecurity"),
            ("Norton Security", "NortonLifeLock.NortonSecurity"),
            ("LinkedIn", "Microsoft.LinkedInForWindows"),
            ("Duolingo", "Duolingo-Inc.Duolingo"),
            ("Adobe Express", "AdobeSystemsIncorporated.AdobeExpress"),
            ("Picsart", "PicsArt-Inc.PicsartPhotoEditor"),
            ("HP Smart", "AD2F1837.HPSmart"),
            ("HP Documentation", "AD2F1837.HPDocumentation"),
            ("Dell Digital Delivery", "DellInc.DellDigitalDelivery"),
            ("Dell SupportAssist", "DellInc.SupportAssistforPCs"),
            ("Lenovo Welcome", "Lenovo.LenovoWelcome"),
            ("Asus Aura", "Asus.AsusAura"),
            ("CyberLink PowerDVD", "CyberLinkCorp.PowerDVD"),
            ("Dropbox", "Dropbox.Dropbox"),
            ("WhatsApp", "Microsoft.WhatsAppDesktop"),
            ("Print 3D", "Microsoft.Print3D"),
            ("Family", "Microsoft.MicrosoftFamilyFeatures"),
            ("Dev Home", "Microsoft.Windows.DevHome"),
            ("Quick Assist", "MicrosoftCorporationII.QuickAssist"),
            ("Snipping Tool", "Microsoft.ScreenSketch"),
            ("Windows Clock", "Microsoft.WindowsAlarms"),
            ("Windows Camera", "Microsoft.WindowsCamera"),
            ("Windows Calculator", "Microsoft.WindowsCalculator"),
            ("Sound Recorder", "Microsoft.WindowsSoundRecorder"),
            ("Power BI", "Microsoft.MicrosoftPowerBIDesktop"),
            ("Microsoft Teams", "MicrosoftTeams*"),
            ("WhatsApp", "Microsoft.WhatsAppDesktop"),
            ("LinkedIn", "Microsoft.LinkedInForWindows"),
        ]

        self.render_bloatware_list()


        # --- Tweaks Tab ---
        self.tweak_vars = []
        self.tweaks_list = [
            ("Disable Location Tracking", self.disable_location, (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location", "Value", "Deny")),
            ("Disable Advertising ID", self.disable_ads_id, (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", 0)),
            ("Disable Feedback Notifications", self.disable_feedback, (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", 0)),
            ("Disable Windows Tips & Tricks", self.disable_tips, (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SoftLandingEnabled", 0)),
            ("Disable Handwriting Data Collection", self.disable_handwriting, (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Input\TIPC", "Enabled", 0)),
            ("Disable Error Reporting", self.disable_error_reporting, (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", 1)),
            ("Disable Remote Assistance", self.disable_remote_assist, (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Remote Assistance", "fAllowToGetHelp", 0)),
            ("Disable Telemetry Data Collection",     self.disable_telemetry,         (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0)),
            ("Disable Tailored Experiences",           self.disable_tailored_exp,      (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", 0)),
            ("Disable Lock Screen Notifications",      self.disable_lockscreen_notif,  (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "LockScreenToastEnabled", 0)),
            ("Create System Restore Point", self.create_restore_point, "ALWAYS")
            ]

        self.render_tweaks_list()

        self.permanent_list = [
            ("Gaming Tweaks", self.apply_multimedia_tweaks,None),
            ("Disable Unnecessary Services (use it with Win 10 Services Disable if u are in win 10)", self.disable_services, (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4)),
            ("Win 10 Service Disable", self.disable_win10_services, None),
            ("Mouse Tweaks", self.permanent_optimizations, None),
            ("Disable Animation", self.AnimeDis, None),
            ("CPU Power Tweaks(Risk)", self.apply_cpu_power_tweaks, None),
            ("Import LowLatency Gaming Power Plan", self.import_custom_power_plan, None),
            ("Disable Xbox Services", self.disable_Xbox_Services, (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\XblAuthManager", "Start", 4)),
            ("Disable Bittlocker Services", self.disable_Bitlocker_Services, None),
            ("Delete Xbox Apps", self.remove_xbox_apps, None),
            ("Restore Windows 10 Classic Context Menu", self.enable_classic_context_menu, (winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "", "")),
            ("Add Basic Tweaks Options To Right-Click", self.add_context_menu_tools, None),
            ("Debloat Microsoft Edge Browser", self.remove_microsoft_edge, (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msedge.exe", "Debugger", "systray.exe"))
        ]
        self.render_permanent_list()
        
        self.restore_list = [
            ("Disable Gaming Tweaks", self.restore_multimedia_defaults, None),            
            ("Win 10 Service Restore", self.Restore_win10, None),
            ("Restore Services (Default)", self.restore_services, None),
            ("Restore Bitlocker Services (Default)", self.Enable_Bitlocker, None),
            ("Restore Xbox Services (Default)", self.restore_Xbox_services, None),
            ("Restore CPU Power Tweaks", self.restore_cpu_power_tweaks, None),
            ("Remove Custom Power Plan", self.remove_custom_power_plan, None),
            ("Restore Xbox Apps (Default)", self.restore_xbox_apps, None),
            ("Restore Windows 11 Modern Context Menu", self.restore_windows11_context_menu, (winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}", "", "NOT_FOUND")),
            ("Enable Microsoft Edge (Unblock)", self.restore_edge, (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msedge.exe", "Debugger", "")),
            ("Remove Basic Tweaks Options from Right-Click", self.remove_context_menu_tools, None),
        ]

        
        self.render_restore_list()
        self.render_About_List()
        # Apply Button
        ctk.CTkButton(
            self.root,
            text="⚡  Apply Tweaks",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#00aaff",
            hover_color="#0077cc",
            text_color="white",
            corner_radius=10,
            height=44,
            command=self.apply_changes
        ).pack(fill="x", padx=30, pady=(4, 16))
    def apply_changes(self):
        # 1. جمع المهام المحددة
        tasks = []
        for var, package in self.bloatware_vars:
            if var.get(): tasks.append(("bloatware", package))
        for var, func in self.tweak_vars:
            if var.get(): tasks.append(("func", func))
        for var, func in self.permanent_vars:
            if var.get(): tasks.append(("func", func))
        for var, func in self.restore_vars:
            if var.get(): tasks.append(("func", func))

        if not tasks:
            messagebox.showinfo("Alert", "Please Choose One of tasks to do")
            return

        progress_win = ctk.CTkToplevel(self.root)
        progress_win.title("Process Applying...")
        progress_win.geometry("400x200")
        progress_win.attributes("-topmost", True) 
        progress_win.grab_set() 

        label_status = ctk.CTkLabel(progress_win, text="بدء العمليات...", font=("Segoe UI", 13))
        label_status.pack(pady=20)

        progress_bar = ctk.CTkProgressBar(progress_win, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        label_percent = ctk.CTkLabel(progress_win, text="0%")
        label_percent.pack()

        CREATE_NO_WINDOW = 0x08000000

        total_tasks = len(tasks)
        
        for index, (task_type, task_data) in enumerate(tasks):
            current_step = (index + 1) / total_tasks
            
            if task_type == "bloatware":
                label_status.configure(text=f"Removing: {task_data}")
            else:
                label_status.configure(text=f"Applying: {task_data.__name__}")

            progress_bar.set(current_step)
            label_percent.configure(text=f"{int(current_step * 100)}%")
            progress_win.update() 

            # تنفيذ المهمة فعلياً
            try:
                if task_type == "bloatware":
                    cmd = f"Get-AppxPackage *{task_data}* | Remove-AppxPackage"
                    subprocess.run(["powershell", "-Command", cmd], 
                                 capture_output=True, 
                                 creationflags=CREATE_NO_WINDOW,
                                 check=False)
                else:
                    task_data()
            except Exception as e:
                print(f"Error executing {task_data}: {e}")

        progress_win.destroy() 
        
        self.refresh_all_lists() 
        
        if not fix_windowed_presentmode:
            messagebox.showinfo("✅ Done", f"Applied {total} tweaks successfully!")

    def refresh_all_lists(self):
        self.installed_packages = self.get_installed_packages()
        self.render_bloatware_list()
        self.render_tweaks_list()
        self.render_permanent_list()
        self.render_restore_list()
        

# DEL
    def remove_package(self, package_name):
        CREATE_NO_WINDOW = 0x08000000
        cmd = f"Get-AppxPackage *{package_name}* | Remove-AppxPackage"
        subprocess.run(["powershell", "-Command", cmd], 
                     capture_output=True, 
                     creationflags=CREATE_NO_WINDOW)


    def build_system_info_tab(self):
            for child in self.tab_system.winfo_children():
                child.destroy()

            scroll = ctk.CTkScrollableFrame(self.tab_system, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=6, pady=6)

            def info_row(label, value, color="#cdd6f4"):
                row = ctk.CTkFrame(scroll, fg_color="#111827", corner_radius=8)
                row.pack(fill="x", padx=8, pady=3)
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont("Segoe UI", 12),
                            text_color="#445566", width=200, anchor="w").pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(row, text=str(value), font=ctk.CTkFont("Segoe UI", 12, weight="bold"),
                            text_color=color, anchor="w").pack(side="left", padx=4)

            try:
                cmd = 'powershell "(Get-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\').CurrentBuild + \'.\' + (Get-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\').UBR"'
                res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                build_full = res.stdout.strip()

                info_row("Windows Build", build_full)
            except:
                info_row("Windows Build", "N/A")


            cpu_name = "Unknown CPU"
            try:
                import winreg
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(reg_key, "ProcessorNameString")[0].strip()
            except:
                cpu_name = platform.processor()
            
            info_row("CPU", cpu_name)
            info_row("CPU Cores", f"{psutil.cpu_count(logical=False)} Physical / {psutil.cpu_count()} Logical")

            gpu_name = "Detecting..."
            try:
                ps_cmd = 'powershell "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"'
                gpu_res = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True)
                gpu_out = gpu_res.stdout.strip()
                
                if gpu_out:
                    gpu_name = gpu_out.replace("\n", " / ")
                else:
                    gpu_res = subprocess.run("wmic path win32_videocontroller get caption", capture_output=True, text=True, shell=True)
                    gpu_lines = [l.strip() for l in gpu_res.stdout.splitlines() if l.strip() and "Caption" not in l]
                    gpu_name = gpu_lines[0] if gpu_lines else "GPU Not Found"
            except:
                gpu_name = "Detection Error"
                
            info_row("GPU", gpu_name)

            ram = psutil.virtual_memory()
            ram_total = f"{ram.total / (1024**3):.1f} GB"
            ram_used  = f"{ram.used  / (1024**3):.1f} GB"
            ram_pct   = ram.percent
            ram_color = "#ff5555" if ram_pct > 80 else "#ffaa00" if ram_pct > 60 else "#00ff88"
            info_row("RAM Total", ram_total)
            info_row("RAM Used", f"{ram_used} ({ram_pct}%)", ram_color)

            try:
                disk = psutil.disk_usage("C:\\")
                info_row("Disk C: Free", f"{disk.free/(1024**3):.1f} GB / {disk.total/(1024**3):.1f} GB")
            except: pass

            import datetime
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
            info_row("Uptime", f"{int(uptime.total_seconds() // 3600)}h {int((uptime.total_seconds() % 3600) // 60)}m")

            is_admin = self.is_admin()
            info_row("Permissions", "✅ Admin" if is_admin else "❌ Not Admin", "#00ff88" if is_admin else "#ff5555")

            ctk.CTkButton(
                scroll, text="🔄  Refresh Info", height=36,
                fg_color="#1a2540", hover_color="#223060",
                command=self.refresh_system_tab
            ).pack(pady=(10, 4))



    def disable_telemetry(self):
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0, winreg.REG_DWORD)
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", 0, winreg.REG_DWORD)
    def disable_lockscreen_notif(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "LockScreenToastEnabled", 0, winreg.REG_DWORD)
    def disable_tailored_exp(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", 0, winreg.REG_DWORD)


    def remove_xbox_apps(self):
        apps = [
            "Microsoft.XboxApp",
            "Microsoft.XboxGamingOverlay",
            "Microsoft.XboxGameOverlay",
            "Microsoft.XboxSpeechToTextOverlay",
            "Microsoft.XboxIdentityProvider",
            "Microsoft.GamingApp",
            "Microsoft.Xbox.TCUI",
            "Microsoft.XboxDevices",
        ]
        success, failed = [], []
        for app in apps:
            try:
                cmd = f"Get-AppxPackage -AllUsers *{app}* | Remove-AppxPackage -AllUsers"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                success.append(app)
                print(f"[OK] Removed: {app}")
            except Exception as e:
                failed.append(app)
                print(f"[ERROR] {app}: {e}")

        msg = f"✅ Removed ({len(success)}):\n" + "\n".join(f"  • {s}" for s in success)
        if failed:
            msg += f"\n\n❌ Failed ({len(failed)}):\n" + "\n".join(f"  • {f}" for f in failed)
        messagebox.showinfo("Remove Xbox Apps", msg)
    def restore_xbox_apps(self):
        apps = [
            "Microsoft.XboxApp",
            "Microsoft.XboxGamingOverlay",
            "Microsoft.XboxGameOverlay",
            "Microsoft.XboxSpeechToTextOverlay",
            "Microsoft.XboxIdentityProvider",
            "Microsoft.GamingApp",
        ]
        success, failed = [], []
        for app in apps:
            try:
                cmd = f"Get-AppxPackage -AllUsers *{app}* | Foreach {{Add-AppxPackage -DisableDevelopmentMode -Register \"$($_.InstallLocation)\\AppXManifest.xml\"}}"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    success.append(app)
                else:
                    # fallback: reinstall from store
                    cmd2 = f"Get-AppxPackage -allusers *{app}* | Foreach {{Add-AppxPackage -register \"$($_.InstallLocation)\\appxmanifest.xml\" -DisableDevelopmentMode}}"
                    subprocess.run(["powershell", "-Command", cmd2], capture_output=True)
                    success.append(app)
            except Exception as e:
                failed.append(app)
                print(f"[ERROR] {app}: {e}")

        msg = f"✅ Restored ({len(success)}):\n" + "\n".join(f"  • {s}" for s in success)
        if failed:
            msg += f"\n\n❌ Failed ({len(failed)}):\n" + "\n".join(f"  • {f}" for f in failed)
        messagebox.showinfo("Restore Xbox Apps", msg)
    def apply_multimedia_tweaks(self):
        try:
            base_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"

            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, base_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0x0000000a)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0x0000000a)  # Keep 10 for gaming
            winreg.CloseKey(key)


            mem_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, mem_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 0x00000000)
            winreg.SetValueEx(key, "DisablePagingExecutive", 0, winreg.REG_DWORD, 0x00000001)  # KEEP - good for performance
            winreg.CloseKey(key)


            game_path = r"SOFTWARE\Microsoft\GameBar"
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, game_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 0x00000001)
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 0x00000001)
            winreg.CloseKey(key)

            io_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\I/O System"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, io_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "CountOperations", 0, winreg.REG_DWORD, 0x00000000)
            winreg.CloseKey(key)

            messagebox.showinfo("✅ Gaming Tweaks", "Safe gaming tweaks applied!\n\nRemoved aggressive GPU settings that caused 100% usage.")
            print("Safe gaming tweaks applied - no GPU forcing")


        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", f"Failed: {e}")




    def add_context_menu_tools(self):
            try:
                # ── Main Category: Basic Tweaks Option ───────────────────────
                main_path = r"SOFTWARE\Classes\DesktopBackground\Shell\BasicTweaks"
                main_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, main_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(main_key, "MUIVerb", 0, winreg.REG_SZ, "🛠️ Basic Tweaks Option")
                winreg.SetValueEx(main_key, "SubCommands", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(main_key, "Icon", 0, winreg.REG_SZ, "shell32.dll,238") # Tools icon
                winreg.CloseKey(main_key)

                # Define the sub-shell path where all items will live
                sub_shell_path = main_path + r"\Shell"

                # ── 1. Power Plan Sub-Menu ──────────────────────────────────
                pp_path = sub_shell_path + r"\PowerPlan"
                pp_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, pp_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(pp_key, "MUIVerb", 0, winreg.REG_SZ, "⚡ Power Plan")
                winreg.SetValueEx(pp_key, "SubCommands", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(pp_key, "Icon", 0, winreg.REG_SZ, "powercpl.dll,0")
                winreg.CloseKey(pp_key)

                plans = [
                    ("Balanced",            "381b4222-f694-41f0-9685-ff5bb260df2e"),
                    ("High Performance",    "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"),
                    ("Power Saver",         "a1841308-3541-4fab-bc81-f71556f20b4a"),
                ]

                for name, guid in plans:
                    plan_key_path = pp_path + rf"\Shell\{name}"
                    p_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, plan_key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(p_key, "MUIVerb", 0, winreg.REG_SZ, name)
                    winreg.CloseKey(p_key)

                    p_cmd_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, plan_key_path + r"\command", 0, winreg.KEY_SET_VALUE)
                    
                    if name == "Ultimate Performance":
                        cmd = f'cmd /c "powercfg -duplicatescheme {guid} && powercfg /setactive {guid}"'
                    else:
                        cmd = f'powercfg /setactive {guid}'
                        
                    winreg.SetValueEx(p_cmd_key, "", 0, winreg.REG_SZ, cmd)
                    winreg.CloseKey(p_cmd_key)

                # ── 2. Temp Files Cleaner ───────────────────────────────────
                temp_path = sub_shell_path + r"\TempCleaner"
                temp_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, temp_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(temp_key, "MUIVerb", 0, winreg.REG_SZ, "🗑️ Clean Temp Files")
                winreg.SetValueEx(temp_key, "Icon", 0, winreg.REG_SZ, "shell32.dll,141")
                winreg.CloseKey(temp_key)

                ps_script = (
                    "powershell -WindowStyle Hidden -Command \"& {"
                    "$paths = @($env:TEMP, $env:TMP, 'C:\\Windows\\Temp', 'C:\\Windows\\Prefetch');"
                    "$total = 0;"
                    "foreach ($p in $paths) {"
                        "if (Test-Path $p) {"
                            "$items = Get-ChildItem -Path $p -Recurse -ErrorAction SilentlyContinue;"
                            "foreach ($i in $items) { if ($i -is [System.IO.FileInfo]) { $total += $i.Length } };"
                            "Remove-Item -Path \\\"$p\\*\\\" -Force -Recurse -ErrorAction SilentlyContinue"
                        "}"
                    "};"
                    "$mb = [Math]::Round($total / 1MB, 2);"
                    "[System.Windows.Forms.MessageBox]::Show(\\\"✅ Basic Tweaker V4.2`n`nSuccessfully freed: $mb MB\\\", 'Cleanup Complete')}\""
                )

                temp_cmd_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, temp_path + r"\command", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(temp_cmd_key, "", 0, winreg.REG_SZ, ps_script)
                winreg.CloseKey(temp_cmd_key)

                # ── 4. LowLatency Power Plan  ──────────
                pl_result = subprocess.run(["powercfg", "/list"], capture_output=True, text=True)
                plan_guid = None
                for line in pl_result.stdout.splitlines():
                    if "LowLatency" in line:
                        m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", line, re.IGNORECASE)
                        if m:
                            plan_guid = m.group(0)
                            break

                if plan_guid:
                    ll_path = sub_shell_path + r"\LLPlan"
                    ll_key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ll_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(ll_key, "MUIVerb", 0, winreg.REG_SZ, "⚡ Activate LowLatency Plan")
                    winreg.SetValueEx(ll_key, "Icon",    0, winreg.REG_SZ, "powercpl.dll,0")
                    winreg.CloseKey(ll_key)

                    ll_cmd = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ll_path + r"\command", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(ll_cmd, "", 0, winreg.REG_SZ, f'powercfg /setactive {plan_guid}')
                    winreg.CloseKey(ll_cmd)

                messagebox.showinfo("✅ Success", "Context menu updated!...")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update menu: {e}")

    def import_custom_power_plan(self):
        try:
            pow_file = resource_path("LLG-CΞRT1F1ΞD.pow")
            
            result = subprocess.run(
                ["powercfg", "-import", pow_file],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                messagebox.showerror("Error", f"Failed to import: {result.stderr}")
                return
            
            match = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", 
                            result.stdout, re.IGNORECASE)
            
            if match:
                guid = match.group(0)
                
                subprocess.run(
                    ["powercfg", "/changename", guid, "⚡ LowLatency Gaming Plan"],
                    capture_output=True
                )
                
                subprocess.run(
                    ["powercfg", "/setactive", guid],
                    capture_output=True
                )
                
                messagebox.showinfo("✅ Done", 
                    f"Power Plan imported and activated!\n"
                    f"Name: ⚡ LowLatency Gaming Plan\n"
                    f"GUID: {guid}")
            else:
                messagebox.showwarning("⚠️", "Imported but couldn't extract GUID.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")


    def remove_custom_power_plan(self):
        try:
            result = subprocess.run(
                ["powercfg", "/list"],
                capture_output=True, text=True
            )
            
            for line in result.stdout.splitlines():
                if "LowLatency" in line or "LLG" in line or "CERT" in line:
                    match = re.search(
                        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                        line, re.IGNORECASE
                    )
                    if match:
                        guid = match.group(0)
                        subprocess.run(["powercfg", "/setactive", 
                            "381b4222-f694-41f0-9685-ff5bb260df2e"], capture_output=True)
                        subprocess.run(["powercfg", "-delete", guid], capture_output=True)
                        messagebox.showinfo("✅ Done", "Custom power plan removed.")
                        return
                        
            messagebox.showinfo("ℹ️", "Custom power plan not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")


    def remove_context_menu_tools(self):
        try:
            paths = [
                r"SOFTWARE\Classes\DesktopBackground\Shell\BasicTweaks",
                r"SOFTWARE\Classes\DesktopBackground\Shell\PowerPlan",
                r"SOFTWARE\Classes\DesktopBackground\Shell\RAMCleaner",
                r"SOFTWARE\Classes\DesktopBackground\Shell\BasicCleaner",
            ]
            for path in paths:
                subprocess.run(["reg", "delete", f"HKLM\\{path}", "/f"], capture_output=True)

            messagebox.showinfo("✅ Done", "Right-click menu entries removed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")


    def show_result_window(self, title, success, failed):
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("480x500")
        win.resizable(False, False)
        win.configure(fg_color="#0d1220")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text=title,
            font=ctk.CTkFont("Segoe UI", 14, weight="bold"),
            text_color="#00aaff"
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            win,
            text=f"✅ Success: {len(success)}    ❌ Failed: {len(failed)}",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color="#cdd6f4"
        ).pack(pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(win, fg_color="#111827", corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        for item in success:
            ctk.CTkLabel(
                scroll,
                text=f"✅  {item}",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color="#00ff88",
                anchor="w"
            ).pack(anchor="w", padx=10, pady=2)

        for item in failed:
            ctk.CTkLabel(
                scroll,
                text=f"❌  {item}",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color="#ff5555",
                anchor="w"
            ).pack(anchor="w", padx=10, pady=2)

        ctk.CTkButton(
            win,
            text="OK",
            width=120,
            height=36,
            fg_color="#00aaff",
            hover_color="#0077cc",
            font=ctk.CTkFont("Segoe UI", 12, weight="bold"),
            command=win.destroy
        ).pack(pady=(0, 16))

        win.bind("<Return>", lambda e: win.destroy())


    def disable_services(self):

        service_window = ctk.CTkToplevel(self.root)
        service_window.title("Select Services to Disable")
        service_window.geometry("950x750")
        service_window.minsize(800, 600)
        service_window.configure(fg_color="#0d1220")
        service_window.grab_set()
        
        service_window.grid_rowconfigure(0, weight=0)
        service_window.grid_rowconfigure(1, weight=1)
        service_window.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(service_window, fg_color="#111827", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="🔧 Service Configuration - Select Services to Disable",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#00aaff"
        ).pack(side="left", padx=15, pady=10)
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        def select_all():
            for var in service_vars:
                var.set(True)
            update_selection_count()
        
        def deselect_all():
            for var in service_vars:
                var.set(False)
            update_selection_count()
        
        ctk.CTkButton(
            btn_frame, text="Select All", width=90, height=30,
            fg_color="#00aaff", hover_color="#0077cc",
            command=select_all
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            btn_frame, text="Deselect All", width=90, height=30,
            fg_color="#445566", hover_color="#334455",
            command=deselect_all
        ).pack(side="left", padx=3)
        
        count_label = ctk.CTkLabel(header, text="Selected: 0 services", font=ctk.CTkFont(size=12), text_color="#88aaff")
        count_label.pack(side="right", padx=15)
        
        warning_frame = ctk.CTkFrame(service_window, fg_color="#331100", corner_radius=8)
        warning_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 5))
        
        ctk.CTkLabel(
            warning_frame,
            text="⚠️ Warning: Disabling critical services may affect system functionality. Only disable services you understand!",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#ffaa44",
            wraplength=850
        ).pack(padx=10, pady=6)
        
        scroll = ctk.CTkScrollableFrame(service_window, fg_color="transparent", scrollbar_button_color="#1a2540")
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        static_services = [
            # Service Name, Display Name, Description
            ("BTAGService", "Bluetooth Audio Gateway Service", "Manages Bluetooth audio devices. DISABLE if you don't use Bluetooth headphones/speakers."),
            ("bthserv", "Bluetooth Support Service", "Core Bluetooth functionality. DISABLE if you never use Bluetooth."),
            ("lfsvc", "Geolocation Service", "Tracks your physical location. DISABLE for privacy."),
            ("DiagTrack", "Connected User Experiences and Telemetry", "Collects usage data and sends to Microsoft. DISABLE for privacy & performance."),
            ("fhsvc", "File History Service", "Automatic file backups. DISABLE if you don't use File History."),
            ("diagsvc", "Diagnostic Execution Service", "Runs diagnostic tools. DISABLE to save resources."),
            ("HvHost", "Hyper-V Host Service", "Core Hyper-V virtualization. DISABLE if no virtual machines."),
            ("PhoneSvc", "Phone Service", "Your Phone app integration. DISABLE if you don't link phone to PC."),
            ("Spooler", "Print Spooler", "Manages print jobs. DISABLE if you never print (saves ~50MB RAM)."),
            ("QWAVE", "Quality Windows Audio Video Experience", "Optimizes audio/video over networks. DISABLE for gaming (reduces latency)."),
            ("SysMain", "SysMain", "Preloads apps into RAM. DISABLE if you have SSD (saves RAM)."),
            ("WbioSrvc", "Windows Biometric Service", "Fingerprint/face recognition. DISABLE if not using Windows Hello."),
            ("wisvc", "Windows Insider Service", "Receives Insider Preview builds. DISABLE if not in Insider Program."),
            ("WMPNetworkSvc", "Windows Media Player Network Sharing Service", "Shares media libraries over network. DISABLE if not needed."),
            ("icssvc", "Internet Connection Sharing", "Shares internet with other devices. DISABLE for single PC."),
            ("SharedAccess", "Internet Connection Sharing (ICS)", "Same as above. DISABLE if not sharing internet."),
            ("WerSvc", "Windows Error Reporting Service", "Sends crash reports to Microsoft. DISABLE for privacy."),
            ("PcaSvc", "Program Compatibility Assistant Service", "Checks app compatibility. DISABLE to save ~30MB RAM."),
            ("wercplsupport", "Problem Reports and Solutions Control Panel Support", "Manages problem reports. DISABLE to stop error reporting."),
            ("MapsBroker", "Downloaded Maps Manager", "Downloads offline maps. DISABLE if you don't use Maps app."),
            ("dmwappushservice", "Device Management WAP Push Service", "Push notifications for device management. DISABLE for privacy."),
            ("LanmanServer", "Server", "File/printer sharing. DISABLE if you don't share files on network."),
            ("LanmanWorkstation", "Workstation", "Access network files. ⚠️ CAUTION: Needed for network drives!"),
            ("SessionEnv", "Remote Desktop Configuration", "RDP configuration. DISABLE if not using Remote Desktop."),
            ("TermService", "Remote Desktop Services", "Core Remote Desktop service. DISABLE if not using RDP."),
            ("UmRdpService", "Remote Desktop Services UserMode Port Redirector", "RDP user session management. DISABLE if not using RDP."),
            ("WiaRpc", "Still Image Acquisition Events", "Scanner/camera support. DISABLE if no scanners/cameras."),
            ("SEMgrSvc", "Payments and NFC/SE Manager", "NFC payments. DISABLE if not using phone payments on PC."),
            ("ScDeviceEnum", "Smart Card Device Enumeration Service", "Finds smart card readers. DISABLE for home users."),
            ("SCardSvr", "Smart Card", "Manages smart card access. DISABLE for home users."),
            ("SCPolicySvc", "Smart Card Removal Policy", "Locks PC when card removed. DISABLE if not using smart cards."),
            ("CloudBackupRestoreSvc", "Cloud Backup and Restore", "Windows cloud backup. DISABLE if using other backup."),
            ("FileSyncHelper", "File Sync Helper", "Helps OneDrive sync files. DISABLE if no OneDrive."),
            ("OneDrive", "OneDrive Updater Service", "OneDrive cloud sync. DISABLE if you don't use OneDrive."),
            ("MicrosoftEdgeElevationService", "Microsoft Edge Elevation Service", "Allows Edge to update. DISABLE to stop auto-updates."),
            ("edgeupdate", "Microsoft Edge Update Service", "Automatic Edge updates. DISABLE to control manually."),
            ("edgeupdatem", "Microsoft Edge Update Service (edgeupdatem)", "Secondary Edge updater. DISABLE same as above."),
            ("PrintNotify", "Printer Extensions and Notifications", "Printer popups and alerts. DISABLE if no printer."),
            ("VaultSvc", "Credential Manager", "Saves passwords. ⚠️ CAUTION: Disabling loses saved passwords!"),
            ("WinRM", "Windows Remote Management (WS-Management)", "Remote command execution. ⚠️ SECURITY RISK - DISABLE!"),
            ("FDResPub", "Function Discovery Resource Publication", "Publishes PC to network. DISABLE for security."),
            ("fdPHost", "Function Discovery Provider Host", "Finds network devices. DISABLE for security."),
            ("WpcMonSvc", "Parental Controls", "Family safety and screen time. DISABLE if not needed."),
            ("InventorySvc", "Windows Inventory Service", "App inventory collection. DISABLE for privacy."),
            ("DsSvc", "Data Sharing Service", "Data sharing between apps. DISABLE if not needed."),
            ("RetailDemoService", "Retail Demo Service", "Demo mode for retail. DISABLE on personal PCs."),
            ("BthAvctpSvc", "AVCTP Service", "Audio/Video control for Bluetooth. DISABLE if no BT audio."),
            ("BthHFSrv", "Bluetooth Handsfree Service", "Handsfree calling profile. DISABLE if no calls on PC."),
            ("BthRcManSvc", "Bluetooth Remote Control Manager", "Manages Bluetooth remotes. DISABLE if no BT remotes."),
            ("WManSvc", "Windows Mobile Hotspot Service", "Creates mobile hotspot. DISABLE if not sharing WiFi."),
            ("DusmSvc", "Data Usage Service", "Tracks network data usage. DISABLE if no data cap."),
            ("diagnosticshub.standardcollector.service", "Microsoft (R) Diagnostics Hub Standard Collector", "Diagnostic data collection. DISABLE for privacy."),
            ("NfcService", "NFC Service", "Near Field Communication. DISABLE if no NFC reader."),
            ("TapiSrv", "Telephony", "Phone/modem support. DISABLE if no dial-up or fax."),
            ("lltdsvc", "Link-Layer Topology Discovery Mapper", "Maps network topology. DISABLE if not needed."),
            ("SSDPSRV", "SSDP Discovery", "Finds UPnP devices. ⚠️ SECURITY RISK - DISABLE!"),
            ("upnphost", "UPnP Device Host", "Hosts UPnP devices. ⚠️ SECURITY RISK - DISABLE!"),
            ("p2psvc", "Peer Networking Grouping", "P2P collaboration. DISABLE for security."),
            ("p2pimsvc", "Peer Networking Identity Manager", "P2P identity management. DISABLE for security."),
            ("PNRPsvc", "Peer Name Resolution Protocol", "P2P name resolution. DISABLE for security."),
            ("PNRPAutoReg", "PNRP Machine Name Publication Service", "Publishes PC name for P2P. DISABLE for security."),
            ("Wecsvc", "Windows Event Collector", "Collects events from other PCs. DISABLE for home users."),
            ("MSiSCSI", "Microsoft iSCSI Initiator Service", "Connects to storage networks. DISABLE if not using iSCSI."),
            ("NetTcpPortSharing", "Net.Tcp Port Sharing Service", "Shares TCP ports for WCF. DISABLE if not needed."),
            ("MSDTC", "Distributed Transaction Coordinator", "Database transactions. DISABLE for home users."),
            ("RemoteRegistry", "Remote Registry", "Remote registry access. ⚠️ SECURITY RISK - DISABLE IMMEDIATELY!"),
            ("WalletService", "Wallet Service", "Digital wallet management. DISABLE if not used."),
            ("embeddedmode", "Embedded Mode", "For embedded devices. DISABLE on desktop PCs."),
            ("EntAppSvc", "Enterprise App Management Service", "Business app management. DISABLE for home users."),
            ("stisvc", "Windows Image Acquisition (WIA)", "Scanner/camera support. DISABLE if no scanners/cameras."),
            ("MixedRealityOpenXRSvc", "Windows Mixed Reality OpenXR Service", "VR headset support. DISABLE if no VR."),
            ("UevAgentService", "User Experience Virtualization Service", "Roams settings between PCs. DISABLE for single PC."),
            ("lmhosts", "TCP/IP NetBIOS Helper", "Legacy NetBIOS support. DISABLE for security."),
            ("SNMPTRAP", "SNMP Trap", "Network monitoring. DISABLE if not managing network."),
            ("RmSvc", "Radio Management Service", "Manages radio on/off. DISABLE if no airplane mode need."),
            
            ("vmickvpexchange", "Hyper-V Data Exchange Service", "Shares data between host and VMs. DISABLE if not using Hyper-V."),
            ("vmicguestinterface", "Hyper-V Guest Service Interface", "VM communication service. DISABLE if not using Hyper-V."),
            ("vmicshutdown", "Hyper-V Shutdown Service", "Allows VMs to shutdown host. DISABLE if not using Hyper-V."),
            ("vmicheartbeat", "Hyper-V Heartbeat Service", "Monitors if VMs are running. DISABLE if not using Hyper-V."),
            ("vmicvmsession", "Hyper-V VM Session Service", "Manages VM sessions. DISABLE if not using Hyper-V."),
            ("vmicrdv", "Hyper-V Remote Desktop Virtualization Service", "Remote access to VMs. DISABLE if not using Hyper-V."),
            ("vmictimesync", "Hyper-V Time Synchronization Service", "Syncs time between host and VMs. DISABLE if not using Hyper-V."),
            ("vmicvss", "Hyper-V Volume Shadow Copy Requestor", "VM backups. DISABLE if not using Hyper-V."),
        ]
        
        service_vars = []
        service_items = []  
        
        def update_selection_count():
            selected = sum(1 for var in service_vars if var.get())
            count_label.configure(text=f"Selected: {selected} services")
        
        for service_name, display_name, description in static_services:
            frame = ctk.CTkFrame(scroll, fg_color="#111827", corner_radius=8)
            frame.pack(fill="x", padx=5, pady=3)
            
            var = tk.BooleanVar()
            service_vars.append(var)
            service_items.append((service_name, display_name))
            
            var.trace('w', lambda *args: update_selection_count())
            
            cb = ctk.CTkCheckBox(
                frame,
                text=f"{display_name}",
                variable=var,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#00aaff",
                fg_color="#00aaff",
                hover_color="#0077cc",
                checkmark_color="white"
            )
            cb.pack(side="left", padx=(10, 5), pady=8)
            
            desc_label = ctk.CTkLabel(
                frame,
                text=description,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#8899aa",
                wraplength=650,
                justify="left"
            )
            desc_label.pack(side="left", padx=(5, 10), pady=8, fill="x", expand=True)
        
        dynamic_service_patterns = [
            ("MessagingService", "Messaging Service", "Handles SMS and chat messaging. DISABLE if you don't use Windows messaging apps."),
            ("OneSyncSvc", "Sync Host Service", "Synchronizes mail, contacts, and calendar. DISABLE if not using built-in mail/calendar apps."),
            ("BluetoothUserService", "Bluetooth User Support Service", "Handles Bluetooth user interactions. DISABLE if you don't use Bluetooth."),
            ("PrintWorkflowUserSvc", "Print Workflow Service", "Manages modern print dialogs. DISABLE if you don't print."),
            ("cbdhsvc", "Clipboard User Service", "Handles cloud clipboard sync. DISABLE if you don't sync clipboard between devices."),
        ]
        
        try:
            base_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services"
            )
            i = 0
            discovered_services = set()  # To avoid duplicates
            
            while True:
                try:
                    sub = winreg.EnumKey(base_key, i)
                    for pattern, display_base, description_base in dynamic_service_patterns:
                        if sub.startswith(pattern) and sub not in discovered_services:
                            discovered_services.add(sub)
                            
                            # Create display name with actual service name
                            display_name = f"{display_base} [{sub}]"
                            
                            frame = ctk.CTkFrame(scroll, fg_color="#112233", corner_radius=8)
                            frame.pack(fill="x", padx=5, pady=3)
                            
                            var = tk.BooleanVar()
                            service_vars.append(var)
                            service_items.append((sub, display_name))
                            
                            var.trace('w', lambda *args: update_selection_count())
                            
                            cb = ctk.CTkCheckBox(
                                frame,
                                text=f"🔍 {display_name}",
                                variable=var,
                                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                text_color="#88aaff",
                                fg_color="#00aaff",
                                hover_color="#0077cc",
                                checkmark_color="white"
                            )
                            cb.pack(side="left", padx=(10, 5), pady=8)
                            
                            # Add note that this is a discovered service
                            desc_text = f"{description_base} (DISCOVERED SERVICE - specific to your system)"
                            
                            desc_label = ctk.CTkLabel(
                                frame,
                                text=desc_text,
                                font=ctk.CTkFont(family="Segoe UI", size=10),
                                text_color="#88aacc",
                                wraplength=630,
                                justify="left"
                            )
                            desc_label.pack(side="left", padx=(5, 10), pady=8, fill="x", expand=True)
                            
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(base_key)
            
            if discovered_services:
                # Add a separator label
                sep_frame = ctk.CTkFrame(scroll, fg_color="#1a2540", height=2)
                sep_frame.pack(fill="x", padx=10, pady=10)
                
                sep_label = ctk.CTkLabel(
                    scroll,
                    text="📌 Discovered Dynamic Services (unique to your system)",
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                    text_color="#ffaa44"
                )
                sep_label.pack(pady=(5, 5))
                
        except Exception as e:
            print(f"[ERROR] Dynamic services discovery: {e}")
        
        bottom_frame = ctk.CTkFrame(service_window, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        def apply_selected_services():
            selected_services = []
            selected_names = []
            for i, var in enumerate(service_vars):
                if var.get():
                    service_name, display_name = service_items[i]
                    selected_services.append(service_name)
                    selected_names.append(display_name)
            
            if not selected_services:
                messagebox.showinfo("No Selection", "Please select at least one service to disable.")
                return
            
            confirm_msg = f"Are you sure you want to disable {len(selected_services)} service(s)?\n\n"
            confirm_msg += "Selected services:\n" + "\n".join(f"• {name}" for name in selected_names[:15])
            if len(selected_services) > 15:
                confirm_msg += f"\n... and {len(selected_services) - 15} more"
            
            if not messagebox.askyesno("Confirm", confirm_msg):
                return
            
            service_window.destroy()
            self.apply_selected_services(selected_services)
        
        ctk.CTkButton(
            bottom_frame,
            text="✅ Apply Selected Services",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00aaff",
            hover_color="#0077cc",
            height=40,
            command=apply_selected_services
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            bottom_frame,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color="#445566",
            hover_color="#334455",
            height=35,
            command=service_window.destroy
        ).pack(fill="x", pady=3)


    def apply_selected_services(self, selected_services):
        """Apply service disabling for selected services only"""
        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []
        
        progress_win = ctk.CTkToplevel(self.root)
        progress_win.title("Disabling Services")
        progress_win.geometry("400x150")
        progress_win.attributes("-topmost", True)
        progress_win.grab_set()
        
        label_status = ctk.CTkLabel(progress_win, text="Disabling services...", font=("Segoe UI", 12))
        label_status.pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(progress_win, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        total = len(selected_services)
        
        for index, service in enumerate(selected_services):
            progress_bar.set((index + 1) / total)
            label_status.configure(text=f"Disabling: {service}")
            progress_win.update()
            
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)  # 4 = Disabled
                winreg.CloseKey(key)
                success.append(service)
            except Exception as e:
                failed.append(f"{service} ({str(e)[:50]})")
        
        progress_win.destroy()
        
        result_msg = f"✅ Services Disabled: {len(success)}\n"
        if success:
            result_msg += "\n" + "\n".join(f"  • {s}" for s in success[:20])
            if len(success) > 20:
                result_msg += f"\n  ... and {len(success) - 20} more"
        
        if failed:
            result_msg += f"\n\n❌ Failed ({len(failed)}):\n" + "\n".join(f"  • {f}" for f in failed)
        
        messagebox.showinfo("Service Configuration Complete", result_msg)


    def disable_win10_services(self):
        """تعطيل خدمات ويندوز 10 غير الضرورية عبر الريجستري"""
        services = [
        ("Fax", "Fax Service"),
        ("DoSvc", "Delivery Optimization"),
        ("wuauserv", "Windows Update Service"),
        ("UsoSvc", "Update Orchestrator Service"),
        ("bits", "Background Intelligent Transfer Service"),
        ("waasmedic", "Windows Update Medic Service")
        ]

        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        warp_installed = os.path.exists(r"C:\Program Files\Cloudflare\Cloudflare WARP\warp-svc.exe")
        if warp_installed:
            confirm = messagebox.askyesno(
                "⚠️ Cloudflare WARP Detected",
                "Will Stop Working When Disable Service.\n\n"
                "Do you want to continue?"
            )
            if not confirm:
                return

        for service, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Disabled: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        dynamic_services = [
            "MessagingService",
            "OneSyncSvc",
            "BluetoothUserService",
            "PrintWorkflowUserSvc",
            "cbdhsvc",
        ]

        try:
            base_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services"
            )
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(base_key, i)
                    for ds in dynamic_services:
                        if sub.startswith(ds):
                            try:
                                key = winreg.CreateKeyEx(
                                    winreg.HKEY_LOCAL_MACHINE,
                                    rf"SYSTEM\CurrentControlSet\Services\{sub}",
                                    0, winreg.KEY_SET_VALUE
                                )
                                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
                                winreg.CloseKey(key)
                                success.append(sub)
                            except Exception as e:
                                failed.append(sub)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(base_key)
        except Exception as e:
            print(f"[ERROR] Dynamic services: {e}")

        self.show_result_window("Disable Services", success, failed)


    def Restore_win10(self):
        services = [
            ("Fax", 3, "Fax Service"),
            ("DoSvc", 2, "Delivery Optimization"),
            ("wuauserv", 3, "Windows Update Service"),
            ("UsoSvc", 2, "Update Orchestrator Service"),
            ("bits", 3, "Background Intelligent Transfer Service"),
            ("waasmedic", 3, "Windows Update Medic Service")
        ]

        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, default_val, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, default_val)
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Restored: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("Restore Services", success, failed)



    def disable_Xbox_Services(self):
        services = [
            # ---- Xbox & Gaming (if not a gamer) ----
            ("XblAuthManager",      "Xbox Live Auth Manager"),
            ("XblGameSave",         "Xbox Live Game Save"),
            ("XboxGipSvc",          "Xbox Accessory Management"),
            ("XboxNetApiSvc",       "Xbox Live Networking"),
            ("GamingServices",      "Gaming Services")
            ]
        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)  # 4 = Disabled
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Disabled: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("Disable Xbox Services", success, failed)  
  


    def disable_Bitlocker_Services(self):
        """تعطيل الخدمات غير الضرورية عبر الريجستري"""
        services = [
            # ---- Xbox & Gaming (if not a gamer) ----
            ("BDESVC",      "BitLocker Drive Encryption Service"),
            ]
        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)  # 4 = Disabled
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Disabled: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("Disable Xbox Services", success, failed)  

    def Enable_Bitlocker(self):
        services = [
            ("BDESVC", 3 , "BitLocker Drive Encryption Service"),
        ]
        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, default_val, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, default_val)
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Restored: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("Enable Wifi", success, failed)

    def restore_services(self):
        services = [
            ("BTAGService",         3, "Bluetooth Audio Gateway"),
            ("bthserv",             3, "Bluetooth Support Service"),
            ("lfsvc",               3, "Geolocation Service"),
            ("DiagTrack",           2, "Connected User Experiences & Telemetry"),
            ("HvHost",              3, "Hyper-V Host"),
            ("vmickvpexchange",     3, "Hyper-V Data Exchange"),
            ("fhsvc",         3,"File History Service"),
            ("vmicguestinterface",  3, "Hyper-V Guest Interface"),
            ("vmicshutdown",        3, "Hyper-V Shutdown"),
            ("vmicheartbeat",       3, "Hyper-V Heartbeat"),
            ("vmicvmsession",       3, "Hyper-V VM Session"),
            ("vmicrdv",             3, "Hyper-V Remote Desktop"),
            ("vmictimesync",        3, "Hyper-V Time Sync"),
            ("vmicvss",             3, "Hyper-V VSS"),
            ("PhoneSvc",            3, "Phone Service"),
            ("Spooler",             2, "Print Spooler"),
            ("QWAVE",               3, "Quality Windows Audio Visual Experience"),
            ("SysMain",             2, "SysMain (Superfetch)"),
            ("WbioSrvc",            3, "Windows Biometric Service"),
            ("wisvc",               3, "Windows Insider Service"),
            ("WMPNetworkSvc",       3, "Windows Media Player Network Sharing"),
            ("icssvc",              3, "Internet Connection Sharing"),
            ("SharedAccess",        3, "Internet Connection Sharing (ICS)"),
            ("WerSvc",              3, "Windows Error Reporting Service"),
            ("PcaSvc",              2, "Program Compatibility Assistant"),
            ("wercplsupport",       3, "Problem Reports Control Panel"),
            ("MapsBroker",          2, "Downloaded Maps Manager"),
            ("RetailDemoService",   4, "Retail Demo Service"),
            ("dmwappushservice",    3, "Device Management WAP Push"),
            ("MessagingService",    3, "Messaging Service"),
            ("OneSyncSvc",          2, "Sync Host Service"),
            ("LanmanServer",        3, "Server (File Sharing)"),
            ("LanmanWorkstation",   2, "Workstation (Network Files)"),
            ("SessionEnv",          3, "Remote Desktop Configuration"),
            ("TermService",         3, "Remote Desktop Services"),
            ("UmRdpService",        3, "Remote Desktop Services UserMode"),
            ("WiaRpc",              3, "Still Image Acquisition"),
            ("SEMgrSvc",            3, "Payments and NFC"),
            ("ScDeviceEnum",        3, "Smart Card Device Enumeration"),
            ("SCardSvr",            3, "Smart Card"),
            ("SCPolicySvc",         3, "Smart Card Removal Policy"),
            ("CloudBackupRestoreSvc", 3, "Cloud Backup and Restore"),
            ("FileSyncHelper",      3, "File Sync Helper"),
            ("OneDrive",            3, "OneDrive Sync"),
            ("MicrosoftEdgeElevationService", 3, "Microsoft Edge Elevation"),
            ("edgeupdate",          2, "Microsoft Edge Update"),
            ("edgeupdatem",         3, "Microsoft Edge Update (m)"),
            ("PrintNotify",         3, "Printer Extensions and Notifications"),
            ("PrintWorkflowUserSvc",3, "Print Workflow Service"),
            ("VaultSvc",            3, "Credential Manager"),
            ("WpcMonSvc",           3, "Parental Controls"),
            ("InventorySvc",        3, "Windows Inventory Service"),
            ("DsSvc",               3, "Data Sharing Service"),
            ("BluetoothUserService",3, "Bluetooth User Support Service"),
            ("BthAvctpSvc",         3, "AVCTP Service"),
            ("BthHFSrv",            3, "Bluetooth Handsfree Service"),
            ("BthRcManSvc",         3, "Bluetooth Remote Control Manager"),
            ("WManSvc",             3, "Windows Mobile Hotspot Service"),
            ("DusmSvc",             2, "Data Usage Service"),
            ("diagnosticshub.standardcollector.service", 3, "Diagnostics Hub Standard Collector"),
            ("NfcService",          3, "NFC Service"),
            ("TapiSrv",             3, "Telephony"),
            ("WinRM",               3, "Windows Remote Management"),
            ("FDResPub",            3, "Function Discovery Resource Pub"),
            ("fdPHost",             3, "Function Discovery Provider"),
            ("diagsvc",             3, "Diagnostic Execution Service"),
            ("lltdsvc",             3, "Link-Layer Topology Discovery"),
            ("SSDPSRV",             3, "SSDP Discovery"),
            ("upnphost",            3, "UPnP Device Host"),
            ("p2psvc",              3, "Peer Networking Grouping"),
            ("p2pimsvc",            3, "Peer Networking Identity Manager"),
            ("PNRPsvc",             3, "Peer Name Resolution Protocol"),
            ("PNRPAutoReg",         3, "PNRP Machine Name Publication"),
            ("Wecsvc",              3, "Windows Event Collector"),
            ("MSiSCSI",             3, "Microsoft iSCSI Initiator"),
            ("NetTcpPortSharing",   4, "Net.Tcp Port Sharing"),
            ("MSDTC",               3, "Distributed Transaction Coordinator"),
            ("RemoteRegistry",      4, "Remote Registry"),
            ("WalletService",       3, "Wallet Service"),
            ("embeddedmode",        4, "Embedded Mode"),
            ("EntAppSvc",           3, "Enterprise App Management"),
            ("stisvc",              3, "Windows Image Acquisition"),
            ("MixedRealityOpenXRSvc",3,"Windows Mixed Reality OpenXR"),
            ("UevAgentService",     4, "User Experience Virtualization"),
            ("lmhosts",             3, "TCP/IP NetBIOS Helper"),
            ("SNMPTRAP",            3, "SNMP Trap"),
            ("RmSvc",               3, "Radio And Airplane mode service"),
        ]

        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, default_val, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, default_val)
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Restored: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("Restore Services", success, failed)

    


    def restore_Xbox_services(self):
        """استعادة الخدمات لقيمها الافتراضية"""
        # 2=Automatic, 3=Manual, 4=Disabled
        services = [
            ("XblAuthManager",      3, "Xbox Live Auth Manager"),
            ("XblGameSave",         3, "Xbox Live Game Save"),
            ("XboxGipSvc",          3, "Xbox Accessory Management"),
            ("XboxNetApiSvc",       3, "Xbox Live Networking"),
            ("GamingServices",      3, "Gaming Services")
        ]

        base = r"SYSTEM\CurrentControlSet\Services"
        success, failed = [], []

        for service, default_val, desc in services:
            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    f"{base}\\{service}",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, default_val)
                winreg.CloseKey(key)
                success.append(desc)
                print(f"[OK] Restored: {desc}")
            except Exception as e:
                failed.append(desc)
                print(f"[ERROR] {desc}: {e}")

        self.show_result_window("restore Xbox Services", success, failed)  

        
    def permanent_optimizations(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects")
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)  # 2 = Adjust for best performance
            winreg.CloseKey(key)

            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse")
            winreg.SetValueEx(key, "MouseTrails",   0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseSpeed",    0, winreg.REG_SZ, "0")  # إيقاف Pointer Precision
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)

            print("Permanent optimizations applied.")
        except Exception as e:
            print(f"Error: {e}")


    def AnimeDis(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects")
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)  # 2 = Adjust for best performance
            winreg.CloseKey(key)

            print("Disable Animation applied.")
        except Exception as e:
            print(f"Error: {e}")

    def enable_classic_context_menu(self):
        path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            subprocess.run("start explorer.exe", shell=True, capture_output=True)
            
            messagebox.showinfo("Success", "تم تحويل القائمة للشكل الكلاسيكي بنجاح!")
        except Exception as e:
            print(f"Error: {e}")

    def create_restore_point(self):
        try:
            print("Create Restore Point....")
            
            cmd = "Checkpoint-Computer -Description 'Optimizer_Backup' -RestorePointType 'MODIFY_SETTINGS'"
            
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "Restore Point Created: Optimizer_Backup")
            else:
                messagebox.showwarning("Alert", "U didnt made an Restore Point.")
        except Exception as e:
            messagebox.showerror("Failed", f"Failed To make Restore Point: {e}")

    def remove_microsoft_edge(self):
        try:
            subprocess.run("taskkill /F /IM msedge.exe /T", shell=True, capture_output=True)
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            disallow_key = winreg.CreateKey(key, "DisallowRun")
            winreg.SetValueEx(disallow_key, "1", 0, winreg.REG_SZ, "msedge.exe")
            
            ifeo_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msedge.exe"
            ifeo_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, ifeo_path)
            winreg.SetValueEx(ifeo_key, "Debugger", 0, winreg.REG_SZ, "systray.exe")
            
            edge_dir = r"C:\Windows\SystemApps\Microsoft.MicrosoftEdge_8wekyb3d8bbwe"
            if os.path.exists(edge_dir):
                try: os.rename(edge_dir, edge_dir + "_disabled")
                except: pass

            messagebox.showinfo("Success", "Microsoft Edge Debloated.")
        except Exception as e:
            messagebox.showerror("Failed", f"Failed to Debloat Edge: {e}")
    def disable_location(self):
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location", "Value", "Deny", winreg.REG_SZ)

    def disable_ads_id(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", 0, winreg.REG_DWORD)

    def disable_feedback(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", 0, winreg.REG_DWORD)


    def disable_tips(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SoftLandingEnabled", 0, winreg.REG_DWORD)

    def disable_handwriting(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, 
                 r"Software\Microsoft\Input\Settings", 
                 "EnableHandwriting", 0, winreg.REG_DWORD)
    def disable_error_reporting(self):
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", 1, winreg.REG_DWORD)



    def disable_remote_assist(self):
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Remote Assistance", "fAllowToGetHelp", 0, winreg.REG_DWORD)



    #RES

    def restore_multimedia_defaults(self):
        """Restore ONLY the settings that your gaming tweaks change"""
        try:
            base_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, base_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0x0000000a)   # 10 (already default, but keep)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0x00000014)     # 20 = Windows DEFAULT (changed from 10)
            winreg.CloseKey(key)

            mem_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, mem_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 0x00000000)         # 0 = default
            winreg.SetValueEx(key, "DisablePagingExecutive", 0, winreg.REG_DWORD, 0x00000000)   # 0 = Windows DEFAULT (changed from 1)
            winreg.CloseKey(key)

            game_path = r"SOFTWARE\Microsoft\GameBar"
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, game_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 0x00000001)        # 1 = default
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 0x00000001)       # 1 = default
            winreg.CloseKey(key)

            io_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\I/O System"
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, io_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "CountOperations", 0, winreg.REG_DWORD, 0x00000001)          # 1 = Windows DEFAULT (changed from 0)
            winreg.CloseKey(key)

            messagebox.showinfo("✅ Restored", "All gaming tweaks have been restored to Windows defaults!\n\n• SystemResponsiveness: 20 (default)\n• DisablePagingExecutive: 0 (default)\n• CountOperations: 1 (default)")
            print("Restored to Windows defaults")

        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", f"Failed to restore: {e}")

    def enable_transparency_reg(self):
        self.set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 1, winreg.REG_DWORD)

    def restore_windows11_context_menu(self):
        path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
        try:
            subprocess.run(['reg', 'delete', f'HKCU\\{path}', '/f'], capture_output=True)
            
            subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            subprocess.run("start explorer.exe", shell=True, capture_output=True)
            
            messagebox.showinfo("Success", "Windows Context Menu back to Defult.")
        except Exception as e:
            print(f"Error: {e}")

    def enable_telemetry_reg(self):
        self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 1, winreg.REG_DWORD)

    def restore_dll_unloading(self):
        try:
            self.set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", 20, winreg.REG_DWORD)
            
            print("System Responsiveness & DLL Unloading restored to default.")
        except Exception as e:
            print(f"Error restoring system responsiveness: {e}")

    def restore_edge(self):
        try:
            path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\msedge.exe"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(key, "Debugger")
            winreg.CloseKey(key)
        except FileNotFoundError:
            # في حال لم تكن القيمة موجودة أصلاً (Edge غير محظور)
            pass
        except Exception as e:
            print(f"Error restoring Edge: {e}")

    def set_reg_value(self, hkey, path, name, value):
        """General registry write function that auto-detects the value type"""
        try:
            key = winreg.CreateKeyEx(hkey, path, 0, winreg.KEY_SET_VALUE)
            if isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to set registry '{name}': {e}")


    def apply_cpu_power_tweaks(self):
        try:
            success, failed = [], []

            tweaks = [
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "0cc5b647-c1df-4637-891a-dec35c318583", "0"],
                "Disable Core Parking"),


                # Processor Performance Boost Mode = Aggressive
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "be337238-0d82-4146-a960-4f3749d470c7", "2"],
                "CPU Boost Mode Aggressive"),


                # Processor Performance Increase Threshold = 10%
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "06cadf0e-64ed-448a-8927-ce7bf90eb35d", "10"],
                "Performance Increase Threshold 10%"),

                # Processor Performance Decrease Threshold = 8%
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "12a0ab44-fe28-4fa9-b3bd-4b64f44960a6", "8"],
                "Performance Decrease Threshold 8%"),

                (["powercfg", "-setactive", "SCHEME_CURRENT"],
                "Apply Changes"),
            ]

            for cmd, desc in tweaks:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    success.append(desc)
                else:
                    failed.append(desc)

            self.show_result_window("CPU Power Tweaks", success, failed)

        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")


    def restore_cpu_power_tweaks(self):
        try:
            success, failed = [], []

            tweaks = [
    # Restore Core Parking
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "0cc5b647-c1df-4637-891a-dec35c318583", "100"],
                "Restore Core Parking"),

                # Restore CPU Boost Mode = Enabled
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "be337238-0d82-4146-a960-4f3749d470c7", "1"],
                "Restore CPU Boost Mode"),

                # Restore Increase Threshold = 40%
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "06cadf0e-64ed-448a-8927-ce7bf90eb35d", "40"],
                "Restore Increase Threshold"),

                # Restore Decrease Threshold = 20%
                (["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "12a0ab44-fe28-4fa9-b3bd-4b64f44960a6", "20"],
                "Restore Decrease Threshold"),

                # Apply Changes
                (["powercfg", "-setactive", "SCHEME_CURRENT"],
                "Apply Changes"),
            ]

            for cmd, desc in tweaks:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    success.append(desc)
                else:
                    failed.append(desc)

            self.show_result_window("Restore CPU Power Tweaks", success, failed)

        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")




if __name__ == "__main__":
    root = ctk.CTk()
    app = WindowsOptimizer(root)
    root.mainloop()