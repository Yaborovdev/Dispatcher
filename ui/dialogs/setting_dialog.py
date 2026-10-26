from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, QWidget,
    QLineEdit, QSpinBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
)

from services.config_service import load_config, save_config, save_db_password
from database.engine import Database


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(480, 320)
        self._build_ui()
        self._load_current()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- Вкладка "База данных" ---
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)

        form = QFormLayout()
        self.host_edit = QLineEdit()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(5432)
        self.dbname_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # скрытый ввод

        form.addRow("Хост:", self.host_edit)
        form.addRow("Порт:", self.port_spin)
        form.addRow("База данных:", self.dbname_edit)
        form.addRow("Пользователь:", self.user_edit)
        form.addRow("Пароль:", self.password_edit)
        db_layout.addLayout(form)

        # Кнопка "Тест" + статус
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("Проверить подключение")
        self.test_btn.clicked.connect(self._on_test)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        test_row.addWidget(self.test_btn)
        test_row.addWidget(self.status_label, 1)
        db_layout.addLayout(test_row)

        db_layout.addStretch()
        self.tabs.addTab(db_tab, "База данных")

        # --- Кнопки OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_current(self):
        config = load_config()
        db = config.get("database", {})
        self.host_edit.setText(db.get("host", "localhost"))
        self.port_spin.setValue(int(db.get("port", 5432)))
        self.dbname_edit.setText(db.get("name", ""))
        self.user_edit.setText(db.get("user", ""))
        # Пароль подтягиваем из keyring, чтобы не заставлять вводить заново
        from services.config_service import KEYRING_SERVICE
        import keyring
        if db.get("user"):
            pwd = keyring.get_password(KEYRING_SERVICE, db["user"])
            if pwd:
                self.password_edit.setText(pwd)

    def _collect_db_config(self) -> dict:
        return {
            "host": self.host_edit.text().strip(),
            "port": self.port_spin.value(),
            "name": self.dbname_edit.text().strip(),
            "user": self.user_edit.text().strip(),
            "password": self.password_edit.text(),
        }

    def _on_test(self):
        cfg = self._collect_db_config()
        if not cfg["password"]:
            self._set_status(False, "Введите пароль")
            return
        self._set_status(None, "Проверка...")
        self.test_btn.setEnabled(False)
        try:
            db = Database(cfg)
            db.connect()
            ok, msg = db.test_connection()
            self._set_status(ok, msg)
            db.engine.dispose()
        except Exception as e:
            self._set_status(False, str(e))
        finally:
            self.test_btn.setEnabled(True)

    def _set_status(self, ok: bool | None, message: str):
        if ok is None:
            self.status_label.setStyleSheet("color: gray;")
        elif ok:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: red;")
        self.status_label.setText(message)

    def _on_save(self):
        cfg = self._collect_db_config()
        if not all([cfg["host"], cfg["name"], cfg["user"], cfg["password"]]):
            QMessageBox.warning(self, "Настройки", "Заполните все поля базы данных.")
            return

        # Сохраняем пароль в keyring, остальное — в JSON
        save_db_password(cfg["user"], cfg["password"])
        save_config({
            "database": {
                "host": cfg["host"],
                "port": cfg["port"],
                "name": cfg["name"],
                "user": cfg["user"],
            }
        })
        self.accept()