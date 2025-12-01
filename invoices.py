import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_mysql
from openpyxl import Workbook
from datetime import datetime

def open_invoice_window(root):
    win = tk.Toplevel(root)
    win.title("Lập hóa đơn")
    win.geometry("950x650")

    # ================================
    # TẢI DỮ LIỆU TỪ MYSQL
    # ================================
    def load_staff():
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_nv, ho_ten, sdt, dia_chi FROM nhanvien")
        data = cur.fetchall()
        cn.close()
        return data

    def load_customer():
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_khachhang, ho_ten, sdt, dia_chi FROM khachhang")
        data = cur.fetchall()
        cn.close()
        return data

    def load_product():
        cn = connect_mysql()
        cur = cn.cursor()
        cur.execute("SELECT id_sanpham, ten_sanpham, gia FROM sanpham")
        data = cur.fetchall()
        cn.close()
        return data

    staff_list = load_staff()
    customer_list = load_customer()
    product_list = load_product()

    # ================================
    # THÔNG TIN HÓA ĐƠN
    # ================================
    frame_info = tk.LabelFrame(win, text="Thông tin hóa đơn")
    frame_info.pack(fill="x", padx=5, pady=5)

    # ===== Nhân viên =====
    tk.Label(frame_info, text="Nhân viên:").grid(row=0, column=0, sticky="w")
    cbo_nv = ttk.Combobox(frame_info, width=25,
                          values=[f"{r[0]} - {r[1]}" for r in staff_list])
    cbo_nv.grid(row=0, column=1, padx=5)

    tk.Label(frame_info, text="Tên NV:").grid(row=1, column=0, sticky="w")
    ten_nv = tk.Entry(frame_info, width=25); ten_nv.grid(row=1, column=1, padx=5)

    tk.Label(frame_info, text="SĐT NV:").grid(row=1, column=2, sticky="w")
    sdt_nv = tk.Entry(frame_info, width=20); sdt_nv.grid(row=1, column=3, padx=5)

    tk.Label(frame_info, text="Địa chỉ NV:").grid(row=1, column=4, sticky="w")
    dc_nv = tk.Entry(frame_info, width=30); dc_nv.grid(row=1, column=5, padx=5)

    def on_staff_select(e):
        if not cbo_nv.get():
            return
    
        id_sel = int(cbo_nv.get().split(" - ")[0])
        for r in staff_list:
            if r[0] == id_sel:
    
                # Mở để ghi dữ liệu
                ten_nv.config(state="normal")
                sdt_nv.config(state="normal")
                dc_nv.config(state="normal")
    
                ten_nv.delete(0, tk.END)
                ten_nv.insert(0, r[1])
    
                sdt_nv.delete(0, tk.END)
                sdt_nv.insert(0, r[2])
    
                dc_nv.delete(0, tk.END)
                dc_nv.insert(0, r[3])
    
                # KHÓA HOÀN TOÀN
                ten_nv.config(state="disabled")
                sdt_nv.config(state="disabled")
                dc_nv.config(state="disabled")
                break

    cbo_nv.bind("<<ComboboxSelected>>", on_staff_select)

    # ===== Khách hàng =====
    tk.Label(frame_info, text="Khách hàng:").grid(row=2, column=0, sticky="w")
    cbo_kh = ttk.Combobox(frame_info, width=25,
                          values=[f"{r[0]} - {r[1]}" for r in customer_list])
    cbo_kh.grid(row=2, column=1, padx=5)

    tk.Label(frame_info, text="Tên KH:").grid(row=3, column=0, sticky="w")
    ten_kh = tk.Entry(frame_info, width=25); ten_kh.grid(row=3, column=1, padx=5)

    tk.Label(frame_info, text="SĐT KH:").grid(row=3, column=2, sticky="w")
    sdt_kh = tk.Entry(frame_info, width=20); sdt_kh.grid(row=3, column=3, padx=5)

    tk.Label(frame_info, text="Địa chỉ KH:").grid(row=3, column=4, sticky="w")
    dc_kh = tk.Entry(frame_info, width=30); dc_kh.grid(row=3, column=5, padx=5)

    def on_customer_select(e):
        if not cbo_kh.get():
            return
    
        id_sel = int(cbo_kh.get().split(" - ")[0])
        for r in customer_list:
            if r[0] == id_sel:
    
                ten_kh.config(state="normal")
                sdt_kh.config(state="normal")
                dc_kh.config(state="normal")
    
                ten_kh.delete(0, tk.END)
                ten_kh.insert(0, r[1])
    
                sdt_kh.delete(0, tk.END)
                sdt_kh.insert(0, r[2])
    
                dc_kh.delete(0, tk.END)
                dc_kh.insert(0, r[3])
    
                ten_kh.config(state="disabled")
                sdt_kh.config(state="disabled")
                dc_kh.config(state="disabled")
                break
            


    cbo_kh.bind("<<ComboboxSelected>>", on_customer_select)

    # ===== Ngày =====
    tk.Label(frame_info, text="Ngày lập:").grid(row=4, column=0, sticky="w")
    ngay = tk.Entry(frame_info, width=15)
    
    today = datetime.now().strftime("%Y-%m-%d")   # YYYY-MM-DD
    ngay.insert(0, today)
    
    # Khóa không cho sửa
    ngay.config(state="disabled")
    
    ngay.grid(row=4, column=1, padx=5)

    # ================================
    # SẢN PHẨM – COMBOBOX
    # ================================
    frame_sp = tk.LabelFrame(win, text="Sản phẩm")
    frame_sp.pack(fill="x", padx=5, pady=5)

    tk.Label(frame_sp, text="Chọn sản phẩm:").grid(row=0, column=0)
    cbo_sp = ttk.Combobox(frame_sp, width=30,
                          values=[f"{r[0]} - {r[1]}" for r in product_list])
    cbo_sp.grid(row=0, column=1, padx=5)

    tk.Label(frame_sp, text="Giá:").grid(row=0, column=2)
    gia_sp = tk.Entry(frame_sp, width=12, state="disabled")
    gia_sp.grid(row=0, column=3, padx=5)

    tk.Label(frame_sp, text="Số lượng:").grid(row=0, column=4)
    sl = tk.Entry(frame_sp, width=10); sl.grid(row=0, column=5, padx=5)
    sl.insert(0, "1") 

    def on_product_select(e):
        if not cbo_sp.get():
            return
    
        id_sel = int(cbo_sp.get().split(" - ")[0])
        for r in product_list:
            if r[0] == id_sel:
    
                # mở để cập nhật
                gia_sp.config(state="normal")
                gia_sp.delete(0, tk.END)
                gia_sp.insert(0, r[2])
    
                # khóa lại (không cho sửa)
                gia_sp.config(state="disabled")
                break

    cbo_sp.bind("<<ComboboxSelected>>", on_product_select)

    # ================================
    # DANH SÁCH SẢN PHẨM TRONG HÓA ĐƠN
    # ================================
    tree = ttk.Treeview(win, columns=("id","ten","sl","gia","tien"), show="headings")
    for c in ("id","ten","sl","gia","tien"):
        tree.heading(c, text=c.upper())
        tree.column(c, width=120)
    tree.pack(fill="both", expand=True, pady=5)

    def add_item():
        if not cbo_sp.get():
            messagebox.showwarning("Thiếu", "Hãy chọn sản phẩm")
            return

        id_sp = int(cbo_sp.get().split(" - ")[0])
        ten_sp = cbo_sp.get().split(" - ")[1]
        so_luong = int(sl.get())
        don_gia = float(gia_sp.get())
        thanh_tien = so_luong * don_gia

        tree.insert("", "end", values=(id_sp, ten_sp, so_luong, don_gia, thanh_tien))

    # ================================
    # LƯU HÓA ĐƠN
    # ================================
    def save_invoice():
        if not cbo_nv.get() or not cbo_kh.get():
            messagebox.showwarning("Thiếu", "Hãy chọn nhân viên và khách hàng")
            return
    
        id_nv = int(cbo_nv.get().split(" - ")[0])
        id_kh = int(cbo_kh.get().split(" - ")[0])
    
        cn = connect_mysql()
        cur = cn.cursor()
    
        # Tạo hóa đơn trước
        cur.execute(
            "INSERT INTO hoadon(id_nv,id_khachhang,ngay_lap,tong_tien) VALUES (%s,%s,%s,%s)",
            (id_nv, id_kh, ngay.get(), 0)
        )
        cn.commit()
    
        id_hd = cur.lastrowid
        total = 0.0
    
        for r in tree.get_children():
            row = tree.item(r)["values"]
    
            id_sp = int(row[0])
            so_luong = int(row[2])
            don_gia = float(row[3])
            thanh_tien = float(row[4])   # ÉP KIỂU TẠI ĐÂY
    
            cur.execute(
                "INSERT INTO ct_hoadon(id_hoadon,id_sanpham,so_luong,don_gia,thanh_tien) VALUES (%s,%s,%s,%s,%s)",
                (id_hd, id_sp, so_luong, don_gia, thanh_tien)
            )
    
            total += thanh_tien   # GIỜ không bị lỗi nữa
    
        cur.execute("UPDATE hoadon SET tong_tien=%s WHERE id_hoadon=%s", (total, id_hd))
        cn.commit()
    
        messagebox.showinfo("OK", f"Đã lưu hóa đơn {id_hd}")
        

    # ================================
    # IN HÓA ĐƠN – openpyxl
    # ================================
    def print_invoice():
        try:
            cn = connect_mysql()
            cur = cn.cursor()
            cur.execute("SELECT * FROM hoadon ORDER BY id_hoadon DESC LIMIT 1")
            hd = cur.fetchone()

            wb = Workbook()
            ws = wb.active
            ws.append(["ID", "ID NV", "ID KH", "Ngày lập", "Tổng tiền"])
            ws.append(list(hd))

            wb.save("hoadon_moi_nhat.xlsx")
            messagebox.showinfo("OK", "Đã in hóa đơn ra file hoadon_moi_nhat.xlsx")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    tk.Button(frame_sp, text="Thêm SP", command=add_item).grid(row=0, column=6, padx=5)

    actions_frame = tk.Frame(win)
    actions_frame.pack(pady=10)

    
    btn_save = tk.Button(actions_frame, text="Lưu hóa đơn", width=15, command=save_invoice)
    btn_print = tk.Button(actions_frame, text="In hóa đơn", width=15, command=print_invoice)
    

    # căn giữa + đặt ngang nhau
    btn_save.pack(side=tk.LEFT, padx=10)
    btn_print.pack(side=tk.LEFT, padx=10)
    
    # căn giữa toàn bộ khung nút
    actions_frame.pack(anchor="center")