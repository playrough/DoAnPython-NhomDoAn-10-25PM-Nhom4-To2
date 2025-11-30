# main.py
import tkinter as tk
import db
import sys
from tkinter import messagebox
from crud import open_crud_window
from invoices import open_invoice_window

def start_app():
    try:
        created_now = db.create_database_and_tables()
    except Exception as e:
        messagebox.showerror("Lỗi kết nối DB", str(e))
        sys.exit(1)

    # only insert sample data if DB was created now
    if created_now:
        try:
            db.insert_sample_data_if_new()
        except Exception as e:
            messagebox.showwarning("Lưu ý", "Không thể nạp dữ liệu mẫu: " + str(e))

    root = tk.Tk()
    root.title("QL Cửa Hàng Tivi")
    root.geometry("800x480")

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Danh mục menu
    cat = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Danh mục", menu=cat)

    cat.add_command(label="Nhà cung cấp", command=lambda: open_crud_window(root,
        "Nhà cung cấp", "nhacungcap",
        ["id_ncc","ten_ncc","dia_chi","sdt"],
        ["ID","Tên NCC","Địa chỉ","SĐT"],
        [("Tên NCC","ten_ncc"),("Địa chỉ","dia_chi"),("SĐT","sdt")]
    ))

    cat.add_command(label="Nhân viên", command=lambda: open_crud_window(root,
        "Nhân viên", "nhanvien",
        ["id_nv","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi","chuc_vu"],
        ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ","Chức vụ"],
        [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),("SĐT","sdt"),("Địa chỉ","dia_chi"),("Chức vụ","chuc_vu")]
    ))

    cat.add_command(label="Khách hàng", command=lambda: open_crud_window(root,
        "Khách hàng", "khachhang",
        ["id_khachhang","ho_ten","gioi_tinh","ngay_sinh","sdt","dia_chi"],
        ["ID","Họ tên","Giới tính","Ngày sinh","SĐT","Địa chỉ"],
        [("Họ tên","ho_ten"),("Giới tính","gioi_tinh"),("Ngày sinh","ngay_sinh"),("SĐT","sdt"),("Địa chỉ","dia_chi")]
    ))

    cat.add_command(label="Sản phẩm", command=lambda: open_crud_window(root,
        "Sản phẩm", "sanpham",
        ["id_sanpham","ten_sanpham","id_ncc","gia","so_luong","mo_ta"],
        ["ID","Tên SP","ID_NCC","Giá","Số lượng","Mô tả"],
        [("Tên SP","ten_sanpham"),("ID NCC","id_ncc"),("Giá","gia"),("Số lượng","so_luong"),("Mô tả","mo_ta")]
    ))

    # Hóa đơn
    hd = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Hóa đơn", menu=hd)
    hd.add_command(label="Lập hóa đơn", command=lambda: open_invoice_window(root))

    # Báo cáo
    rep = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Báo cáo", menu=rep)
    rep.add_command(label="Tồn kho", command=lambda: messagebox.showinfo("Hướng dẫn", "Chọn 'Sản phẩm' trong Danh mục, sắp xếp theo Số lượng để kiểm tra tồn kho."))

    # Help
    opt = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Tùy chọn", menu=opt)
    opt.add_command(label="Thoát", command=root.quit)

    tk.Label(root, text="Quản lý cửa hàng Tivi - Simple", font=("Arial", 20)).pack(pady=20)
    tk.Label(root, text="Dùng menu 'Danh mục' để quản lý, 'Hóa đơn' để bán hàng").pack()

    root.mainloop()

if __name__ == "__main__":
    start_app()