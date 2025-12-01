import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_mysql
from openpyxl import Workbook
from tkcalendar import DateEntry


def open_crud(root, title, table, columns, headers, fields):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("950x550")
    win.grab_set()

    # ======= SEARCH BAR =======
    tk.Label(win, text="Tìm kiếm:").pack(anchor="w", padx=10, pady=(8, 2))
    search_box = tk.Entry(win, width=40)
    search_box.pack(anchor="w", padx=10, pady=(0, 8))

    # ======= FORM FRAME (SPLIT LEFT/RIGHT) =======
    frame_form = tk.Frame(win)
    frame_form.pack(fill="x", padx=10, pady=10)

    # LEFT: FORM INPUTS
    frame_left = tk.LabelFrame(frame_form, text="Thông tin", padx=10, pady=10)
    frame_left.grid(row=0, column=0, sticky="nw")

    # RIGHT: BUTTON PANEL
    frame_btn = tk.Frame(frame_form)
    frame_btn.grid(row=0, column=1, sticky="n", padx=20)

    # ======= LOAD NCC IF NEEDED =======
    ncc_list = []
    if table == "sanpham":
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_ncc, ten_ncc FROM nhacungcap")
        ncc_list = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        cn.close()

    entries = {}

    # ======= FORM INPUTS (NO VERTICAL STRETCH) =======

    # Cho phép input dãn ngang
    frame_left.columnconfigure(1, weight=1)

    # Giảm spacing cho CRUD có ít dòng (nhacungcap)
    pady_val = 4 if table == "nhacungcap" else 6

    for i, (label, col) in enumerate(fields):

        # LABEL
        tk.Label(frame_left, text=label, width=18, anchor="w").grid(
            row=i, column=0, sticky="w", padx=5, pady=pady_val
        )

        # FRAME BAO NGOÀI --> KHUYẾN KHÍCH INPUT GIỮ FORM
        input_frame = tk.Frame(frame_left)
        input_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=pady_val)
        input_frame.columnconfigure(0, weight=1)

        # GIỚI TÍNH
        if col == "gioi_tinh":
            ent = ttk.Combobox(input_frame, values=["Nam", "Nữ"])
            ent.set("Nam")

        # NGÀY SINH
        elif col == "ngay_sinh":
            ent = DateEntry(input_frame, date_pattern="yyyy-mm-dd")

        # NHÀ CUNG CẤP
        elif col == "id_ncc" and table == "sanpham":
            ent = ttk.Combobox(input_frame, values=ncc_list)

        # SỐ LƯỢNG / GIÁ (CHỈ NHẬP SỐ)
        elif col in ("so_luong", "gia"):
            vcmd = (frame_left.register(lambda P: str.isdigit(P) or P == ""), "%P")
            ent = tk.Entry(input_frame, validate="key", validatecommand=vcmd)
            ent.insert(0, "1" if col == "so_luong" else "0")

        # INPUT THƯỜNG
        else:
            ent = tk.Entry(input_frame)

        # dãn full width
        ent.pack(fill="x", expand=True)

        entries[col] = ent
        

        
    def clear_form():
        for e in entries.values():
            e.delete(0, tk.END)

    def load_data():
        for r in tree.get_children():
            tree.delete(r)
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def add_data():
        data_values = []
        for col in columns[1:]:
            val = entries[col].get().strip()
            if col == "id_ncc" and table == "sanpham":
                val = val.split(" - ")[0] if val else None
            data_values.append(val)

        try:
            cn = connect_mysql()
            cur = cn.cursor()
            sql = f"INSERT INTO {table} ({', '.join(columns[1:])}) VALUES ({','.join(['%s']*len(data_values))})"
            cur.execute(sql, tuple(data_values))
            cn.commit()
            clear_form()
            load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def update_data():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Chọn dòng", "Hãy chọn dòng cần sửa")
            return
        pk = tree.item(sel[0])["values"][0]

        values = []
        for col in columns[1:]:
            val = entries[col].get().strip()
            if col == "id_ncc" and table == "sanpham":
                val = val.split(" - ")[0]
            values.append(val)

        try:
            cn = connect_mysql()
            cur = cn.cursor()
            set_str = ", ".join([f"{c}=%s" for c in columns[1:]])
            sql = f"UPDATE {table} SET {set_str} WHERE {columns[0]}=%s"
            cur.execute(sql, tuple(values + [pk]))
            cn.commit()
            clear_form()
            load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def delete_data():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Chọn dòng", "Hãy chọn dòng cần xóa")
            return
        pk = tree.item(sel[0])["values"][0]

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?"):
            return

        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute(f"DELETE FROM {table} WHERE {columns[0]}=%s", (pk,))
            cn.commit()
            clear_form()
            load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def export_excel():
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()

            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for r in rows:
                ws.append(list(r))

            wb.save(f"{table}.xlsx")
            messagebox.showinfo("OK", f"Đã xuất file {table}.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ======= BUTTONS (WITH NICE SPACING) =======
    for text, cmd in [
        ("Thêm", add_data),
        ("Sửa", update_data),
        ("Xóa", delete_data),
        ("Mới", clear_form),
        ("Xuất Excel", export_excel),
        ("Tải lại", load_data),
    ]:
        tk.Button(frame_btn, text=text, width=15, command=cmd).pack(pady=6)

    # ======= TABLE VIEW WITH GOOD SPACE =======
    frame_tbl = tk.Frame(win, padx=10, pady=10)
    frame_tbl.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame_tbl, columns=columns, show="headings")
    for c, h in zip(columns, headers):
        tree.heading(c, text=h)
        tree.column(c, width=150, anchor="center")
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    def select_row(e):
        sel = tree.selection()
        if not sel:
            return

        row = tree.item(sel[0])["values"]

        for i, c in enumerate(columns):
            if c in entries:

                if c == "id_ncc" and table == "sanpham":
                    for item in ncc_list:
                        if item.startswith(f"{row[i]} -"):
                            entries[c].set(item)
                            break
                    continue

                entries[c].delete(0, tk.END)
                entries[c].insert(0, row[i])

    tree.bind("<<TreeviewSelect>>", select_row)

    load_data()