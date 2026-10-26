from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox,
)


class TrailerDialog(QDialog):
    def __init__(self, trailer=None, parent=None):
        super().__init__(parent)
        self.trailer = trailer
        self.setWindowTitle("Полуприцеп" if trailer is None else "Редактирование полуприцепа")
        self.resize(420, 260)
        self._build_ui()
        if trailer is not None:
            self._fill(trailer)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.brand_edit = QLineEdit()
        self.vin_edit = QLineEdit()
        self.reg_edit = QLineEdit()

        form.addRow("Марка/модель:", self.brand_edit)
        form.addRow("VIN:", self.vin_edit)
        form.addRow("Рег. номер:", self.reg_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill(self, t):
        self.brand_edit.setText(t.brand_model or "")
        self.vin_edit.setText(t.vin or "")
        self.reg_edit.setText(t.reg_number or "")

    def _on_save(self):
        if not self.brand_edit.text().strip() or not self.reg_edit.text().strip():
            QMessageBox.warning(self, "Полуприцеп", "Укажите марку и рег. номер.")
            return
        if not self.vin_edit.text().strip():
            QMessageBox.warning(self, "Полуприцеп", "Укажите VIN.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "brand_model": self.brand_edit.text().strip(),
            "vin": self.vin_edit.text().strip(),
            "reg_number": self.reg_edit.text().strip(),
        }