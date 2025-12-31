import sys
import pymysql
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QTextEdit, QVBoxLayout,
    QHBoxLayout, QTableWidget,
    QTableWidgetItem, QSplitter
)


"""
Configuration BDD
"""

CONFIG_BDD = {
    "host": "192.168.106.10",
    "user": "toto",
    "password": "toto",
    "database": "tor_sondag"
}


"""
GUI Master
"""
class MasterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Master Oignon")
        self.resize(900, 600)

        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: #000000; font-family: Arial; font-size: 12px; }
            QLabel { color: #1976D2; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
            QTableWidget { background-color: #ffffff; color: #000000; gridline-color: #cccccc; border: 1px solid #cccccc; }
            QHeaderView::section { background-color: #e0e0e0; color: #000000; border: 1px solid #cccccc; }
            QTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; }
        """)

        self.title = QLabel("Master Oignon — Supervision distante")
        self.title.setStyleSheet("font-size: 14px;")

        # Boutons
        self.btn_refresh_routers = QPushButton("Rafraîchir les routeurs")
        self.btn_refresh_logs = QPushButton("Rafraîchir les logs")

        # Table routeurs
        self.router_table = QTableWidget()
        self.router_table.setColumnCount(3)
        self.router_table.setHorizontalHeaderLabels(["IP", "Port", "Clé publique"])

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)

        # Layout gauche (contrôles + table)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.title)
        left_layout.addWidget(self.btn_refresh_routers)
        left_layout.addWidget(self.btn_refresh_logs)
        left_layout.addWidget(QLabel("Routeurs enregistrés :"))
        left_layout.addWidget(self.router_table)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Layout droite (logs)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Logs du master :"))
        right_layout.addWidget(self.logs)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Splitter horizontal
        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Connexions
        self.btn_refresh_routers.clicked.connect(self.load_routers)
        self.btn_refresh_logs.clicked.connect(self.load_logs)

        # Chargement initial
        self.load_routers()
        self.load_logs()

    """
    BDD
    """
    def get_db(self):
        return pymysql.connect(**CONFIG_BDD)

    def load_routers(self):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ip, port, pubkey FROM routeurs")
            rows = cursor.fetchall()

            self.router_table.setRowCount(len(rows))
            for i, (ip, port, pubkey) in enumerate(rows):
                self.router_table.setItem(i, 0, QTableWidgetItem(ip))
                self.router_table.setItem(i, 1, QTableWidgetItem(str(port)))
                self.router_table.setItem(i, 2, QTableWidgetItem(str(pubkey)))

            conn.close()
        except Exception as e:
            self.logs.append(f"[ERREUR BDD routeurs] {e}")

    def load_logs(self):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, source, message
                FROM logs
                ORDER BY id DESC
                LIMIT 50
            """)
            rows = cursor.fetchall()
            conn.close()

            self.logs.clear()
            for ts, src, msg in reversed(rows):
                self.logs.append(f"[{ts}] {src} : {msg}")

        except Exception as e:
            self.logs.append(f"[ERREUR BDD logs] {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MasterGUI()
    gui.show()
    sys.exit(app.exec_())