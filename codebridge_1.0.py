# codebridge syntax edition

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import re
import os
import chardet # type: ignore

class LineNumberEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 codebridge：v1.3 chardet+utf-8 fallback")
        self.font_size = tk.IntVar(value=18)

        self.text_frame = tk.Frame(root, height=720)
        self.text_frame.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=False)
        self.text_frame.pack_propagate(False)

        self.text = ScrolledText(self.text_frame, font=("MS Gothic", self.font_size.get()), width=100,
                                 bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.bind("<Return>", self.auto_insert_line_number)

        self.font_size.trace_add("write", self.update_font_size)

        self.mode = tk.StringVar(value="none")

        control_frame = tk.Frame(root)
        control_frame.pack(pady=(5, 10))

        tk.Button(control_frame, text="📂 ファイルを開く", command=self.load_file).pack(side="left", padx=5)
        tk.Button(control_frame, text="🔢 行番号を付ける", command=self.add_line_numbers).pack(side="left", padx=5)
        tk.Button(control_frame, text="🧹 行番号を除去", command=self.remove_line_numbers).pack(side="left", padx=5)
        tk.Button(control_frame, text="💾 上書き保存", command=self.save_file).pack(side="left", padx=5)
        tk.Button(control_frame, text="📝 名前を付けて保存", command=self.save_as_file).pack(side="left", padx=5)

        tk.Label(control_frame, text="フォントサイズ:").pack(side="left", padx=5)
        tk.Scale(control_frame, from_=8, to=24, orient="horizontal", variable=self.font_size).pack(side="left")

        tk.Label(control_frame, text="モード:").pack(side="left", padx=5)
        tk.OptionMenu(control_frame, self.mode, "none", "python", "vba", command=self.apply_highlight).pack(side="left")

        self.file_path = None
        self.setup_tags()

    def setup_tags(self):
        self.text.tag_configure("keyword", foreground="#569cd6")
        self.text.tag_configure("comment", foreground="#6a9955")
        self.text.tag_configure("string", foreground="#ce9178")

    def apply_highlight(self, *args):
        if self.mode.get() not in ["python", "vba"]:
            return
        self.text.tag_remove("keyword", "1.0", tk.END)
        self.text.tag_remove("comment", "1.0", tk.END)
        self.text.tag_remove("string", "1.0", tk.END)
        lines = self.text.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines, 1):
            if self.mode.get() == "python":
                for m in re.finditer(r"\b(def|class|import|from|return|if|else|for|while|try|except|with|as|in|print)\b", line):
                    self.text.tag_add("keyword", f"{i}.{m.start()}", f"{i}.{m.end()}")
                for m in re.finditer(r"#.*", line):
                    self.text.tag_add("comment", f"{i}.{m.start()}", f"{i}.{m.end()}")
                for m in re.finditer(r"'[^']*'|\"[^\"]*\"", line):
                    self.text.tag_add("string", f"{i}.{m.start()}", f"{i}.{m.end()}")
            elif self.mode.get() == "vba":
                for m in re.finditer(r"\b(Sub|End|Function|Dim|Set|If|Then|Else|For|Each|Next|Exit|Do|Loop|With)\b", line, re.IGNORECASE):
                    self.text.tag_add("keyword", f"{i}.{m.start()}", f"{i}.{m.end()}")
                for m in re.finditer(r"'[^\n]*", line):
                    self.text.tag_add("comment", f"{i}.{m.start()}", f"{i}.{m.end()}")
                for m in re.finditer(r'"[^"]*"', line):
                    self.text.tag_add("string", f"{i}.{m.start()}", f"{i}.{m.end()}")

    def update_font_size(self, *args):
        self.text.config(font=("MS Gothic", self.font_size.get()))
        self.apply_highlight()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if not file_path:
            return
        self.file_path = file_path
        content = ""
        try:
            with open(file_path, "rb") as f:
                raw = f.read()
                guess = chardet.detect(raw)
                enc = guess["encoding"] or "utf-8"

                # 信頼できない文字コードなら強制utf-8
                if enc.lower() in ["ascii", "windows-1252", "iso-8859-1", "charmap"]:
                    enc = "utf-8"

                try:
                    content = raw.decode(enc)
                except UnicodeDecodeError:
                    content = raw.decode("utf-8", errors="replace")
        except Exception as e:
            messagebox.showerror("読み込みエラー", f"このファイルは開けませんでした：\n{e}")
            return

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)

    def add_line_numbers(self):
        lines = self.text.get("1.0", tk.END).splitlines()
        lines = [re.sub(r"^\s*\d+\s*[\|\:\.]?\s*", "", line) for line in lines]
        numbered = [f"{str(i+1).zfill(3)} | {line}" for i, line in enumerate(lines)]
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", "\n".join(numbered))
        self.apply_highlight()

    def remove_line_numbers(self):
        lines = self.text.get("1.0", tk.END).splitlines()
        cleaned = [re.sub(r"^\s*\d+\s*[\|\:\.]?\s*", "", line) for line in lines]
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", "\n".join(cleaned))
        self.apply_highlight()

    def auto_insert_line_number(self, event):
        cursor_index = self.text.index(tk.INSERT)
        current_line = int(cursor_index.split('.')[0])
        self.text.insert(cursor_index, f"\n{str(current_line+1).zfill(3)} | ")
        self.apply_highlight()
        return "break"

    def save_file(self):
        if not self.file_path:
            self.save_as_file()
            return
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", tk.END).rstrip())
        messagebox.showinfo("保存完了", f"{os.path.basename(self.file_path)} を保存しました。")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END).rstrip())
            self.file_path = file_path
            messagebox.showinfo("保存完了", f"{os.path.basename(file_path)} を保存しました。")

def run_app():
    root = tk.Tk()
    app = LineNumberEditor(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
