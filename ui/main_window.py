from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QStackedWidget, QMessageBox,
)

from ui.dialogs.setting_dialog import SettingsDialog
from services.config_service import load_config
from database.engine import Database
from ui.pages.drivers_page import DriversPage
from ui.pages.vehicles_page import VehiclesPage
from ui.pages.trailers_page import TrailersPage  # если сделаете по аналогии
from ui.pages.customers_page import CustomersPage
from ui.pages.waybills_page import WaybillsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диспетчер — Путевые листы")
        self.resize(1100, 700)
        self.db = None
        self._build_ui()
        self._init_db()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(
            "#sidebar { background-color: #2b2d30; }"
            "QPushButton { color: #ddd; text-align: left; padding: 10px 16px;"
            "  border: none; background: transparent; }"
            "QPushButton:hover { background-color: #3a3d42; }"
            "QPushButton:pressed { background-color: #4a4d52; }"
        )
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 12, 0, 12)
        side_layout.setSpacing(2)

        self.btn_waybills = QPushButton("Путевые листы")
        self.btn_drivers = QPushButton("Водители")
        self.btn_vehicles = QPushButton("Транспорт")
        self.btn_trailers = QPushButton("Полуприцепы")
        self.btn_customers = QPushButton("Заказчики")

        for b in (self.btn_waybills, self.btn_drivers, self.btn_vehicles,
                  self.btn_trailers, self.btn_customers):
            side_layout.addWidget(b)

        side_layout.addStretch()

        self.btn_settings = QPushButton("⚙ Настройки")
        self.btn_settings.clicked.connect(self.open_settings)
        side_layout.addWidget(self.btn_settings)

        root.addWidget(sidebar)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.btn_waybills.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_drivers.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_vehicles.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_trailers.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_customers.clicked.connect(lambda: self.stack.setCurrentIndex(4))

    def _build_pages(self):
        # Очищаем stack и создаём страницы заново (после смены БД)
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        self.stack.addWidget(WaybillsPage(self.db))
        self.stack.addWidget(DriversPage(self.db))
        self.stack.addWidget(VehiclesPage(self.db))
        self.stack.addWidget(TrailersPage(self.db))
        self.stack.addWidget(CustomersPage(self.db))

    def _init_db(self):
        config = load_config()
        db_cfg = config.get("database")
        if not db_cfg or not db_cfg.get("password"):
            self._show_connection_warning("Настройки базы данных не заполнены.")
            return
        try:
            if self.db and self.db.engine:
                self.db.engine.dispose()
            self.db = Database(db_cfg)
            self.db.connect()
            ok, msg = self.db.test_connection()
            if not ok:
                self._show_connection_warning(msg)
                return
            self._build_pages()
        except Exception as e:
            self._show_connection_warning(str(e))

    def _show_connection_warning(self, message: str):
        QMessageBox.warning(
            self, "Подключение к БД",
            f"Не удалось подключиться к базе данных:\n{message}\n\n"
            f"Откройте «Настройки» и проверьте параметры."
        )

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            self._init_db()