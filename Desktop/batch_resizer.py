#!/usr/bin/env python3
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD

def closest_multiple_of_4(n: int) -> int:
    return round(n / 4) * 4

class UnityImageResizer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unity Image Resizer")
        self.geometry("700x500")
        self.file_list = []

        # ── Project Path ──────────────────────────────────────────
        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(path_frame, text="Directory to scan:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var, width=55).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse…", command=self._choose_directory).pack(side=tk.LEFT)
        # New button to load images from pasted path
        ttk.Button(path_frame, text="Load Images", command=self._load_from_entry).pack(side=tk.LEFT, padx=(5,0))

        # ── Crunch Checkbox ───────────────────────────────────────
        self.crunch_var = tk.BooleanVar(value=True)
        chk = ttk.Checkbutton(self, text="Use crunch compression", variable=self.crunch_var)
        chk.pack(anchor=tk.W, padx=15, pady=(0,10))

        # ── File List / Drag‑&‑Drop ───────────────────────────────
        self.listbox = tk.Listbox(self, width=100, height=20)
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self._on_drop)

        # ── Buttons ───────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Resize Images", command=self._resize_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear List",   command=self._clear_list).pack(side=tk.LEFT, padx=5)

    def _choose_directory(self):
        d = filedialog.askdirectory()
        if d:
            self.path_var.set(d)
            self._load_images_from_path(d)

    def _load_from_entry(self):
        d = self.path_var.get()
        if os.path.isdir(d):
            self._load_images_from_path(d)
        else:
            messagebox.showerror("Error", f"Directory not found:\n{d}")

    def _load_images_from_path(self, directory):
        self._clear_list()
        for root, _, files in os.walk(directory):
            for f in files:
                if f.lower().endswith(('.png','.jpg','.jpeg','.bmp','.gif','tiff')):
                    full = os.path.join(root, f)
                    self.file_list.append(full)
                    self.listbox.insert(tk.END, full)

    def _on_drop(self, event):
        for f in self.tk.splitlist(event.data):
            if os.path.isfile(f) and f.lower().endswith(('.png','.jpg','.jpeg','.bmp','.gif','tiff')):
                if f not in self.file_list:
                    self.file_list.append(f)
                    self.listbox.insert(tk.END, f)

    def _resize_images(self):
        if not self.file_list:
            messagebox.showerror("Error", "No images selected!")
            return

        use_crunch = self.crunch_var.get()

        for img_path in list(self.file_list):
            try:
                # Resize image
                img = Image.open(img_path)
                w, h = img.size
                nw, nh = closest_multiple_of_4(w), closest_multiple_of_4(h)
                resized = img.resize((nw, nh), Image.LANCZOS)
                resized.save(img_path)
                img.close()

                # Update .meta if present
                meta_path = img_path + '.meta'
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as mf:
                        lines = mf.readlines()
                    changed = False
                    for i, line in enumerate(lines):
                        m = re.match(r'^(\s*)crunchedCompression:\s*\d+', line)
                        if m:
                            indent = m.group(1)
                            lines[i] = f"{indent}crunchedCompression: {'1' if use_crunch else '0'}\n"
                            changed = True
                    if changed:
                        with open(meta_path, 'w', encoding='utf-8') as mf:
                            mf.writelines(lines)

            except Exception as e:
                messagebox.showwarning("Processing error",
                                       f"{os.path.basename(img_path)} failed:\n{e}")

        messagebox.showinfo("Done", "All images resized and metas updated.")
        self._clear_list()

    def _clear_list(self):
        self.file_list.clear()
        self.listbox.delete(0, tk.END)

if __name__ == "__main__":
    app = UnityImageResizer()
    app.mainloop()
