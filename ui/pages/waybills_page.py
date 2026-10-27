from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox, QFileDialog, QLineEdit,
)

from database.models import Waybill
from ui.models.table_model import RecordTableModel
from ui.models.proxy import SearchProxyModel
from ui.dialogs.waybill_dialog import WaybillDialog
from services.excel_service import fill_waybill_template


class WaybillsPage(QWidget):
    # Добавляем id в COLUMNS, но потом скроем его через setColumnHidden
    COLUMNS = [
        ("id", "ID"),
        ("number", "Номер"),
        ("date_issue", "Дата выдачи"),
        ("_driver_name", "Водитель"),
        ("_vehicle_label", "ТС"),
        ("customer_name", "Заказчик"),
        ("route", "Маршрут"),
        ("template_type", "Шаблон"),
    ]

    # Индексы для поиска: номер (1), водитель (3), машина (4)
    SEARCH_COLUMNS = [1, 3, 4]

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.model = RecordTableModel(self.COLUMNS)
        self.proxy = SearchProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.set_search_columns(self.SEARCH_COLUMNS)
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

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по номеру, водителю или машине…")
        self.search_edit.textChanged.connect(self.proxy.setFilterFixedString)
        layout.addWidget(self.search_edit)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Скрываем колонку ID (индекс 0)
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

    def reload(self):
        with self.db.session_scope() as session:
            rows = (
                session.query(Waybill)
                .order_by(Waybill.number.desc())  # новые сверху
                .all()
            )
            for r in rows:
                # Заполняем виртуальные атрибуты для отображения
                r._driver_name = r.driver.full_name if r.driver else ""
                r._vehicle_label = (
                    f"{r.vehicle.brand_model} ({r.vehicle.gov_number})"
                    if r.vehicle else ""
                )
                r.customer_name = r.customer.name if r.customer else ""
            self.model.set_rows(rows)

        # Сортировка по колонке "Номер" (индекс 1) по убыванию
        self.table.sortByColumn(1, Qt.DescendingOrder)

    def _selected(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        source_idx = self.proxy.mapToSource(idx)
        return self.model.record_at(source_idx.row())

    def add_record(self):
        dlg = WaybillDialog(self.db, parent=self)
        if not dlg.exec():
            return
        try:
            with self.db.session_scope() as session:
                session.add(Waybill(**dlg.get_data()))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
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

        try:
            with self.db.session_scope() as session:
                obj = session.get(Waybill, w.id)
                saved = fill_waybill_template(obj, path)
            QMessageBox.information(self, "Excel", f"Файл сохранён:\n{saved}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка Excel", str(e))

    def delete_record(self):
        w = self._selected()
        if w is None:
            return
        if QMessageBox.question(
            self, "Удаление", f"Удалить путевой лист №{w.number}?"
        ) != QMessageBox.Yes:
            return
        try:
            with self.db.session_scope() as session:
                session.delete(session.get(Waybill, w.id))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {e}")
        self.reload()