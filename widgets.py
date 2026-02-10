import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from pathlib import Path
from theme import Material3

class ModernFileTree(ctk.CTkFrame):
    def __init__(self, master, navigate_cb, toggle_cb, **kwargs):
        super().__init__(master, **kwargs)
        self.navigate_cb = navigate_cb
        self.toggle_cb = toggle_cb 
        self.selection_map = set()
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        bg = Material3.get("bg")
        fg = Material3.get("text")
        hl = Material3.get("surface_variant")
        
        self.style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        self.style.configure("Custom.Treeview", 
                           background=bg, foreground=fg, fieldbackground=bg,
                           borderwidth=0, rowheight=36,
                           font=("Microsoft YaHei UI", 11))
        
        self.style.map("Custom.Treeview", 
                      background=[("selected", hl)], 
                      foreground=[("selected", fg)])
        
        self.style.configure("Custom.Treeview.Heading", 
                           font=("Microsoft YaHei UI", 11, "bold"), 
                           background=Material3.get("surface"), 
                           foreground=fg, borderwidth=0, relief="flat")

        self.tree = ttk.Treeview(self, columns=("size", "date"), 
                               show="tree headings", style="Custom.Treeview", selectmode="browse")
        
        self.tree.heading("#0", text="  文件名", anchor="w")
        self.tree.heading("size", text="大小  ", anchor="e")
        self.tree.heading("date", text="修改日期  ", anchor="e")
        
        self.tree.column("#0", minwidth=300, stretch=True) 
        self.tree.column("size", width=100, anchor="e", stretch=False)
        self.tree.column("date", width=140, anchor="e", stretch=False)

        self.scroll_y = ctk.CTkScrollbar(self, command=self.tree.yview, width=12)
        self.tree.configure(yscrollcommand=self.scroll_y.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_single_click)

        self.icons = {
            "checked": "☑",
            "unchecked": "☐",
            "folder": "📁",
            "file": "📄"
        }
        self.current_items_map = {} 
        self._populate_queue = []

    def populate(self, items):
        self.tree.delete(*self.tree.get_children())
        self.current_items_map = {str(item['path']): item for item in items}
        self._populate_queue = items
        self.after(1, self._process_batch_insert)

    def _process_batch_insert(self):
        batch_size = 60 
        if not self._populate_queue:
            return
            
        batch = self._populate_queue[:batch_size]
        self._populate_queue = self._populate_queue[batch_size:]
        
        for item in batch:
            path_str = str(item['path'])
            is_checked = path_str in self.selection_map
            self._insert_item(item, is_checked)
            
        if self._populate_queue:
            self.after(5, self._process_batch_insert)

    def _insert_item(self, item, checked):
        check_icon = self.icons["checked"] if checked else self.icons["unchecked"]
        type_icon = self.icons["folder"] if item['is_dir'] else self.icons["file"]
        display_text = f"  {check_icon}   {type_icon}   {item['name']}"
        tags = ("dir",) if item['is_dir'] else ("file",)
        
        self.tree.insert("", "end", iid=str(item['path']), text=display_text, 
                         values=(item['size_str'], item['date']), tags=tags)

    def on_single_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item_id = self.tree.identify_row(event.y)
            if not item_id: return
            if event.x < 60:
                self.handle_toggle(item_id)
                return "break"

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        p = Path(item_id)
        if p.is_dir():
            self.navigate_cb(p)
        else:
            self.handle_toggle(item_id)

    def handle_toggle(self, item_id):
        item = self.current_items_map.get(item_id)
        is_dir = item['is_dir'] if item else Path(item_id).is_dir()
        
        is_selecting = item_id not in self.selection_map
        
        if is_selecting:
            self.selection_map.add(item_id)
        else:
            self.selection_map.discard(item_id)
            
        self.refresh_row_visual(item_id)
        self.toggle_cb(item_id, is_selecting, recursive=is_dir)

    def refresh_row_visual(self, item_id):
        if not self.tree.exists(item_id): return
        old_text = self.tree.item(item_id, "text")
        
        target_icon = self.icons["checked"] if item_id in self.selection_map else self.icons["unchecked"]
        
        if self.icons["checked"] in old_text and target_icon == self.icons["unchecked"]:
            new_text = old_text.replace(self.icons["checked"], self.icons["unchecked"], 1)
            self.tree.item(item_id, text=new_text)
        elif self.icons["unchecked"] in old_text and target_icon == self.icons["checked"]:
            new_text = old_text.replace(self.icons["unchecked"], self.icons["checked"], 1)
            self.tree.item(item_id, text=new_text)

    def clear_selection(self):
        visible_ids = self.tree.get_children()
        self.selection_map.clear()
        for item_id in visible_ids:
            self.refresh_row_visual(item_id)
        self.toggle_cb(None, False, False)

    def remove_specific(self, path_str):
        if path_str in self.selection_map:
            self.selection_map.remove(path_str)
            if self.tree.exists(path_str):
                self.refresh_row_visual(path_str)
            
            if Path(path_str).is_dir():
                self.toggle_cb(path_str, False, recursive=True)
            else:
                self.toggle_cb(path_str, False, recursive=False)

    def bulk_update_visuals(self, affected_items=None):
        current_visible_ids = set(self.tree.get_children())
        if affected_items:
            to_update = current_visible_ids.intersection(affected_items)
            for item_id in to_update:
                self.refresh_row_visual(item_id)
        else:
            for item_id in current_visible_ids:
                self.refresh_row_visual(item_id)