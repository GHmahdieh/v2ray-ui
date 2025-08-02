#!/mahdieh-gharibi/bin/env python3
import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QGroupBox
)
from PyQt5.QtCore import QProcess, Qt, QPoint, QRectF
from PyQt5.QtGui import QPainterPath, QRegion

class V2RayConfigurator(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = '/home/mahdieh-gharibi/Downloads/v2ray-linux-64/config.json'
        self.v2ray_binary = '/home/mahdieh-gharibi/Downloads/v2ray-linux-64/v2ray'
        self.process = None
        self.old_pos = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('v2ray')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(600, 550)
        self.setMinimumSize(600, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #e0e0e0;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                border: 1px solid #000000;
            }
            QGroupBox {
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
                font-weight: 600;
                color: #bb86fc;
            }
            QLabel {
                font-weight: 600;
                color: #bb86fc;
                margin-bottom: 4px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #6200ee;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #3700b3;
            }
            QPushButton:pressed {
                background-color: #29006a;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton#closeButton {
                background-color: transparent;
                color: #bb86fc;
                font-weight: 900;
                font-size: 18px;
                padding: 0px;
                border: none;
            }
            QPushButton#closeButton:hover {
                color: #cf6679;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        close_layout = QHBoxLayout()
        close_layout.addStretch()

        self.close_button = QPushButton('✕')
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self.close)
        close_layout.addWidget(self.close_button)

        main_layout.addLayout(close_layout)

        config_group = QGroupBox("Connection Settings")
        config_layout = QVBoxLayout()

        self.server_input = QLineEdit(self)
        self.port_input = QLineEdit(self)
        self.protocol_input = QLineEdit(self)

        config_layout.addWidget(QLabel("🌍 Server Address:"))
        config_layout.addWidget(self.server_input)
        config_layout.addWidget(QLabel("🔌 Server Port:"))
        config_layout.addWidget(self.port_input)
        config_layout.addWidget(QLabel("📡 Protocol:"))
        config_layout.addWidget(self.protocol_input)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        self.paste_button = QPushButton('📋 Paste Config from Clipboard')
        self.paste_button.setMinimumWidth(380)
        self.paste_button.clicked.connect(self.paste_config_from_clipboard)
        main_layout.addWidget(self.paste_button)

        control_layout = QHBoxLayout()
        self.start_button = QPushButton('▶️ Start V2Ray')
        self.start_button.setMinimumWidth(180)
        self.start_button.clicked.connect(self.start_v2ray)
        self.stop_button = QPushButton('⛔ Stop V2Ray')
        self.stop_button.setMinimumWidth(180)
        self.stop_button.clicked.connect(self.stop_v2ray)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        main_layout.addLayout(control_layout)

        self.save_button = QPushButton('💾 Save Configuration')
        self.save_button.setMinimumWidth(380)
        self.save_button.clicked.connect(self.save_config)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)
        self.set_rounded_corners()

    def set_rounded_corners(self):
        path = QPainterPath()
        rect = QRectF(self.rect())
        radius = 20.0
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # اضافه شده: هر بار که پنجره resize می‌شود، گوشه‌های گرد تنظیم شود
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_rounded_corners()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def paste_config_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        config_dir = os.path.dirname(self.config_file)

        try:
            config_data = json.loads(text)

            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)

            self.show_message("✅ Configuration pasted and saved successfully!")

        except json.JSONDecodeError:
            self.show_error("❌ Clipboard does not contain valid JSON configuration.")
        except PermissionError:
            self.show_error("❌ Permission denied: check file permissions.")
        except Exception as e:
            self.show_error(f"❌ Failed to paste config: {str(e)}")

    def save_config(self):
        if not os.path.exists(self.config_file):
            self.show_error("❌ Config file not found!")
            return

        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)

            config['outbounds'][0]['settings']['servers'][0]['address'] = self.server_input.text()
            config['outbounds'][0]['settings']['servers'][0]['port'] = int(self.port_input.text())
            config['outbounds'][0]['settings']['servers'][0]['protocol'] = self.protocol_input.text()

            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=4)

            self.show_message("✅ Configuration saved successfully!")

        except Exception as e:
            self.show_error(f"❌ Error: {str(e)}")

    def start_v2ray(self):
        if self.process is not None and self.process.state() == QProcess.Running:
            self.show_error("⚠️ V2Ray is already running.")
            return

        self.process = QProcess(self)
        self.process.start(self.v2ray_binary, ['-config', self.config_file])

        if self.process.waitForStarted():
            self.set_system_proxy()
            self.show_message("🚀 V2Ray started and system proxy configured!")
        else:
            self.show_error("❌ Failed to start V2Ray.")

    def stop_v2ray(self):
        if self.process is not None and self.process.state() == QProcess.Running:
            self.process.terminate()
            self.process.waitForFinished()
            self.unset_system_proxy()
            self.show_message("🛑 V2Ray stopped and proxy removed.")
            self.process = None
        else:
            self.show_error("⚠️ V2Ray is not running.")

    def set_system_proxy(self):
        try:
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"], check=True)
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy.socks", "host", "127.0.0.1"], check=True)
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy.socks", "port", "10809"], check=True)
        except subprocess.CalledProcessError as e:
            self.show_error(f"❌ Failed to set system proxy: {e}")

    def unset_system_proxy(self):
        try:
            subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"], check=True)
        except subprocess.CalledProcessError as e:
            self.show_error(f"❌ Failed to unset system proxy: {e}")

    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.exec_()

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = V2RayConfigurator()
    window.show()
    sys.exit(app.exec_())
