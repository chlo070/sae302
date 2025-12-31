import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QTextEdit, QVBoxLayout,
    QLineEdit, QSplitter
)
from PyQt5.QtCore import QProcess, QProcessEnvironment, QByteArray


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client Oignon")
        self.resize(800, 500)

        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: #000000; font-family: Arial; font-size: 12px; }
            QLabel { color: #1976D2; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
            QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; padding: 4px; }
            QTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; }
        """)

        self.label = QLabel("Client Oignon – Envoi de message")
        self.label.setStyleSheet("font-size: 14px;")

        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Message à envoyer")

        self.send_btn = QPushButton("Envoyer")

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        # Layout gauche (contrôles)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.label)
        left_layout.addWidget(self.input_msg)
        left_layout.addWidget(self.send_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Layout droite (logs)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Logs du client :"))
        right_layout.addWidget(self.log_area)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Splitter horizontal
        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.process = QProcess(self)

        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUTF8", "1")
        self.process.setProcessEnvironment(env)

        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)

        self.send_btn.clicked.connect(self.send_message)

    def log(self, message, level="INFO"):
        colors = {
            "INFO": "#2196F3",  # bleu
            "ERREUR": "#F44336",  # rouge
            "OIGNON": "#4CAF50"  # vert
        }
        color = colors.get(level, "white")
        self.log_area.append(f'<span style="color:{color}">{message}</span>')

    def send_message(self):
        msg = self.input_msg.text().strip()
        if not msg:
            return

        self.log("[GUI] Envoi du message...<br>", "INFO")
        self.process.start(
            "python",
            ["noeud.py", "--role", "clienta", "--msg", msg]
        )

    def read_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")

        # Sauts de ligne dans noeud.py
        text = text.replace('\n', '<br>')

        # Colorisation selon le message
        if "Chiffrement" in text or "Oignon" in text or "Circuit" in text:
            self.log(text, "OIGNON")
        else:
            self.log(text, "INFO")

    def read_stderr(self):
        data: QByteArray = self.process.readAllStandardError()
        text = bytes(data).decode("utf-8")
        self.log("[ERREUR]<br>" + text, "ERREUR")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ClientGUI()
    gui.show()
    sys.exit(app.exec_())
