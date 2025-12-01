import tkinter as tk
import db
import sys
from tkinter import messagebox
from crud import open_crud
from invoices import open_invoice_window
from receipt import open_receipt_window
from utils import center_window

def start_app():
    try:
        created = db.create_database_and_tables()
        if created:
            db.insert_sample_data_if_new()
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
        sys.exit(1)

    root = tk.Tk()
    root.title("Quản lý cửa hàng TV")
    root.geometry("900x550")
    root.configure(bg="#f5f5f5")
    center_window(root)

    # Menu
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
    m_hd.add_command(label="Lập phiếu nhập", command=lambda: open_receipt_window(root))

    m_exit = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Hệ thống", menu=m_exit)
    m_exit.add_command(label="Thoát", command=root.quit)

    # ===== Giao diện trang chủ =====
    # Tiêu đề
    title = tk.Label(root, text="HỆ THỐNG QUẢN LÝ CỬA HÀNG TIVI", font=("Arial", 24, "bold"), bg="#f5f5f5", fg="#2c3e50")
    title.pack(pady=20)

    # Thông tin giới thiệu
    info_frame = tk.Frame(root, bg="#ecf0f1", bd=2, relief="groove")
    info_frame.pack(padx=30, pady=10, fill="x")

    info_label = tk.Label(info_frame, text=(
        "Chào mừng bạn đến với hệ thống quản lý cửa hàng TV.\n"
        "Bạn có thể quản lý danh mục sản phẩm, khách hàng, nhà cung cấp, nhân viên và lập hóa đơn.\n"
    ), font=("Arial", 12), bg="#ecf0f1", justify="left")
    info_label.pack(padx=10, pady=10)

    # Shortcut buttons
    btn_frame = tk.Frame(root, bg="#f5f5f5")
    btn_frame.pack(pady=20)

    btn_specs = [
        (
            "Nhà cung cấp",
            lambda: open_crud(
                root, "Nhà cung cấp", "nhacungcap",
                ["id_ncc","ten_ncc","dia_chi","sdt"],
                ["ID","Tên NCC","Địa chỉ","SĐT"],
                [("Tên NCC","ten_ncc"),("Địa chỉ","dia_chi"),("SĐT","sdt")]
            )
        ),
        (
            "Nhân viên",
            lambda: open_crud(
                root, "Nhân viên","nhanvien",
                ["id_nv","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi","chuc_vu"],
                ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ","Chức vụ"],
                [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),
                 ("SĐT","sdt"),("Địa chỉ","dia_chi"),("Chức vụ","chuc_vu")]
            )
        ),
        (
            "Khách hàng",
            lambda: open_crud(
                root, "Khách hàng","khachhang",
                ["id_khachhang","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi"],
                ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ"],
                [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),
                 ("SĐT","sdt"),("Địa chỉ","dia_chi")]
            )
        ),
        (
            "Sản phẩm",
            lambda: open_crud(
                root, "Sản phẩm","sanpham",
                ["id_sanpham","ten_sanpham","id_ncc","gia","so_luong","mo_ta"],
                ["ID","Tên SP","NCC","Giá","SL","Mô tả"],
                [("Tên SP","ten_sanpham"),("Nhà cung cấp","id_ncc"),
                 ("Giá","gia"),("Số lượng","so_luong"),("Mô tả","mo_ta")]
            )
        ),
        (
            "Lập hóa đơn",
            lambda: open_invoice_window(root)
        ),
        (
            "Thoát",
            root.quit
        )
    ]
    
    for i, (text, cmd) in enumerate(btn_specs):
        btn = tk.Button(btn_frame, text=text, command=cmd,
                        font=("Arial", 12, "bold"), bg="#3498db", fg="white",
                        width=15, height=2, relief="raised", bd=3)
        btn.grid(row=i//3, column=i%3, padx=15, pady=15)

    # Footer
    footer = tk.Label(root, text="© 2025 Cửa hàng Tivi. All rights reserved.",
                      font=("Arial", 10), bg="#f5f5f5", fg="#7f8c8d")
    footer.pack(side="bottom", pady=10)

    root.mainloop()


if __name__ == "__main__":
    start_app()