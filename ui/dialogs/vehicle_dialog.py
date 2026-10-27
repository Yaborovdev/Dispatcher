from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDialogButtonBox, QMessageBox,
)


VEHICLE_TYPES = ["легковой", "грузовой", "спецтехника", "автокран"]


class VehicleDialog(QDialog):
    def __init__(self, vehicle=None, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle("Транспорт" if vehicle is None else "Редактирование ТС")
        self.resize(420, 280)
        self._build_ui()
        if vehicle is not None:
            self._fill(vehicle)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(VEHICLE_TYPES)
        self.brand_edit = QLineEdit()
        self.gov_edit = QLineEdit()
        self.vin_edit = QLineEdit()
        self.odometer_spin = QSpinBox()
        self.odometer_spin.setRange(0, 10_000_000)

        form.addRow("Тип:", self.type_combo)
        form.addRow("Марка/модель:", self.brand_edit)
        form.addRow("Госномер:", self.gov_edit)
        form.addRow("VIN:", self.vin_edit)
        form.addRow("Пробег (одометр):", self.odometer_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill(self, v):
        idx = self.type_combo.findText(v.type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.brand_edit.setText(v.brand_model or "")
        self.gov_edit.setText(v.gov_number or "")
        self.vin_edit.setText(v.vin or "")
        self.odometer_spin.setValue(v.odometer_start or 0)

    def _on_save(self):
        if not self.brand_edit.text().strip() or not self.gov_edit.text().strip():
            QMessageBox.warning(self, "Транспорт", "Укажите марку и госномер.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "type": self.type_combo.currentText(),
            "brand_model": self.brand_edit.text().strip(),
            "gov_number": self.gov_edit.text().strip(),
            "vin": self.vin_edit.text().strip(),
            "odometer_start": self.odometer_spin.value(),
        }