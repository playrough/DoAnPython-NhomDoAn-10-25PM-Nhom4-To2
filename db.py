import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "iat",
    "database": "ql_cuahang_tivi"
}

def connect_mysql(use_database=True):
    """Connect to MySQL. If use_database=False connect without specifying database."""
    cfg = DB_CONFIG.copy()
    if not use_database:
        cfg.pop("database", None)
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except mysql.connector.Error as err:
        raise err

def database_exists():
    """Return True if DB exists on server."""
    try:
        cn = connect_mysql(use_database=False)
        cur = cn.cursor()
        cur.execute("SHOW DATABASES LIKE %s", (DB_CONFIG["database"],))
        exists = cur.fetchone() is not None
        cur.close()
        cn.close()
        return exists
    except Exception:
        return False

def create_database_and_tables():
    """
    Create database and tables if database not exists.
    If DB exists, this function will do nothing.
    Returns True if DB was created now (and sample data should be inserted),
    False if DB already existed.
    """
    if database_exists():
        return False  # DB already exists -> skip creating and skip sample data

    # create DB
    try:
        cn = connect_mysql(use_database=False)
        cur = cn.cursor()
        dbname = DB_CONFIG["database"]
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cur.close()
        cn.close()
    except mysql.connector.Error as err:
        raise err

    # now connect to the new DB and create tables
    cn = connect_mysql(use_database=True)
    cur = cn.cursor()
    # Create tables (names & columns in Vietnamese as you provided)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nhacungcap (
        id_ncc INT AUTO_INCREMENT PRIMARY KEY,
        ten_ncc VARCHAR(100) NOT NULL,
        dia_chi VARCHAR(255),
        sdt VARCHAR(20)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nhanvien (
        id_nv INT AUTO_INCREMENT PRIMARY KEY,
        ho_ten VARCHAR(100) NOT NULL,
        gioi_tinh ENUM('Nam','Nu') DEFAULT 'Nam',
        ngay_sinh DATE,
        sdt VARCHAR(20),
        dia_chi VARCHAR(255),
        chuc_vu VARCHAR(50)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS khachhang (
        id_khachhang INT AUTO_INCREMENT PRIMARY KEY,
        ho_ten VARCHAR(100) NOT NULL,
        gioi_tinh ENUM('Nam','Nu') DEFAULT 'Nam',
        ngay_sinh DATE,
        sdt VARCHAR(20),
        dia_chi VARCHAR(255)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sanpham (
        id_sanpham INT AUTO_INCREMENT PRIMARY KEY,
        ten_sanpham VARCHAR(100) NOT NULL,
        id_ncc INT,
        gia DECIMAL(15,2) NOT NULL,
        so_luong INT DEFAULT 0,
        mo_ta TEXT,
        FOREIGN KEY (id_ncc) REFERENCES nhacungcap(id_ncc) ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phieunhap (
        id_phieunhap INT AUTO_INCREMENT PRIMARY KEY,
        id_nv INT,
        id_ncc INT,
        ngay_nhap DATE,
        tong_tien DECIMAL(15,2),
        FOREIGN KEY (id_nv) REFERENCES nhanvien(id_nv),
        FOREIGN KEY (id_ncc) REFERENCES nhacungcap(id_ncc)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chitiet_phieunhap (
        id_ct INT AUTO_INCREMENT PRIMARY KEY,
        id_phieunhap INT,
        id_sanpham INT,
        so_luong INT,
        don_gia DECIMAL(15,2),
    
        FOREIGN KEY (id_phieunhap) REFERENCES phieunhap(id_phieunhap)
            ON DELETE CASCADE,
        FOREIGN KEY (id_sanpham) REFERENCES sanpham(id_sanpham)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hoadon (
        id_hoadon INT AUTO_INCREMENT PRIMARY KEY,
        id_nv INT,
        id_khachhang INT,
        ngay_lap DATE,
        tong_tien DECIMAL(15,2),
        FOREIGN KEY (id_nv) REFERENCES nhanvien(id_nv),
        FOREIGN KEY (id_khachhang) REFERENCES khachhang(id_khachhang)
    ) ENGINE=InnoDB;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ct_hoadon (
        id_ct_hoadon INT AUTO_INCREMENT PRIMARY KEY,
        id_hoadon INT,
        id_sanpham INT,
        so_luong INT,
        don_gia DECIMAL(15,2),
        thanh_tien DECIMAL(15,2),
        FOREIGN KEY (id_hoadon) REFERENCES hoadon(id_hoadon),
        FOREIGN KEY (id_sanpham) REFERENCES sanpham(id_sanpham)
    ) ENGINE=InnoDB;
    """)
    cn.commit()
    cur.close()
    cn.close()
    return True


def insert_sample_data_if_new():
    cn = connect_mysql(use_database=True)
    cur = cn.cursor()

    # check if DB already has data
    cur.execute("SELECT COUNT(*) FROM nhacungcap")
    if cur.fetchone()[0] > 0:
        cur.close()
        cn.close()
        return

    # ---------------------------
    # Insert nhà cung cấp
    # ---------------------------
    cur.executemany("""
        INSERT INTO nhacungcap(ten_ncc, dia_chi, sdt)
        VALUES (%s,%s,%s)
    """, [
        ("Công ty Samsung Vina", "HCM", "02839157310"),
        ("Sony Electronics VN", "Hà Nội", "1800588885"),
        ("LG Việt Nam", "HCM", "02838882345"),
        ("Toshiba Supply", "Hà Nội", "0243556677")
    ])

    # ---------------------------
    # Insert nhân viên
    # ---------------------------
    cur.executemany("""
        INSERT INTO nhanvien(ho_ten, gioi_tinh, ngay_sinh, sdt, dia_chi, chuc_vu)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, [
        ("Nguyễn Văn An", "Nam", "1990-05-15", "0909123456", "HCM", "Quản lý"),
        ("Trần Thị Bình", "Nu", "1995-08-20", "0918887777", "Đà Nẵng", "Thu ngân"),
        ("Lê Văn Nam", "Nam", "1987-03-10", "0932334455", "HCM", "Kho"),
        ("Phạm Thị Hoa", "Nu", "1998-11-05", "0923456677", "Hà Nội", "Bán hàng")
    ])

    # ---------------------------
    # Insert khách hàng
    # ---------------------------
    cur.executemany("""
        INSERT INTO khachhang(ho_ten, gioi_tinh, ngay_sinh, sdt, dia_chi)
        VALUES (%s,%s,%s,%s,%s)
    """, [
        ("Phạm Minh Tuấn", "Nam", "1988-01-01", "0909000000", "HCM"),
        ("Đỗ Thúy Hằng", "Nu", "1992-02-02", "0919000000", "Hà Nội"),
        ("Ngô Minh Đức", "Nam", "1995-05-12", "0988776655", "HCM"),
        ("Trần Thu Trang", "Nu", "1999-07-07", "0977665544", "Đà Nẵng"),
    ])

    # ---------------------------
    # Insert sản phẩm
    # ---------------------------
    cur.executemany("""
        INSERT INTO sanpham(ten_sanpham, id_ncc, gia, so_luong, mo_ta)
        VALUES (%s,%s,%s,%s,%s)
    """, [
        ("Smart TV Samsung 50 inch", 1, 12500000, 20, "Smart 4K 50\""),
        ("Android TV Sony 43 inch", 2, 9800000, 15, "Android 43\""),
        ("Tivi LG 55 inch OLED", 3, 21500000, 10, "OLED 55\""),
        ("Tủ lạnh Toshiba Inverter", 4, 8900000, 8, "Inverter 300L")
    ])

    # ---------------------------
    # Insert phiếu nhập
    # ---------------------------
    cur.executemany("""
        INSERT INTO phieunhap(id_nv, id_ncc, ngay_nhap, tong_tien)
        VALUES (%s,%s,%s,%s)
    """, [
        (3, 1, "2024-01-10", 25000000),
        (3, 2, "2024-02-12", 19600000),
    ])

    # ---------------------------
    # Insert chi tiết phiếu nhập
    # ---------------------------
    cur.executemany("""
        INSERT INTO chitiet_phieunhap(id_phieunhap, id_sanpham, so_luong, don_gia)
        VALUES (%s,%s,%s,%s)
    """, [
        (1, 1, 2, 12500000),   # 2 TV Samsung
        (2, 2, 2, 9800000),    # 2 Sony TV
    ])

    # ---------------------------
    # Insert hóa đơn
    # ---------------------------
    cur.executemany("""
        INSERT INTO hoadon(id_nv, id_khachhang, ngay_lap, tong_tien)
        VALUES (%s,%s,%s,%s)
    """, [
        (4, 1, "2024-03-01", 12500000),
        (4, 2, "2024-03-05", 9800000),
    ])

    # ---------------------------
    # Insert chi tiết hóa đơn
    # ---------------------------
    cur.executemany("""
        INSERT INTO ct_hoadon(id_hoadon, id_sanpham, so_luong, don_gia, thanh_tien)
        VALUES (%s,%s,%s,%s,%s)
    """, [
        (1, 1, 1, 12500000, 12500000),
        (2, 2, 1, 9800000, 9800000),
    ])

    cn.commit()
    cur.close()
    cn.close()