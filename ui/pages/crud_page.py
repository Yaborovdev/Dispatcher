from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox, QLineEdit,
)

from ui.models.table_model import RecordTableModel
from ui.models.proxy import SearchProxyModel


class CrudPage(QWidget):
    model_cls: type
    COLUMNS: list[tuple[str, str]] = []
    order_by: str | None = None
    search_columns: list[int] | None = None   # None = искать по всем колонкам
    delete_error_hint: str = ""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.model = RecordTableModel(self.COLUMNS)
        self.proxy = SearchProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.set_search_columns(self.search_columns)
        self._build_ui()
        self.reload()

    def make_dialog(self, record=None):
        raise NotImplementedError

    def delete_question(self, record) -> str:
        raise NotImplementedError

    def extra_toolbar_widgets(self) -> list[QWidget]:
        return []

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

        for w in (self.btn_add, self.btn_edit, self.btn_delete, *self.extra_toolbar_widgets()):
            toolbar.addWidget(w)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        layout.addLayout(toolbar)

        # Строка поиска
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск…")
        self.search_edit.textChanged.connect(self._on_search)
        layout.addWidget(self.search_edit)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)  # сортировка по клику на заголовок
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.edit_record)
        layout.addWidget(self.table)

    def _on_search(self, text: str):
        self.proxy.setFilterFixedString(text)

    def reload(self):
        with self.db.session_scope() as session:
            query = session.query(self.model_cls)
            if self.order_by:
                query = query.order_by(getattr(self.model_cls, self.order_by))
            self.model.set_rows(query.all())

    def _selected(self):
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        source_idx = self.proxy.mapToSource(idx)
        return self.model.record_at(source_idx.row())

    def add_record(self):
        dlg = self.make_dialog()
        if not dlg.exec():
            return
        try:
            with self.db.session_scope() as session:
                session.add(self.model_cls(**dlg.get_data()))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        self.reload()

    def edit_record(self):
        record = self._selected()
        if record is None:
            return
        dlg = self.make_dialog(record)
        if not dlg.exec():
            return
        try:
            with self.db.session_scope() as session:
                obj = session.get(self.model_cls, record.id)
                for key, value in dlg.get_data().items():
                    setattr(obj, key, value)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        self.reload()

    def delete_record(self):
        record = self._selected()
        if record is None:
            return
        if QMessageBox.question(self, "Удаление", self.delete_question(record)) != QMessageBox.Yes:
            return
        try:
            with self.db.session_scope() as session:
                session.delete(session.get(self.model_cls, record.id))
        except Exception as e:
            hint = f"{self.delete_error_hint}\n" if self.delete_error_hint else ""
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {hint}{e}")
        self.reload()