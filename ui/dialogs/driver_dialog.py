from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox,
    QMessageBox,
)


class DriverDialog(QDialog):
    def __init__(self, driver=None, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.setWindowTitle("Водитель" if driver is None else "Редактирование водителя")
        self.resize(420, 260)
        self._build_ui()
        if driver is not None:
            self._fill(driver)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.full_name_edit = QLineEdit()
        self.snils_edit = QLineEdit()
        self.license_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        form.addRow("ФИО:", self.full_name_edit)
        form.addRow("СНИЛС:", self.snils_edit)
        form.addRow("Вод. удостоверение:", self.license_edit)
        form.addRow("Телефон:", self.phone_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill(self, driver):
        self.full_name_edit.setText(driver.full_name or "")
        self.snils_edit.setText(driver.snils or "")
        self.license_edit.setText(driver.driver_license or "")
        self.phone_edit.setText(driver.phone or "")

    def _on_save(self):
        if not self.full_name_edit.text().strip():
            QMessageBox.warning(self, "Водитель", "Укажите ФИО.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "full_name": self.full_name_edit.text().strip(),
            "snils": self.snils_edit.text().strip(),
            "driver_license": self.license_edit.text().strip(),
            "phone": self.phone_edit.text().strip() or None,
        }