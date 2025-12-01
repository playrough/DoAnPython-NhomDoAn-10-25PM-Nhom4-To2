import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_mysql
from openpyxl import Workbook

# Thêm thư viện DateEntry
from tkcalendar import DateEntry


def open_crud(root, title, table, columns, headers, fields):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("900x500")

    tk.Label(win, text="Tìm kiếm:").pack(anchor="w")
    search_box = tk.Entry(win, width=40)
    search_box.pack(anchor="w", pady=3)

    frame_form = tk.LabelFrame(win, text="Thông tin")
    frame_form.pack(fill="x", padx=5, pady=5)

    # =========================
    # LOAD NHÀ CUNG CẤP (nếu cần)
    # =========================
    ncc_list = []
    if table == "sanpham":
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_ncc, ten_ncc FROM nhacungcap")
        ncc_list = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        cn.close()

    entries = {}

    for i, (label, col) in enumerate(fields):
        tk.Label(frame_form, text=label).grid(row=i, column=0, sticky="w")

        # ===============================
        # GIỚI TÍNH = COMBOBOX
        # ===============================
        if col == "gioi_tinh":
            ent = ttk.Combobox(frame_form, values=["Nam", "Nữ"], width=38)
            ent.set("Nam")  # mặc định
            ent.grid(row=i, column=1, padx=5, pady=3)

        # ===============================
        # NGÀY SINH = DATEENTRY
        # ===============================
        elif col == "ngay_sinh":
            ent = DateEntry(frame_form, date_pattern="yyyy-mm-dd", width=36)
            ent.grid(row=i, column=1, padx=5, pady=3)

        # ===============================
        # NHÀ CUNG CẤP = COMBOBOX
        # ===============================
        elif col == "id_ncc" and table == "sanpham":
            ent = ttk.Combobox(frame_form, values=ncc_list, width=38)
            ent.grid(row=i, column=1, padx=5, pady=3)

        # ===============================
        # INPUT CHỈ ĐƯỢC NHẬP SỐ
        # ===============================
        elif col in ("so_luong", "gia"):
            vcmd = (frame_form.register(lambda P: str.isdigit(P) or P == ""), "%P")
            ent = tk.Entry(frame_form, width=40, validate="key", validatecommand=vcmd)
            ent.insert(0, "1") if col == "so_luong" else ent.insert(0, "0")
            ent.grid(row=i, column=1, padx=5, pady=3)

        # ===============================
        # INPUT THƯỜNG
        # ===============================
        else:
            ent = tk.Entry(frame_form, width=40)
            ent.grid(row=i, column=1, padx=5, pady=3)

        entries[col] = ent

    frame_btn = tk.Frame(frame_form)
    frame_btn.grid(row=0, column=2, rowspan=len(fields), padx=10)

    # ================================================================
    # CHỨC NĂNG NÚT
    # ================================================================
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

            # xử lý Ncc
            if col == "id_ncc" and table == "sanpham":
                val = val.split(" - ")[0] if val else None

            data_values.append(val)

        try:
            cn = connect_mysql()
            cur = cn.cursor()
            sql = f"INSERT INTO {table} ({', '.join(columns[1:])}) VALUES ({','.join(['%s']*len(data_values))})"
            cur.execute(sql, tuple(data_values))
            cn.commit()
            load_data()
            clear_form()
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
            load_data()
            clear_form()
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
            load_data()
            clear_form()
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

    # Buttons
    tk.Button(frame_btn, text="Thêm", width=12, command=add_data).pack(pady=3)
    tk.Button(frame_btn, text="Sửa", width=12, command=update_data).pack(pady=3)
    tk.Button(frame_btn, text="Xóa", width=12, command=delete_data).pack(pady=3)
    tk.Button(frame_btn, text="Mới", width=12, command=clear_form).pack(pady=3)
    tk.Button(frame_btn, text="Xuất Excel", width=12, command=export_excel).pack(pady=3)
    tk.Button(frame_btn, text="Tải lại", width=12, command=load_data).pack(pady=3)

    frame_tbl = tk.Frame(win)
    frame_tbl.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame_tbl, columns=columns, show="headings")
    for c, h in zip(columns, headers):
        tree.heading(c, text=h)
        tree.column(c, width=120)
    tree.pack(fill="both", expand=True)

    # Khi chọn dòng → đổ vào form
    def select_row(e):
        sel = tree.selection()
        if not sel:
            return
        row = tree.item(sel[0])["values"]

        for i, c in enumerate(columns):
            if c in entries:

                # ncc -> convert "1" > "1 - Samsung"
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