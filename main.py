import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QTabWidget, QGridLayout, QMainWindow, QAction, QMenu
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class BookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1D022108_Ajundasrika Anugrahanti TS")
        self.setGeometry(100, 100, 600, 500)
        self.conn = sqlite3.connect("database.db")
        self.init_db()
        self.init_menu()
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.setup_ui()
        self.load_data()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                year TEXT
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM books WHERE title=? AND author=?", 
                   ('MySQL', 'Ajundasrika Anugrahanti TS'))
        if  cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", 
                       ('MySQL', 'Ajundasrika Anugrahanti TS', '2025'))
            
        self.conn.commit()

    def init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        save_action = QAction("Simpan", self)
        save_action.triggered.connect(self.add_data)
        file_menu.addAction(save_action)

        export_action = QAction("Ekspor ke CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)

        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("Edit")

        search_action = QAction("Cari Judul", self)
        search_action.triggered.connect(lambda: self.search_input.setFocus())
        edit_menu.addAction(search_action)

        delete_action = QAction("Hapus Data", self)
        delete_action.triggered.connect(self.delete_data)
        edit_menu.addAction(delete_action)

        autofill_menu = QMenu("AutoFill", self)
        autofill_dummy = QAction("(Tidak tersedia)", self)
        autofill_dummy.setEnabled(False)
        autofill_menu.addAction(autofill_dummy)
        edit_menu.addMenu(autofill_menu)

        start_dictation = QAction("Start Dictation…", self)
        start_dictation.setEnabled(False)
        edit_menu.addAction(start_dictation)

        emoji_symbols = QAction("Emoji & Symbols", self)
        emoji_symbols.setEnabled(False)
        edit_menu.addAction(emoji_symbols)

    def setup_ui(self):
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_data, "Data Buku")
        self.tabs.addTab(self.tab_export, "Ekspor")

        self.setup_data_tab()
        self.setup_export_tab()

        main_layout.addWidget(self.tabs)
        self.widget.setLayout(main_layout)

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D7;
            }
            QTableWidget {
                border: 1px solid #ddd;
                alternate-background-color: #f6f6f6;
                gridline-color: #ccc;
                selection-background-color: #cce4ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QLabel {
                font-weight: bold;
            }
            QTabBar::tab {
                padding: 8px 20px;
                background: #f4f4f4;
                border: 1px solid #ccc;
                border-bottom: none;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
        """)

    def setup_data_tab(self):
        layout = QVBoxLayout()
        form_layout = QGridLayout()

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()
        form_layout.addWidget(QLabel("Judul:"), 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)
        form_layout.addWidget(QLabel("Pengarang:"), 1, 0)
        form_layout.addWidget(self.author_input, 1, 1)
        form_layout.addWidget(QLabel("Tahun:"), 2, 0)
        form_layout.addWidget(self.year_input, 2, 1)

        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.add_data)
        form_layout.addWidget(self.save_btn, 3, 0, 1, 2)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.search_data)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellChanged.connect(self.update_data)

        self.delete_btn = QPushButton("Hapus Data")
        self.delete_btn.setStyleSheet("background-color: orange; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_data)

        layout.addLayout(form_layout)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addWidget(self.delete_btn)
        self.tab_data.setLayout(layout)

    def setup_export_tab(self):
        layout = QVBoxLayout()
        self.export_btn = QPushButton("Ekspor ke CSV")
        self.export_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_btn)
        self.tab_export.setLayout(layout)

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        for row_data in cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
        self.table.blockSignals(False)

    def add_data(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        if not title or not author or not year:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi!")
            return
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
        self.conn.commit()
        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()
        self.load_data()

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin dihapus!")
            return
        book_id = self.table.item(selected, 0).text()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()
        self.load_data()

    def export_csv(self):
        from PyQt5.QtWidgets import QFileDialog

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM books")
            rows = cursor.fetchall()
            with open(file_name, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
        QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke data_buku.csv")

    def search_data(self):
        keyword = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1) 
            self.table.setRowHidden(row, keyword not in item.text().lower())

    def update_data(self, row, col):
        book_id = self.table.item(row, 0).text()
        new_value = self.table.item(row, col).text()
        column_map = {1: "title", 2: "author", 3: "year"}
        if col in column_map:
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE books SET {column_map[col]} = ? WHERE id = ?", (new_value, book_id))
            self.conn.commit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookApp()
    window.show()
    sys.exit(app.exec_())
