# crud.py
# Generic simple CRUD window with search for a given table.
import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_mysql
from datetime import datetime

def open_crud_window(root, title, table, columns, headers, form_fields):
    """
    - title: window title (Vietnamese label visible)
    - table: db table name (Vietnamese)
    - columns: list of db column names in same order as headers
    - headers: display headers for Treeview
    - form_fields: list of (label_text, db_col) for form inputs
    """
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("900x520")
    win.transient(root)
    win.grab_set()

    # top: search
    search_frame = tk.Frame(win, padx=6, pady=6)
    search_frame.pack(fill="x")
    tk.Label(search_frame, text="Tìm kiếm:").pack(side="left")
    search_entry = tk.Entry(search_frame, width=40)
    search_entry.pack(side="left", padx=6)

    def search_action(event=None):
        term = search_entry.get().strip()
        for r in tree.get_children():
            tree.delete(r)
        cn = None
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            if term == "":
                cur.execute(f"SELECT {', '.join(columns)} FROM {table} ORDER BY {columns[0]} DESC")
            else:
                # simple search on all textual columns with LIKE
                like = "%" + term + "%"
                where_clauses = []
                params = []
                for col in columns:
                    where_clauses.append(f"{col} LIKE %s")
                    params.append(like)
                sql = f"SELECT {', '.join(columns)} FROM {table} WHERE " + " OR ".join(where_clauses) + f" ORDER BY {columns[0]} DESC"
                cur.execute(sql, tuple(params))
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
        finally:
            if cn: cn.close()

    tk.Button(search_frame, text="Tìm", command=search_action).pack(side="left", padx=4)
    search_entry.bind("<Return>", search_action)

    # middle: form
    form_frame = tk.LabelFrame(win, text="Thông tin", padx=6, pady=6)
    form_frame.pack(fill="x", padx=6, pady=4)
    entries = {}
    for i, (label_text, db_col) in enumerate(form_fields):
        tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=4, pady=3)
        ent = tk.Entry(form_frame, width=50)
        ent.grid(row=i, column=1, padx=4, pady=3)
        entries[db_col] = ent

    # buttons
    btn_frame = tk.Frame(form_frame)
    btn_frame.grid(row=0, column=2, rowspan=len(form_fields), padx=8)
    def clear_form():
        for e in entries.values():
            e.delete(0, tk.END)

    def refresh():
        for r in tree.get_children():
            tree.delete(r)
        cn = None
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute(f"SELECT {', '.join(columns)} FROM {table} ORDER BY {columns[0]} DESC")
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))
        finally:
            if cn: cn.close()

    def add_record():
        vals = [entries.get(c).get().strip() if entries.get(c) else "" for c in columns]
        if vals[0] == "":
            messagebox.showwarning("Thiếu dữ liệu", f"Nhập {form_fields[0][0]}")
            return
        cn = None
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            placeholders = ", ".join(["%s"] * len(columns))
            cur.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", tuple(vals))
            cn.commit()
            refresh(); clear_form()
            messagebox.showinfo("OK", "Đã thêm")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            if cn: cn.close()

    def on_select(evt=None):
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0])['values']
        for i, col in enumerate(columns):
            if col in entries:
                entries[col].delete(0, tk.END)
                if vals[i] is not None:
                    entries[col].insert(0, str(vals[i]))

    def update_record():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Chọn dòng để sửa")
            return
        pk = tree.item(sel[0])['values'][0]
        vals = [entries.get(c).get().strip() if entries.get(c) else "" for c in columns]
        cn = None
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            set_clause = ", ".join([f"{c}=%s" for c in columns[1:]])
            params = vals[1:] + [pk]
            cur.execute(f"UPDATE {table} SET {set_clause} WHERE {columns[0]}=%s", tuple(params))
            cn.commit()
            refresh(); clear_form()
            messagebox.showinfo("OK", "Đã cập nhật")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            if cn: cn.close()

    def delete_record():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Chọn dòng để xóa")
            return
        pk = tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("Xác nhận", f"Xóa {pk}?"): return
        cn = None
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute(f"DELETE FROM {table} WHERE {columns[0]}=%s", (pk,))
            cn.commit()
            refresh(); clear_form()
            messagebox.showinfo("OK", "Đã xóa")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            if cn: cn.close()

    tk.Button(btn_frame, text="Thêm", width=12, command=add_record, bg="#90ee90").pack(pady=4)
    tk.Button(btn_frame, text="Lưu (Sửa)", width=12, command=update_record, bg="#add8e6").pack(pady=4)
    tk.Button(btn_frame, text="Xóa", width=12, command=delete_record, bg="#ffcccc").pack(pady=4)
    tk.Button(btn_frame, text="Mới", width=12, command=clear_form).pack(pady=4)
    tk.Button(btn_frame, text="Làm mới danh sách", width=14, command=refresh).pack(pady=6)

    # bottom: treeview
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=6, pady=6)
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    for c, h in zip(columns, headers):
        tree.heading(c, text=h)
        tree.column(c, width=120, anchor="w")
    tree.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.bind("<<TreeviewSelect>>", on_select)
    refresh()