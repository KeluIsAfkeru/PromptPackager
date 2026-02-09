import sys
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch

from theme import Material3
from async_utils import AsyncEngine
from widgets import ModernFileTree

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Prompt Packager Pro v1.0.2 - By Afkeru")
        self._center_window(900, 650) 
        
        self.engine = AsyncEngine(self)
        self.current_path = Path.cwd()
        self.history_stack = []
        self.output_dir = Path.cwd() / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.configure(fg_color=Material3.pair("bg"))
        self._init_ui()
        self.navigate(self.current_path)

    def _center_window(self, w, h):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (w / 2))
        y = int((screen_height / 2) - (h / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _init_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=Material3.pair("surface"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self._setup_sidebar()

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self._setup_main_area()

    def _setup_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="✨ PromptPackager", font=("Microsoft YaHei UI", 22, "bold"), 
                   text_color=Material3.pair("primary")).pack(anchor="w", padx=10, pady=(25, 15))

        self.fmt_var = tk.StringVar(value="markdown")
        r_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        r_box.pack(fill="x", padx=20)
        for t, v in [("Markdown", "markdown"), ("XML", "xml")]:
            ctk.CTkRadioButton(r_box, text=t, value=v, variable=self.fmt_var, 
                             fg_color=Material3.pair("primary"), command=self._on_fmt_change).pack(side="left", padx=(0,10))

        self._lbl(self.sidebar, "输出文件名")
        self.name_entry = ctk.CTkEntry(self.sidebar, height=36, corner_radius=18, border_width=0, 
                                     fg_color=Material3.pair("surface_variant"),
                                     text_color=Material3.pair("text"))
        self.name_entry.pack(fill="x", padx=20, pady=(5, 5))
        self.name_entry.insert(0, "prompt_context.md")

        self._lbl(self.sidebar, "输出路径")
        self.path_btn = ctk.CTkButton(self.sidebar, text=f"📂 {self.output_dir.name}", height=32, corner_radius=16,
                                    fg_color=Material3.pair("surface_variant"), text_color=Material3.pair("text"),
                                    hover_color=Material3.pair("outline"), anchor="w", command=self.choose_out_dir)
        self.path_btn.pack(fill="x", padx=20, pady=(5, 10))

        opt_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        opt_box.pack(fill="x", padx=20, pady=5)
        
        self.rel_path_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opt_box, text="写入相对路径", variable=self.rel_path_var, font=("Microsoft YaHei UI", 12),
                      text_color=Material3.pair("text"), fg_color=Material3.pair("primary")).pack(anchor="w", pady=2)
        
        self.compress_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_box, text="压缩空行/回车", variable=self.compress_var, font=("Microsoft YaHei UI", 12),
                      text_color=Material3.pair("text"), fg_color=Material3.pair("primary")).pack(anchor="w", pady=2)

        self._lbl(self.sidebar, "忽略规则")
        self.ign_box = ctk.CTkTextbox(self.sidebar, height=70, corner_radius=15, border_width=0,
                                    fg_color=Material3.pair("surface_variant"),
                                    text_color=Material3.pair("text"))
        self.ign_box.pack(fill="x", padx=20, pady=5)
        self.ign_box.insert("0.0", "node_modules;.git;__pycache__;*.pyc;*.png;*.jpg;*.exe;.vscode")

        sel_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sel_header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(sel_header, text="已选文件", font=("Microsoft YaHei UI", 12, "bold"), 
                   text_color=Material3.pair("secondary")).pack(side="left")
        
        self.clear_btn = ctk.CTkButton(sel_header, text="清空", width=50, height=24, corner_radius=12,
                                     fg_color=Material3.pair("surface_variant"), 
                                     text_color=Material3.pair("text"),
                                     hover_color=Material3.pair("outline"),
                                     font=("Microsoft YaHei UI", 11), command=self.clear_all_selection)
        self.clear_btn.pack(side="right")

        self.sel_list_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.sel_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def _lbl(self, p, t):
        ctk.CTkLabel(p, text=t, font=("Microsoft YaHei UI", 12, "bold"), 
                   text_color=Material3.pair("secondary")).pack(anchor="w", padx=20, pady=(15, 0))

    def _setup_main_area(self):
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        nav = ctk.CTkFrame(self.main_area, fg_color="transparent", height=45)
        nav.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self._nav_btn(nav, "⬅", self.go_back)
        self._nav_btn(nav, "⬆", self.go_up)
        
        self.addr_bar = ctk.CTkEntry(nav, height=36, corner_radius=18, border_width=0,
                                   fg_color=Material3.pair("surface"),
                                   text_color=Material3.pair("text"))
        self.addr_bar.pack(side="left", fill="x", expand=True, padx=10)
        self.addr_bar.bind("<Return>", lambda e: self.navigate(Path(self.addr_bar.get())))
        
        self._nav_btn(nav, "📂", self.browse_folder, width=40)

        self.file_tree = ModernFileTree(self.main_area, self.navigate, self.on_tree_toggle)
        self.file_tree.grid(row=1, column=0, sticky="nsew")

        self.bottom_bar = ctk.CTkFrame(self.main_area, fg_color="transparent", height=50)
        self.bottom_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.status_lbl = ctk.CTkLabel(self.bottom_bar, text="就绪", anchor="w", text_color=Material3.pair("text_dim"))
        self.status_lbl.pack(side="left", padx=10)

        self.action_btn = ctk.CTkButton(self.bottom_bar, text="🚀 开始生成", height=38, width=130, corner_radius=19,
                                      font=("Microsoft YaHei UI", 14, "bold"),
                                      fg_color=Material3.pair("primary"),
                                      text_color=Material3.pair("on_primary"),
                                      hover_color=Material3.pair("secondary"),
                                      command=self.start_process)
        self.action_btn.pack(side="right", padx=10)

    def _nav_btn(self, p, t, c, width=40):
        ctk.CTkButton(p, text=t, width=width, height=36, corner_radius=18,
                    fg_color=Material3.pair("surface"), text_color=Material3.pair("text"),
                    font=("Segoe UI Emoji", 14), command=c).pack(side="left", padx=(0, 5))

    def navigate(self, path):
        path = Path(path)
        if not path.exists() or not path.is_dir(): return
        if self.current_path != path: self.history_stack.append(self.current_path)
        self.current_path = path
        self.addr_bar.delete(0, tk.END)
        self.addr_bar.insert(0, str(path))
        self.status_lbl.configure(text="加载中...")
        self.engine.run(self._scan, self.file_tree.populate, path)

    def _scan(self, path):
        data = []
        try:
            with os.scandir(path) as it:
                entries = list(it)
            entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
            for e in entries:
                if e.name.startswith('.'): continue
                sz = ""
                if not e.is_dir():
                    try: sz = f"{e.stat().st_size/1024:.1f} KB"
                    except: sz = "N/A"
                mtime = ""
                try: 
                    import datetime
                    mtime = datetime.datetime.fromtimestamp(e.stat().st_mtime).strftime('%Y-%m-%d')
                except: pass
                data.append({
                    "name": e.name, "path": str(e.path), "is_dir": e.is_dir(),
                    "size_str": sz, "date": mtime
                })
        except: pass
        return data

    def on_tree_toggle(self, item_path, is_selecting, recursive=False):
        self.update_selection_ui()
        
        if recursive and item_path:
            self.status_lbl.configure(text="正在处理文件夹内容..." if is_selecting else "正在移除文件夹内容...")
            ignores = self.ign_box.get("0.0", "end").replace("\n", ";").split(";")
            
            task_args = {
                "root": item_path,
                "is_selecting": is_selecting,
                "ignores": [x.strip() for x in ignores if x.strip()]
            }
            self.engine.run(self._recursive_worker, self._recursive_done, task_args)

    def _recursive_worker(self, args):
        root = Path(args["root"])
        is_selecting = args["is_selecting"]
        ignores = args["ignores"]
        
        def is_ign(p): return any(fnmatch.fnmatch(Path(p).name, x) for x in ignores)
        
        affected_items = set()
        try:
            affected_items.add(str(root))
            for parent, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if not is_ign(os.path.join(parent, d))]
                for f in files:
                    if not is_ign(f):
                        affected_items.add(os.path.join(parent, f))
                for d in dirs:
                    affected_items.add(os.path.join(parent, d))
        except Exception: pass
        return affected_items, is_selecting

    def _recursive_done(self, result):
        affected_items, is_selecting = result
        if is_selecting:
            self.file_tree.selection_map.update(affected_items)
        else:
            self.file_tree.selection_map.difference_update(affected_items)
        self.file_tree.bulk_update_visuals()
        self.update_selection_ui()

    def update_selection_ui(self):
        all_items = list(self.file_tree.selection_map)
        files_only = [p for p in all_items if Path(p).is_file()]
        files_only.sort()
        
        count = len(files_only)
        self.status_lbl.configure(text=f"已选 {count} 个文件")
        
        for w in self.sel_list_frame.winfo_children(): w.destroy()
        
        if count > 100:
            ctk.CTkLabel(self.sel_list_frame, text=f"已选择 {count} 个文件\n数量过多，不显示详情", 
                       text_color=Material3.pair("text_dim")).pack(pady=20)
            return

        for path_str in files_only:
            p = Path(path_str)
            row = ctk.CTkFrame(self.sel_list_frame, fg_color="transparent", height=28)
            row.pack(fill="x", pady=1)
            
            ctk.CTkButton(row, text="✕", width=20, height=20, corner_radius=10,
                        fg_color="transparent", text_color=Material3.pair("error"), hover_color=Material3.pair("surface_variant"),
                        command=lambda x=path_str: self.file_tree.remove_specific(x)).pack(side="right")
            
            ctk.CTkLabel(row, text=p.name, anchor="w", font=("Microsoft YaHei UI", 11),
                       text_color=Material3.pair("text")).pack(side="left", fill="x", expand=True)

    def clear_all_selection(self):
        self.file_tree.clear_selection()

    def _on_fmt_change(self):
        current = self.name_entry.get()
        if not current: return
        base = os.path.splitext(current)[0]
        ext = ".xml" if self.fmt_var.get() == "xml" else ".md"
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, base + ext)

    def choose_out_dir(self):
        if d := filedialog.askdirectory():
            self.output_dir = Path(d)
            self.path_btn.configure(text=f"📂 {self.output_dir.name}")

    def go_back(self):
        if self.history_stack: self.navigate(self.history_stack.pop())
    
    def go_up(self):
        self.navigate(self.current_path.parent)
        
    def browse_folder(self):
        if d := filedialog.askdirectory(): self.navigate(Path(d))

    def start_process(self):
        all_items = list(self.file_tree.selection_map)
        files = [x for x in all_items if Path(x).is_file()]
        
        if not files: return messagebox.showwarning("提示", "请至少选择一个文件")
        
        self.action_btn.configure(state="disabled", text="⏳ 生成中...")
        cfg = {
            'out': self.output_dir / self.name_entry.get(),
            'fmt': self.fmt_var.get(),
            'ign': self.ign_box.get("0.0", "end").replace("\n", ";").split(";"),
            'src': files,
            'root': self.current_path,
            'rel_path': self.rel_path_var.get(),
            'compress': self.compress_var.get()
        }
        self.engine.run(self._worker, self._done, cfg)

    def _worker(self, cfg):
        is_xml = cfg['fmt'] == 'xml'
        ignores = [x.strip() for x in cfg['ign'] if x.strip()]
        
        def is_ign(p): return any(fnmatch.fnmatch(Path(p).name, x) for x in ignores)
        
        def read_one_file(f_path_str):
            p = Path(f_path_str)
            if is_ign(p): return None
            try:
                content = p.read_text(encoding='utf-8', errors='ignore')
                if cfg['compress']:
                    content = re.sub(r'\n\s*\n', '\n', content)
                
                display_path = p.name
                if cfg['rel_path']:
                    try: display_path = str(p.relative_to(cfg['root'])).replace("\\", "/")
                    except: display_path = p.name
                
                return {
                    "path": display_path,
                    "content": content,
                    "ext": p.suffix[1:] if p.suffix else "txt",
                    "sort_key": str(p).lower() 
                }
            except: return None

        processed_files = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(read_one_file, f) for f in cfg['src']]
            for future in as_completed(futures):
                res = future.result()
                if res: processed_files.append(res)
        
        processed_files.sort(key=lambda x: x['sort_key'])

        buf = []
        
        if is_xml:
            buf.append("<file_index>")
            for i, f in enumerate(processed_files, 1):
                buf.append(f'  <entry index="{i}">{f["path"]}</entry>')
            buf.append("</file_index>\n")
            
            buf.append("<documents>")
            for i, f in enumerate(processed_files, 1):
                buf.append(f'<document index="{i}">\n<source>{f["path"]}</source>\n<document_content>\n{f["content"]}\n</document_content>\n</document>')
            buf.append("</documents>")
        else:
            buf.append("# File Index")
            for i, f in enumerate(processed_files, 1):
                buf.append(f"{i}. {f['path']}")
            buf.append("\n" + "="*30 + "\n")
            
            for i, f in enumerate(processed_files, 1):
                buf.append(f"## File {i}: {f['path']}\n```{f['ext']}\n{f['content']}\n```\n")

        cfg['out'].write_text("\n".join(buf), encoding='utf-8')
        return str(cfg['out'])

    def _done(self, path):
        self.action_btn.configure(state="normal", text="🚀 开始生成")
        messagebox.showinfo("完成", f"文件已生成:\n{path}")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()