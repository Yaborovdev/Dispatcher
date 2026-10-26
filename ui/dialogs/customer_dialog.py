from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox,
)


class CustomerDialog(QDialog):
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Заказчик" if customer is None else "Редактирование заказчика")
        self.resize(420, 240)
        self._build_ui()
        if customer is not None:
            self._fill(customer)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.inn_edit = QLineEdit()
        form.addRow("Наименование:", self.name_edit)
        form.addRow("Адрес:", self.address_edit)
        form.addRow("ИНН:", self.inn_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _fill(self, c):
        self.name_edit.setText(c.name or "")
        self.address_edit.setText(c.address or "")
        self.inn_edit.setText(c.inn or "")

    def _on_save(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Заказчик", "Укажите наименование.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "address": self.address_edit.text().strip() or None,
            "inn": self.inn_edit.text().strip() or None,
        }