from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QTextEdit, QDialogButtonBox, QMessageBox,
)

from database.models import Driver, Vehicle, Trailer, Customer

TEMPLATE_TYPES = ["междугородний", "грузовой", "спецтехника", "автокран", "легковой"]


class WaybillDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Новый путевой лист")
        self.resize(520, 620)
        self._build_ui()
        self._load_lists()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.number_edit = QLineEdit()
        self.date_issue = QDateEdit(calendarPopup=True)
        self.date_issue.setDate(QDate.currentDate())
        self.date_start = QDateEdit(calendarPopup=True)
        self.date_start.setDate(QDate.currentDate())
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setDate(QDate.currentDate().addDays(1))

        self.driver_combo = QComboBox()
        self.vehicle_combo = QComboBox()
        self.trailer_combo = QComboBox()
        self.customer_combo = QComboBox()
        self.template_combo = QComboBox()
        self.template_combo.addItems(TEMPLATE_TYPES)
        self.route_edit = QTextEdit()
        self.route_edit.setFixedHeight(80)

        form.addRow("Номер ПЛ:", self.number_edit)
        form.addRow("Дата выдачи:", self.date_issue)
        form.addRow("Действует с:", self.date_start)
        form.addRow("Действует по:", self.date_end)
        form.addRow("Водитель:", self.driver_combo)
        form.addRow("Транспорт:", self.vehicle_combo)
        form.addRow("Полуприцеп:", self.trailer_combo)
        form.addRow("Заказчик:", self.customer_combo)
        form.addRow("Тип шаблона:", self.template_combo)
        form.addRow("Маршрут:", self.route_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_lists(self):
        session = self.db.get_session()
        try:
            self.driver_combo.clear()
            for d in session.query(Driver).order_by(Driver.full_name).all():
                self.driver_combo.addItem(d.full_name, d.id)

            self.vehicle_combo.clear()
            for v in session.query(Vehicle).order_by(Vehicle.brand_model).all():
                self.vehicle_combo.addItem(f"{v.brand_model} ({v.gov_number})", v.id)

            self.trailer_combo.clear()
            self.trailer_combo.addItem("— нет —", None)
            for t in session.query(Trailer).order_by(Trailer.brand_model).all():
                self.trailer_combo.addItem(f"{t.brand_model} ({t.reg_number})", t.id)

            self.customer_combo.clear()
            self.customer_combo.addItem("— нет —", None)
            for c in session.query(Customer).order_by(Customer.name).all():
                self.customer_combo.addItem(c.name, c.id)
        finally:
            session.close()

    def _on_save(self):
        if not self.number_edit.text().strip():
            QMessageBox.warning(self, "ПЛ", "Укажите номер путевого листа.")
            return
        if self.driver_combo.currentData() is None:
            QMessageBox.warning(self, "ПЛ", "Добавьте хотя бы одного водителя.")
            return
        if self.vehicle_combo.currentData() is None:
            QMessageBox.warning(self, "ПЛ", "Добавьте хотя бы одно ТС.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "number": self.number_edit.text().strip(),
            "date_issue": self.date_issue.date().toPython(),
            "date_start": self.date_start.date().toPython(),
            "date_end": self.date_end.date().toPython(),
            "route": self.route_edit.toPlainText().strip() or None,
            "template_type": self.template_combo.currentText(),
            "driver_id": self.driver_combo.currentData(),
            "vehicle_id": self.vehicle_combo.currentData(),
            "trailer_id": self.trailer_combo.currentData(),
            "customer_id": self.customer_combo.currentData(),
        }