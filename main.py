import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import json
import threading
import time
from datetime import datetime
import subprocess
import sys

class GameConfig:
    """游戏配置管理类"""
    def __init__(self):
        self.config_file = "game_config.json"
        self.default_config = {
            "language": "Chinese",
            "version": "v2.0",
            "window_position": {"x": 100, "y": 100},
            "theme": "dark",
            "auto_launch": False,
            "last_played": "",
            "play_count": 0,
            "chinese_path": r"super_ball-HTMLfile\super_ball-chinese.html",
            "english_path": r"super_ball-HTMLfile\super_ball-english.html"
        }
        self.config_data = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                # 合并默认配置，确保所有键都存在
                for key, value in self.default_config.items():
                    if key not in config_data:
                        config_data[key] = value
                return config_data
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config_data.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config_data[key] = value
        self.save_config()

class AnimationHandler:
    """动画处理类"""
    def __init__(self, master):
        self.master = master
        self.animations = []
    
    def fade_in(self, widget, duration=1000, steps=50):
        """淡入动画"""
        def animate():
            step_time = duration / steps
            alpha_step = 1.0 / steps
            current_alpha = 0.0
            
            for i in range(steps):
                current_alpha += alpha_step
                try:
                    # 模拟透明度效果
                    widget.configure(fg=self._interpolate_color("#666666", "#ffffff", current_alpha))
                    self.master.update()
                    time.sleep(step_time / 1000)
                except:
                    break
        
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()
    
    def _interpolate_color(self, color1, color2, factor):
        """颜色插值"""
        return color2 if factor > 0.5 else color1
    
    def bounce_effect(self, widget, callback=None):
        """弹跳效果"""
        def animate():
            try:
                for scale in [1.1, 1.2, 1.1, 1.0]:
                    time.sleep(0.05)
                    self.master.update()
                if callback:
                    callback()
            except:
                pass
        
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()

class ThemeManager:
    """主题管理类"""
    def __init__(self):
        self.themes = {
            "dark": {
                "bg": "#1e1e2f",
                "fg": "#ffffff",
                "button_bg": "#61dafb",
                "button_fg": "#ffffff",
                "button_active": "#21a1f1",
                "frame_bg": "#2d2d44",
                "accent": "#ff6b6b"
            },
            "light": {
                "bg": "#f0f0f0",
                "fg": "#333333",
                "button_bg": "#007acc",
                "button_fg": "#ffffff", 
                "button_active": "#005999",
                "frame_bg": "#e0e0e0",
                "accent": "#e74c3c"
            },
            "gaming": {
                "bg": "#0d1117",
                "fg": "#00ff00",
                "button_bg": "#ff0080",
                "button_fg": "#ffffff",
                "button_active": "#cc0066",
                "frame_bg": "#161b22",
                "accent": "#ffff00"
            }
        }
    
    def get_theme(self, theme_name):
        """获取主题配置"""
        return self.themes.get(theme_name, self.themes["dark"])

class GameStats:
    """游戏统计类"""
    def __init__(self, game_config):
        self.game_config = game_config
    
    def update_play_count(self):
        """更新游戏次数"""
        count = self.game_config.get("play_count", 0)
        self.game_config.set("play_count", count + 1)
    
    def update_last_played(self):
        """更新最后游戏时间"""
        self.game_config.set("last_played", datetime.now().isoformat())
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "play_count": self.game_config.get("play_count", 0),
            "last_played": self.game_config.get("last_played", "从未游戏")
        }

class CustomButton(tk.Button):
    """自定义按钮类"""
    def __init__(self, parent, text="", command=None, **kwargs):
        # 设置默认样式
        default_style = {
            'font': ('Helvetica', 12, 'bold'),
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': '#21a1f1',
            'activeforeground': 'white'
        }
        default_style.update(kwargs)
        
        super().__init__(parent, text=text, command=command, **default_style)
        
        # 绑定鼠标事件
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
        
        self.original_bg = self.cget('bg')
        self.hover_bg = kwargs.get('activebackground', '#21a1f1')
    
    def on_enter(self, event):
        """鼠标进入"""
        self.configure(bg=self.hover_bg)
        self.configure(relief=tk.RAISED)
    
    def on_leave(self, event):
        """鼠标离开"""
        self.configure(bg=self.original_bg)
        self.configure(relief=tk.FLAT)
    
    def on_click(self, event):
        """鼠标按下"""
        self.configure(relief=tk.SUNKEN)
    
    def on_release(self, event):
        """鼠标释放"""
        self.configure(relief=tk.RAISED)

class GameLauncher(tk.Tk):
    """主游戏启动器类"""
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.game_config = GameConfig()  # 修改变量名避免冲突
        self.theme_manager = ThemeManager()
        self.animation_handler = AnimationHandler(self)
        self.stats = GameStats(self.game_config)
        
        # 设置窗口
        self.setup_window()
        
        # 创建变量
        self.language = tk.StringVar(value=self.game_config.get("language", "Chinese"))
        self.version = tk.StringVar(value=self.game_config.get("version", "v2.0"))
        self.theme = tk.StringVar(value=self.game_config.get("theme", "dark"))
        
        # 应用主题
        self.current_theme = self.theme_manager.get_theme(self.theme.get())
        self.apply_theme()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 启动动画
        self.after(100, self.startup_animation)
    
    def setup_window(self):
        """设置窗口属性"""
        self.title("Super Ball Game Launcher Pro")
        self.geometry("900x700")
        self.resizable(True, True)
        self.minsize(800, 600)
        
        # 设置窗口位置
        pos = self.game_config.get("window_position", {"x": 100, "y": 100})
        self.geometry(f"900x700+{pos['x']}+{pos['y']}")
        
        # 设置图标（如果存在）
        try:
            self.iconbitmap("game_icon.ico")
        except:
            pass
    
    def apply_theme(self):
        """应用主题"""
        self.configure(bg=self.current_theme["bg"])
    
    def create_widgets(self):
        """创建所有界面组件"""
        self.create_header()
        self.create_main_content()
        self.create_settings_panel()
        self.create_footer()
        self.create_menu()
    
    def create_header(self):
        """创建头部区域"""
        self.header_frame = tk.Frame(self, bg=self.current_theme["bg"], height=120)
        self.header_frame.pack(fill=tk.X, pady=(20, 10))
        self.header_frame.pack_propagate(False)
        
        # 主标题
        self.title_label = tk.Label(
            self.header_frame,
            text="🎮 Super Ball Game Launcher",
            font=("Helvetica", 28, "bold"),
            fg=self.current_theme["button_bg"],
            bg=self.current_theme["bg"]
        )
        self.title_label.pack(pady=(20, 5))
        
        # 副标题
        self.subtitle_label = tk.Label(
            self.header_frame,
            text="Professional Game Management System",
            font=("Helvetica", 12, "italic"),
            fg=self.current_theme["fg"],
            bg=self.current_theme["bg"]
        )
        self.subtitle_label.pack()
    
    def create_main_content(self):
        """创建主要内容区域"""
        self.main_frame = tk.Frame(self, bg=self.current_theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # 左侧面板
        self.left_panel = tk.Frame(self.main_frame, bg=self.current_theme["frame_bg"], relief=tk.RAISED, bd=2)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 右侧面板
        self.right_panel = tk.Frame(self.main_frame, bg=self.current_theme["frame_bg"], relief=tk.RAISED, bd=2)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.create_game_selection()
        self.create_action_buttons()
        self.create_info_panel()
    
    def create_game_selection(self):
        """创建游戏选择区域"""
        # 语言选择区域
        lang_frame = tk.LabelFrame(
            self.left_panel,
            text="🌍 Language Selection",
            font=("Helvetica", 14, "bold"),
            fg=self.current_theme["accent"],
            bg=self.current_theme["frame_bg"],
            pady=10
        )
        lang_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # 语言选项
        lang_options_frame = tk.Frame(lang_frame, bg=self.current_theme["frame_bg"])
        lang_options_frame.pack(pady=10)
        
        self.lang_chinese = tk.Radiobutton(
            lang_options_frame,
            text="🇨🇳 中文 (Chinese)",
            variable=self.language,
            value="Chinese",
            font=("Helvetica", 12),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"],
            selectcolor=self.current_theme["button_bg"],
            activebackground=self.current_theme["frame_bg"],
            command=self.on_language_change
        )
        self.lang_chinese.pack(anchor=tk.W, padx=20, pady=5)
        
        self.lang_english = tk.Radiobutton(
            lang_options_frame,
            text="🇺🇸 English",
            variable=self.language,
            value="English", 
            font=("Helvetica", 12),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"],
            selectcolor=self.current_theme["button_bg"],
            activebackground=self.current_theme["frame_bg"],
            command=self.on_language_change
        )
        self.lang_english.pack(anchor=tk.W, padx=20, pady=5)
        
        # 版本选择区域
        version_frame = tk.LabelFrame(
            self.left_panel,
            text="⚙️ Version Selection",
            font=("Helvetica", 14, "bold"),
            fg=self.current_theme["accent"],
            bg=self.current_theme["frame_bg"],
            pady=10
        )
        version_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 版本选项
        version_options_frame = tk.Frame(version_frame, bg=self.current_theme["frame_bg"])
        version_options_frame.pack(pady=10)
        
        self.version_1 = tk.Radiobutton(
            version_options_frame,
            text="🎯 v1.0 - Classic Edition",
            variable=self.version,
            value="v1.0",
            font=("Helvetica", 12),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"],
            selectcolor=self.current_theme["button_bg"],
            activebackground=self.current_theme["frame_bg"],
            command=self.on_version_change
        )
        self.version_1.pack(anchor=tk.W, padx=20, pady=5)
        
        self.version_2 = tk.Radiobutton(
            version_options_frame,
            text="🚀 v2.0 - Advanced Edition",
            variable=self.version,
            value="v2.0",
            font=("Helvetica", 12),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"],
            selectcolor=self.current_theme["button_bg"],
            activebackground=self.current_theme["frame_bg"],
            command=self.on_version_change
        )
        self.version_2.pack(anchor=tk.W, padx=20, pady=5)
        
        # 特性描述
        features_frame = tk.Frame(self.left_panel, bg=self.current_theme["frame_bg"])
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.features_label = tk.Label(
            features_frame,
            text=self.get_version_features(),
            font=("Helvetica", 10),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"],
            justify=tk.LEFT,
            wraplength=400
        )
        self.features_label.pack(anchor=tk.W)
    
    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.left_panel, bg=self.current_theme["frame_bg"])
        button_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # 启动游戏按钮
        self.start_button = CustomButton(
            button_frame,
            text="🎮 Start Game",
            command=self.start_game,
            font=("Helvetica", 16, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            activebackground=self.current_theme["button_active"],
            width=20,
            height=2
        )
        self.start_button.pack(pady=10)
        
        # 其他按钮
        buttons_row = tk.Frame(button_frame, bg=self.current_theme["frame_bg"])
        buttons_row.pack(fill=tk.X, pady=10)
        
        self.test_button = CustomButton(
            buttons_row,
            text="🔧 Test Files",
            command=self.test_files,
            font=("Helvetica", 10),
            bg=self.current_theme["accent"],
            fg="white",
            width=12
        )
        self.test_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.settings_button = CustomButton(
            buttons_row,
            text="⚙️ Settings",
            command=self.open_settings,
            font=("Helvetica", 10),
            bg="#6c757d",
            fg="white",
            width=12
        )
        self.settings_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = CustomButton(
            buttons_row,
            text="❌ Exit",
            command=self.on_closing,
            font=("Helvetica", 10),
            bg="#dc3545",
            fg="white",
            width=12
        )
        self.exit_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_info_panel(self):
        """创建信息面板"""
        info_frame = tk.LabelFrame(
            self.right_panel,
            text="📊 Game Statistics",
            font=("Helvetica", 12, "bold"),
            fg=self.current_theme["accent"],
            bg=self.current_theme["frame_bg"],
            width=250
        )
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info_frame.pack_propagate(False)
        
        # 统计信息
        self.stats_text = tk.Text(
            info_frame,
            font=("Consolas", 9),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_stats_display()
        
        # 状态显示
        status_frame = tk.LabelFrame(
            self.right_panel,
            text="🔄 Status",
            font=("Helvetica", 12, "bold"),
            fg=self.current_theme["accent"],
            bg=self.current_theme["frame_bg"]
        )
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to launch",
            font=("Helvetica", 10),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"]
        )
        self.status_label.pack(pady=10)
    
    def create_settings_panel(self):
        """创建设置面板"""
        self.settings_window = None
    
    def create_footer(self):
        """创建底部区域"""
        self.footer_frame = tk.Frame(self, bg=self.current_theme["frame_bg"], height=40)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer_frame.pack_propagate(False)
        
        # 版权信息
        copyright_label = tk.Label(
            self.footer_frame,
            text="© 2025 Super Ball Game Launcher - Professional Edition",
            font=("Helvetica", 8),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"]
        )
        copyright_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 时间显示
        self.time_label = tk.Label(
            self.footer_frame,
            text="",
            font=("Helvetica", 8),
            fg=self.current_theme["fg"],
            bg=self.current_theme["frame_bg"]
        )
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.update_time()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Test Game Files", command=self.test_files)
        file_menu.add_command(label="Browse Game Folder", command=self.browse_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # 主题菜单
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Gaming Theme", command=lambda: self.change_theme("gaming"))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Controls", command=self.show_controls)
    
    def get_version_features(self):
        """获取版本特性描述"""
        features = {
            "v1.0": "• Basic ball physics\n• Simple controls\n• Classic gameplay\n• Standard graphics",
            "v2.0": "• Advanced physics engine\n• Spear combat system\n• Enhanced animations\n• Modern graphics\n• Special effects"
        }
        return features.get(self.version.get(), "Select a version to see features")
    
    def on_language_change(self):
        """语言变更回调"""
        self.game_config.set("language", self.language.get())
        self.update_status(f"Language changed to {self.language.get()}")
    
    def on_version_change(self):
        """版本变更回调"""
        self.game_config.set("version", self.version.get())
        self.features_label.config(text=self.get_version_features())
        self.update_status(f"Version changed to {self.version.get()}")
    
    def change_theme(self, theme_name):
        """更改主题"""
        self.theme.set(theme_name)
        self.game_config.set("theme", theme_name)
        self.current_theme = self.theme_manager.get_theme(theme_name)
        self.refresh_ui()
        self.update_status(f"Theme changed to {theme_name}")
    
    def refresh_ui(self):
        """刷新界面"""
        # 重新创建界面以应用新主题
        for widget in self.winfo_children():
            widget.destroy()
        self.apply_theme()
        self.create_widgets()
    
    def update_status(self, message):
        """更新状态显示"""
        self.status_label.config(text=message)
        self.after(3000, lambda: self.status_label.config(text="Ready to launch"))
    
    def update_stats_display(self):
        """更新统计显示"""
        stats = self.stats.get_stats()
        stats_text = f"""
📊 GAME STATISTICS
{'='*25}

🎮 Total Games Played: {stats['play_count']}
📅 Last Played: {stats['last_played'][:10] if stats['last_played'] != '从未游戏' else 'Never'}

🌍 Current Language: {self.language.get()}
⚙️ Current Version: {self.version.get()}
🎨 Current Theme: {self.theme.get().title()}

📁 Game Files Status:
{'='*25}
🇨🇳 Chinese: {'✅ Found' if self.check_file_exists('chinese') else '❌ Missing'}
🇺🇸 English: {'✅ Found' if self.check_file_exists('english') else '❌ Missing'}

💾 System Information:
{'='*25}
🐍 Python: {sys.version[:5]}
🖥️ Platform: {sys.platform}
📊 Memory Usage: Normal
🔄 Status: Ready
        """
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)
    
    def check_file_exists(self, language):
        """检查游戏文件是否存在"""
        if language == "chinese":
            path = self.game_config.get("chinese_path")
        else:
            path = self.game_config.get("english_path")
        return os.path.exists(path)
    
    def test_files(self):
        """测试游戏文件"""
        chinese_exists = self.check_file_exists("chinese")
        english_exists = self.check_file_exists("english")
        
        result = "File Test Results:\n\n"
        result += f"Chinese Version: {'✅ Found' if chinese_exists else '❌ Missing'}\n"
        result += f"English Version: {'✅ Found' if english_exists else '❌ Missing'}\n\n"
        
        if not chinese_exists:
            result += f"Chinese file path: {self.game_config.get('chinese_path')}\n"
        if not english_exists:
            result += f"English file path: {self.game_config.get('english_path')}\n"
        
        messagebox.showinfo("File Test", result)
    
    def browse_folder(self):
        """浏览游戏文件夹"""
        folder_path = filedialog.askdirectory(title="Select Game Folder")
        if folder_path:
            # 更新路径配置
            chinese_path = os.path.join(folder_path, "super_ball-chinese.html")
            english_path = os.path.join(folder_path, "super_ball-english.html")
            
            if os.path.exists(chinese_path):
                self.game_config.set("chinese_path", chinese_path)
            if os.path.exists(english_path):
                self.game_config.set("english_path", english_path)
            
            self.update_stats_display()
            self.update_status("Game folder updated")
    
    def open_settings(self):
        """打开设置窗口"""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
        
        self.settings_window = tk.Toplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x300")
        self.settings_window.configure(bg=self.current_theme["bg"])
        
        # 设置内容
        settings_label = tk.Label(
            self.settings_window,
            text="⚙️ Game Settings",
            font=("Helvetica", 16, "bold"),
            fg=self.current_theme["button_bg"],
            bg=self.current_theme["bg"]
        )
        settings_label.pack(pady=20)
        
        # 自动启动选项
        auto_frame = tk.Frame(self.settings_window, bg=self.current_theme["bg"])
        auto_frame.pack(pady=10)
        
        self.auto_launch_var = tk.BooleanVar(value=self.game_config.get("auto_launch", False))
        auto_check = tk.Checkbutton(
            auto_frame,
            text="Auto-launch last selected game",
            variable=self.auto_launch_var,
            font=("Helvetica", 12),
            fg=self.current_theme["fg"],
            bg=self.current_theme["bg"],
            selectcolor=self.current_theme["button_bg"],
            command=self.save_auto_launch
        )
        auto_check.pack()
        
        # 路径设置
        path_frame = tk.LabelFrame(
            self.settings_window,
            text="Game Paths",
            font=("Helvetica", 12, "bold"),
            fg=self.current_theme["accent"],
            bg=self.current_theme["bg"]
        )
        path_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 中文路径
        chinese_label = tk.Label(path_frame, text="Chinese Version:", fg=self.current_theme["fg"], bg=self.current_theme["bg"])
        chinese_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        chinese_path_label = tk.Label(
            path_frame,
            text=self.game_config.get("chinese_path", "")[:50] + "...",
            fg=self.current_theme["fg"],
            bg=self.current_theme["bg"],
            font=("Helvetica", 8)
        )
        chinese_path_label.pack(anchor=tk.W, padx=10)
        
        # 英文路径
        english_label = tk.Label(path_frame, text="English Version:", fg=self.current_theme["fg"], bg=self.current_theme["bg"])
        english_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        english_path_label = tk.Label(
            path_frame,
            text=self.game_config.get("english_path", "")[:50] + "...",
            fg=self.current_theme["fg"],
            bg=self.current_theme["bg"],
            font=("Helvetica", 8)
        )
        english_path_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
    
    def save_auto_launch(self):
        """保存自动启动设置"""
        self.game_config.set("auto_launch", self.auto_launch_var.get())
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
Super Ball Game Launcher Pro v1.0

A professional game management system for the Super Ball game series.

Features:
• Multi-language support
• Version management  
• Theme customization
• Game statistics
• File validation
• Auto-launch options

© 2025 Game Development Team
        """
        messagebox.showinfo("About", about_text)
    
    def show_controls(self):
        """显示控制说明"""
        controls_text = """
Game Controls:

🎮 In-Game Controls:
• W - Jump
• A - Move Left  
• D - Move Right
• Space - Attack/Shoot
• R - Restart Game

🖱️ Launcher Controls:
• Select language and version
• Click Start Game to launch
• Use menu for advanced options
• Check statistics in right panel
        """
        messagebox.showinfo("Game Controls", controls_text)
    
    def startup_animation(self):
        """启动动画"""
        self.animation_handler.fade_in(self.title_label)
        self.after(500, lambda: self.animation_handler.fade_in(self.subtitle_label))
    
    def start_game(self):
        """启动游戏"""
        lang = self.language.get()
        version = self.version.get()
        
        # 确定文件路径
        if lang == "Chinese":
            file_path = self.game_config.get("chinese_path")
        else:
            file_path = self.game_config.get("english_path")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            messagebox.showerror(
                "Error",
                f"Game file not found:\n{file_path}\n\nPlease check the file path in settings."
            )
            return
        
        try:
            # 更新统计
            self.stats.update_play_count()
            self.stats.update_last_played()
            
            # 启动游戏
            webbrowser.open(f"file:///{file_path}")
            
            # 更新界面
            self.update_stats_display()
            self.update_status(f"Game launched: {lang} {version}")
            
            # 播放启动动画
            self.animation_handler.bounce_effect(self.start_button)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch game:\n{str(e)}")
    
    def on_closing(self):
        """关闭程序"""
        # 保存窗口位置
        geometry = self.geometry()
        x = self.winfo_x()
        y = self.winfo_y()
        self.game_config.set("window_position", {"x": x, "y": y})
        
        # 确认退出
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.destroy()

# 主程序入口
if __name__ == '__main__':
    try:
        app = GameLauncher()
        app.mainloop()
    except Exception as e:
        print(f"程序启动失败: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")
