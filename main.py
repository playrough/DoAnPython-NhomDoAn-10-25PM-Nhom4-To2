import tkinter as tk
import db
import sys
from tkinter import messagebox
from crud import open_crud
from invoices import open_invoice_window

def start_app():
    try:
        created = db.create_database_and_tables()
        if created:
            db.insert_sample_data_if_new()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
        sys.exit(1)

    root = tk.Tk()
    root.title("Quản lý cửa hàng Tivi")
    root.geometry("800x450")

    menu = tk.Menu(root)
    root.config(menu=menu)

    m_cat = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Danh mục", menu=m_cat)

    m_cat.add_command(label="Nhà cung cấp",
        command=lambda: open_crud(root,
            "Nhà cung cấp","nhacungcap",
            ["id_ncc","ten_ncc","dia_chi","sdt"],
            ["ID","Tên NCC","Địa chỉ","SĐT"],
            [("Tên NCC","ten_ncc"),("Địa chỉ","dia_chi"),("SĐT","sdt")]
        )
    )

    m_cat.add_command(label="Nhân viên",
        command=lambda: open_crud(root,
            "Nhân viên","nhanvien",
            ["id_nv","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi","chuc_vu"],
            ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ","Chức vụ"],
            [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),
             ("SĐT","sdt"),("Địa chỉ","dia_chi"),("Chức vụ","chuc_vu")]
        )
    )

    m_cat.add_command(label="Khách hàng",
        command=lambda: open_crud(root,
            "Khách hàng","khachhang",
            ["id_khachhang","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi"],
            ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ"],
            [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),
             ("SĐT","sdt"),("Địa chỉ","dia_chi")]
        )
    )

    m_cat.add_command(label="Sản phẩm",
        command=lambda: open_crud(root,
            "Sản phẩm","sanpham",
            ["id_sanpham","ten_sanpham","id_ncc","gia","so_luong","mo_ta"],
            ["ID","Tên SP","NCC","Giá","SL","Mô tả"],
            [("Tên SP","ten_sanpham"),("Nhà cung cấp","id_ncc"),
             ("Giá","gia"),("Số lượng","so_luong"),("Mô tả","mo_ta")]
        )
    )

    m_hd = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Hóa đơn", menu=m_hd)
    m_hd.add_command(label="Lập hóa đơn", command=lambda: open_invoice_window(root))

    m_exit = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Hệ thống", menu=m_exit)
    m_exit.add_command(label="Thoát", command=root.quit)

    tk.Label(root, text="Hệ thống quản lý cửa hàng Tivi", font=("Arial", 20)).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    start_app()