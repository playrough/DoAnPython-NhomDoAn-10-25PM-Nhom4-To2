import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db import connect_mysql


def open_receipt_window(root):
    win = tk.Toplevel(root)
    win.title("Lập Phiếu Nhập")
    win.geometry("750x550")

    # ===== LẤY DANH SÁCH NHÂN VIÊN =====
    cn = connect_mysql()
    cur = cn.cursor()
    cur.execute("SELECT id_nv, ho_ten FROM nhanvien")
    nv_list = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    # ===== LẤY DANH SÁCH NHÀ CUNG CẤP =====
    cur.execute("SELECT id_ncc, ten_ncc FROM nhacungcap")
    ncc_list = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    # ===== LẤY DANH SÁCH SẢN PHẨM =====
    cur.execute("SELECT id_sanpham, ten_sanpham FROM sanpham")
    sp_list = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
    cur.close()
    cn.close()

    # =============== FRAME THÔNG TIN PHIẾU ===============
    frm_info = tk.LabelFrame(win, text="Thông tin phiếu nhập", padx=10, pady=10)
    frm_info.pack(fill="x", padx=10, pady=10)

    tk.Label(frm_info, text="Nhân viên:").grid(row=0, column=0, padx=5, pady=5)
    cb_nv = ttk.Combobox(frm_info, values=nv_list, width=25, state="readonly")
    cb_nv.grid(row=0, column=1)
    cb_nv.current(0)

    tk.Label(frm_info, text="Nhà cung cấp:").grid(row=1, column=0, padx=5, pady=5)
    cb_ncc = ttk.Combobox(frm_info, values=ncc_list, width=25, state="readonly")
    cb_ncc.grid(row=1, column=1)
    cb_ncc.current(0)

    tk.Label(frm_info, text="Ngày nhập:").grid(row=2, column=0, padx=5, pady=5)
    ent_date = tk.Entry(frm_info, width=20)
    ent_date.grid(row=2, column=1)
    
    ent_date.config(state="normal")
    ent_date.insert(0, str(date.today()))
    ent_date.config(state="disabled")

    # =============== FRAME THÊM SẢN PHẨM ===============
    frm_add = tk.LabelFrame(win, text="Thêm sản phẩm nhập", padx=10, pady=10)
    frm_add.pack(fill="x", padx=10)

    tk.Label(frm_add, text="Sản phẩm:").grid(row=0, column=0)
    cb_sp = ttk.Combobox(frm_add, values=sp_list, width=30, state="readonly")
    cb_sp.grid(row=0, column=1, padx=5)

    tk.Label(frm_add, text="Số lượng:").grid(row=0, column=2)
    ent_sl = tk.Entry(frm_add, width=10)
    ent_sl.grid(row=0, column=3, padx=5)
    ent_sl.insert(0, "1")

    tk.Label(frm_add, text="Đơn giá:").grid(row=0, column=4)
    ent_dg = tk.Entry(frm_add, width=10)
    ent_dg.grid(row=0, column=5, padx=5)
    ent_dg.insert(0, "0")

    # ========= TABLE =========
    frm_tbl = tk.Frame(win)
    frm_tbl.pack(fill="both", expand=True, padx=10, pady=10)

    cols = ("id_sp", "ten_sp", "so_luong", "don_gia", "thanh_tien")
    tree = ttk.Treeview(frm_tbl, columns=cols, show="headings", height=10)
    for c in cols:
        tree.heading(c, text=c.upper())
        tree.column(c, width=120, anchor="center")
    tree.pack(fill="both", expand=True)

    # ======= TÍNH TỔNG =======
    lbl_total = tk.Label(win, text="Tổng tiền: 0", font=("Arial", 14))
    lbl_total.pack(pady=5)

    def update_total():
        total = 0
        for row in tree.get_children():
            total += float(tree.item(row)["values"][4])
        lbl_total.config(text=f"Tổng tiền: {total:,.0f}")

    # ======= BUTTON THÊM SP =======
    def add_product():
        if not cb_sp.get():
            messagebox.showwarning("Thiếu dữ liệu", "Chọn sản phẩm")
            return

        sp_id = cb_sp.get().split(" - ")[0]
        sp_name = cb_sp.get().split(" - ")[1]
        sl = ent_sl.get().strip()
        dg = ent_dg.get().strip()

        if not sl.isdigit() or not dg.isdigit():
            messagebox.showwarning("Lỗi", "Số lượng và đơn giá phải là số")
            return

        sl = int(sl)
        dg = int(dg)
        tt = sl * dg

        tree.insert("", tk.END, values=(sp_id, sp_name, sl, dg, tt))
        update_total()

    tk.Button(frm_add, text="Thêm vào phiếu", command=add_product).grid(row=0, column=6, padx=10)

    # =========== LƯU PHIẾU NHẬP ===========

    def save_receipt():
        if len(tree.get_children()) == 0:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có sản phẩm")
            return

        id_nv = cb_nv.get().split(" - ")[0]
        id_ncc = cb_ncc.get().split(" - ")[0]
        ngay = ent_date.get().strip()
        tong_tien = 0

        # Tính tổng
        for r in tree.get_children():
            tong_tien += float(tree.item(r)["values"][4])

        try:
            cn = connect_mysql()
            cur = cn.cursor()

            # Insert phiếu nhập
            sql = """
                INSERT INTO phieunhap (id_nv, id_ncc, ngay_nhap, tong_tien)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql, (id_nv, id_ncc, ngay, tong_tien))
            id_pn = cur.lastrowid

            # Insert chi tiết
            for r in tree.get_children():
                v = tree.item(r)["values"]
                sql_ct = """
                    INSERT INTO chitiet_phieunhap (id_phieunhap, id_sanpham, so_luong, don_gia)
                    VALUES (%s, %s, %s, %s)
                """
                cur.execute(sql_ct, (id_pn, v[0], v[2], v[3]))

            cn.commit()
            messagebox.showinfo("Thành công", f"Lưu phiếu nhập #{id_pn} thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    tk.Button(win, text="LƯU PHIẾU NHẬP", font=("Arial", 14), bg="#4CAF50", fg="white",
              command=save_receipt).pack(pady=10)