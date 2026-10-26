from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox,
)

from database.models import Driver
from ui.models.table_model import RecordTableModel
from ui.dialogs.driver_dialog import DriverDialog


class DriversPage(QWidget):
    COLUMNS = [
        ("full_name", "ФИО"),
        ("snils", "СНИЛС"),
        ("driver_license", "Вод. удостоверение"),
        ("phone", "Телефон"),
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
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.reload)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
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
        self.table.doubleClicked.connect(self.edit_record)
        layout.addWidget(self.table)

    def reload(self):
        session = self.db.get_session()
        try:
            rows = session.query(Driver).order_by(Driver.full_name).all()
            self.model.set_rows(rows)
        finally:
            session.close()

    def _selected(self) -> Driver | None:
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        return self.model.record_at(idx.row())

    def add_record(self):
        dlg = DriverDialog(parent=self)
        if not dlg.exec():
            return
        session = self.db.get_session()
        try:
            session.add(Driver(**dlg.get_data()))
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()
        self.reload()

    def edit_record(self):
        driver = self._selected()
        if driver is None:
            return
        dlg = DriverDialog(driver=driver, parent=self)
        if not dlg.exec():
            return
        session = self.db.get_session()
        try:
            obj = session.get(Driver, driver.id)
            for k, v in dlg.get_data().items():
                setattr(obj, k, v)
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()
        self.reload()

    def delete_record(self):
        driver = self._selected()
        if driver is None:
            return
        if QMessageBox.question(
            self, "Удаление",
            f"Удалить водителя «{driver.full_name}»?",
        ) != QMessageBox.Yes:
            return
        session = self.db.get_session()
        try:
            obj = session.get(Driver, driver.id)
            session.delete(obj)
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось удалить: возможно, есть путевые листы.\n{e}"
            )
        finally:
            session.close()
        self.reload()