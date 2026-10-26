from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox, QFileDialog,
)

from database.models import Waybill
from ui.models.table_model import RecordTableModel
from ui.dialogs.waybill_dialog import WaybillDialog
from services.excel_service import fill_waybill_template


class WaybillsPage(QWidget):
    COLUMNS = [
        ("number", "Номер"),
        ("date_issue", "Дата выдачи"),
        ("_driver_name", "Водитель"),
        ("_vehicle_label", "ТС"),
        ("customer_name", "Заказчик"),
        ("route", "Маршрут"),
        ("template_type", "Шаблон"),
    ]

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.model = RecordTableModel(self.COLUMNS)
        self._build_ui()
        self.reload()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Создать ПЛ")
        self.btn_export = QPushButton("Сохранить в Excel")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.add_record)
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.reload)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_export)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        layout.addLayout(toolbar)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def reload(self):
        session = self.db.get_session()
        try:
            rows = session.query(Waybill).order_by(Waybill.date_issue.desc()).all()
            for r in rows:
                r._driver_name = r.driver.full_name if r.driver else ""
                r._vehicle_label = (
                    f"{r.vehicle.brand_model} ({r.vehicle.gov_number})"
                    if r.vehicle else ""
                )
                r.customer_name = r.customer.name if r.customer else ""
            self.model.set_rows(rows)
        finally:
            session.close()

    def _selected(self):
        idx = self.table.currentIndex()
        return self.model.record_at(idx.row()) if idx.isValid() else None

    def add_record(self):
        dlg = WaybillDialog(self.db, parent=self)
        if not dlg.exec():
            return
        session = self.db.get_session()
        try:
            session.add(Waybill(**dlg.get_data()))
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()
        self.reload()

    def export_to_excel(self):
        w = self._selected()
        if w is None:
            QMessageBox.information(self, "Excel", "Выберите путевой лист в таблице.")
            return

        default_name = f"ПЛ_{w.number}_{w.date_issue.strftime('%Y%m%d')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить путевой лист", default_name, "Excel (*.xlsx)"
        )
        if not path:
            return

        session = self.db.get_session()
        try:
            obj = session.get(Waybill, w.id)
            saved = fill_waybill_template(obj, path)
            QMessageBox.information(self, "Excel", f"Файл сохранён:\n{saved}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка Excel", str(e))
        finally:
            session.close()

    def delete_record(self):
        w = self._selected()
        if w is None:
            return
        if QMessageBox.question(
            self, "Удаление", f"Удалить путевой лист №{w.number}?"
        ) != QMessageBox.Yes:
            return
        session = self.db.get_session()
        try:
            session.delete(session.get(Waybill, w.id))
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")
        finally:
            session.close()
        self.reload()