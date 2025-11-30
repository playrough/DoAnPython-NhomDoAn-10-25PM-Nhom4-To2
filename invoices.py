# invoices.py
# Simple invoice window: create invoice, write into hoadon & ct_hoadon, update stock, export to excel
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import connect_mysql
from datetime import datetime
from openpyxl import Workbook
import os

def open_invoice_window(root):
    win = tk.Toplevel(root)
    win.title("Lập Hóa Đơn")
    win.geometry("900x600")
    win.grab_set()

    # header area: choose customer and staff
    hdr = tk.Frame(win, padx=6, pady=6)
    hdr.pack(fill="x")
    tk.Label(hdr, text="Khách hàng:").grid(row=0, column=0, sticky="w")
    cb_customer = ttk.Combobox(hdr, width=40, state="readonly")
    cb_customer.grid(row=0, column=1, padx=6)
    tk.Label(hdr, text="Nhân viên:").grid(row=1, column=0, sticky="w")
    cb_staff = ttk.Combobox(hdr, width=40, state="readonly")
    cb_staff.grid(row=1, column=1, padx=6)

    # load lists
    prod_map = {}
    def load_lists():
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_khachhang, ho_ten FROM khachhang")
        customers = cur.fetchall()
        cb_customer['values'] = [f"{r[0]} - {r[1]}" for r in customers]
        cur.execute("SELECT id_nv, ho_ten FROM nhanvien")
        staffs = cur.fetchall()
        cb_staff['values'] = [f"{r[0]} - {r[1]}" for r in staffs]
        # products
        cur.execute("SELECT id_sanpham, ten_sanpham, gia, so_luong FROM sanpham")
        prods = cur.fetchall()
        prod_map.clear()
        cb_products['values'] = [f"{r[0]} - {r[1]} (Giá: {int(r[2])}, Tồn: {r[3]})" for r in prods]
        for r in prods:
            prod_map[r[0]] = {"ten": r[1], "gia": float(r[2]), "so": int(r[3])}
        cn.close()

    # product selection
    prod_frame = tk.Frame(win, padx=6, pady=6)
    prod_frame.pack(fill="x")
    tk.Label(prod_frame, text="Sản phẩm:").grid(row=0, column=0, sticky="w")
    cb_products = ttk.Combobox(prod_frame, width=60, state="readonly")
    cb_products.grid(row=0, column=1, padx=6)
    tk.Label(prod_frame, text="Số lượng:").grid(row=1, column=0, sticky="w")
    entry_qty = tk.Entry(prod_frame, width=10); entry_qty.insert(0, "1")
    entry_qty.grid(row=1, column=1, sticky="w")

    # cart
    cart_frame = tk.Frame(win)
    cart_frame.pack(fill="both", expand=True, padx=6, pady=6)
    cols = ("id_sp","ten","so_luong","don_gia","thanh_tien")
    tree = ttk.Treeview(cart_frame, columns=cols, show="headings", height=10)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120)
    tree.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(cart_frame, orient="vertical", command=tree.yview).pack(side="right", fill="y")

    total_var = tk.StringVar(value="0")
    tk.Label(win, text="Tổng:").pack(anchor="e", padx=8)
    tk.Label(win, textvariable=total_var, font=("Arial", 12, "bold")).pack(anchor="e", padx=8)

    def add_to_cart():
        sel = cb_products.get()
        if not sel:
            return
        id_sp = int(sel.split(" - ")[0])
        try:
            qty = int(entry_qty.get())
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Lỗi", "Số lượng phải là số nguyên dương")
            return
        info = prod_map.get(id_sp)
        if not info:
            messagebox.showwarning("Lỗi", "Không tìm sản phẩm")
            return
        if qty > info["so"]:
            messagebox.showwarning("Lỗi", f"Tồn kho không đủ: {info['so']}")
            return
        price = info["gia"]
        amount = qty * price
        tree.insert("", "end", values=(id_sp, info["ten"], qty, price, amount))
        recalc_total()

    def recalc_total():
        s = 0
        for it in tree.get_children():
            s += float(tree.item(it, "values")[4])
        total_var.set(f"{int(s):,}")

    def remove_selected():
        sel = tree.selection()
        for i in sel:
            tree.delete(i)
        recalc_total()

    def save_invoice():
        if not cb_customer.get() or not cb_staff.get():
            messagebox.showwarning("Thiếu", "Chọn khách hàng và nhân viên")
            return
        if not tree.get_children():
            messagebox.showwarning("Thiếu", "Chưa có sản phẩm")
            return
        id_kh = int(cb_customer.get().split(" - ")[0])
        id_nv = int(cb_staff.get().split(" - ")[0])
        ngay = datetime.now().strftime("%Y-%m-%d")
        tong = 0
        items = []
        for it in tree.get_children():
            id_sp, ten, qty, dg, tt = tree.item(it, "values")
            items.append((int(id_sp), int(qty), float(dg), float(tt)))
            tong += float(tt)
        # write to DB
        cn = connect_mysql()
        cur = cn.cursor()
        try:
            cur.execute("INSERT INTO hoadon(id_nv, id_khachhang, ngay_lap, tong_tien) VALUES (%s,%s,%s,%s)", (id_nv, id_kh, ngay, tong))
            cn.commit()
            # get last inserted id
            cur.execute("SELECT LAST_INSERT_ID()")
            id_hd = cur.fetchone()[0]
            for id_sp, qty, dg, tt in items:
                cur.execute("INSERT INTO ct_hoadon(id_hoadon, id_sanpham, so_luong, don_gia, thanh_tien) VALUES (%s,%s,%s,%s,%s)",
                            (id_hd, id_sp, qty, dg, tt))
                # update stock
                cur.execute("UPDATE sanpham SET so_luong = so_luong - %s WHERE id_sanpham = %s", (qty, id_sp))
            cn.commit()
            messagebox.showinfo("OK", f"Lưu hóa đơn {id_hd} thành công")
            win.destroy()
            # offer to export
            if messagebox.askyesno("Xuất", "Xuất hóa đơn vừa tạo ra Excel?"):
                export_invoice_excel(id_hd)
        except Exception as e:
            cn.rollback()
            messagebox.showerror("Lỗi DB", str(e))
        finally:
            cur.close()
            cn.close()

    def export_invoice_excel(invoice_id):
        # fetch info + items
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("""
            SELECT h.id_hoadon, h.ngay_lap, kh.ho_ten, nv.ho_ten, h.tong_tien
            FROM hoadon h
            LEFT JOIN khachhang kh ON h.id_khachhang = kh.id_khachhang
            LEFT JOIN nhanvien nv ON h.id_nv = nv.id_nv
            WHERE h.id_hoadon = %s
        """, (invoice_id,))
        info = cur.fetchone()
        if not info:
            messagebox.showerror("Lỗi", "Không tìm hóa đơn")
            cur.close(); cn.close(); return
        cur.execute("""
            SELECT ct.id_sanpham, sp.ten_sanpham, ct.so_luong, ct.don_gia, ct.thanh_tien
            FROM ct_hoadon ct
            LEFT JOIN sanpham sp ON ct.id_sanpham = sp.id_sanpham
            WHERE ct.id_hoadon = %s
        """, (invoice_id,))
        items = cur.fetchall()
        cur.close(); cn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "HóaĐơn"
        ws.append(["HÓA ĐƠN BÁN HÀNG"])
        ws.append(["Mã HĐ", info[0], "", "Ngày", str(info[1])])
        ws.append(["Khách hàng", info[2], "", "Nhân viên", info[3]])
        ws.append([])
        ws.append(["STT", "Tên SP", "Số lượng", "Đơn giá", "Thành tiền"])
        for i, it in enumerate(items, start=1):
            ws.append([i, it[1], it[2], float(it[3]), float(it[4])])
        ws.append([])
        ws.append(["", "", "", "Tổng", float(info[4])])

        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")],
                                            initialfile=f"HoaDon_{invoice_id}.xlsx")
        if file:
            wb.save(file)
            messagebox.showinfo("OK", f"Đã lưu: {file}")
            try:
                os.startfile(file)
            except:
                pass

    # controls
    ctl = tk.Frame(win)
    ctl.pack(fill="x", padx=6, pady=6)
    tk.Button(ctl, text="Thêm vào HĐ", command=add_to_cart).pack(side="left", padx=6)
    tk.Button(ctl, text="Xóa mục", command=remove_selected).pack(side="left", padx=6)
    tk.Button(ctl, text="Lưu HĐ", command=save_invoice, bg="#90ee90").pack(side="right", padx=6)
    tk.Button(ctl, text="Đóng", command=win.destroy).pack(side="right", padx=6)

    load_lists()