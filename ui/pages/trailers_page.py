from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox,
)

from database.models import Trailer
from ui.models.table_model import RecordTableModel
from ui.dialogs.trailer_dialog import TrailerDialog


class TrailersPage(QWidget):
    model_cls = Trailer
    COLUMNS = [
        ("brand_model", "Марка/модель"),
        ("vin", "VIN"),
        ("reg_number", "Рег. номер"),
    ]
    order_by = "brand_model"
    delete_error_hint = "возможно, есть путевые листы."

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
            rows = session.query(Trailer).order_by(Trailer.brand_model).all()
            self.model.set_rows(rows)
        finally:
            session.close()

    def _selected(self) -> Trailer | None:
        idx = self.table.currentIndex()
        return self.model.record_at(idx.row()) if idx.isValid() else None

    def add_record(self):
        dlg = TrailerDialog(parent=self)
        if not dlg.exec():
            return
        session = self.db.get_session()
        try:
            session.add(Trailer(**dlg.get_data()))
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()
        self.reload()

    def edit_record(self):
        t = self._selected()
        if t is None:
            return
        dlg = TrailerDialog(trailer=t, parent=self)
        if not dlg.exec():
            return
        session = self.db.get_session()
        try:
            obj = session.get(Trailer, t.id)
            for k, val in dlg.get_data().items():
                setattr(obj, k, val)
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()
        self.reload()

    def delete_record(self):
        t = self._selected()
        if t is None:
            return
        if QMessageBox.question(
            self, "Удаление",
            f"Удалить полуприцеп «{t.brand_model}»?",
        ) != QMessageBox.Yes:
            return
        session = self.db.get_session()
        try:
            session.delete(session.get(Trailer, t.id))
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