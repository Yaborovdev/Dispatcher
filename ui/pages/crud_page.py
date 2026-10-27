from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QAbstractItemView, QMessageBox,
)

from ui.models.table_model import RecordTableModel


class CrudPage(QWidget):
    """Базовая страница справочника: таблица + добавить / изменить / удалить.

    Наследнику нужно задать model_cls, COLUMNS, order_by и реализовать
    make_dialog() и delete_question(). Пример: ui/pages/drivers_page.py.
    """

    model_cls: type                       # ORM-класс записи
    COLUMNS: list[tuple[str, str]] = []   # (атрибут, заголовок)
    order_by: str | None = None           # имя атрибута для сортировки
    delete_error_hint: str = ""           # подсказка в тексте ошибки удаления

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.model = RecordTableModel(self.COLUMNS)
        self._build_ui()
        self.reload()

    # --- что переопределяет наследник ---------------------------------

    def make_dialog(self, record=None):
        """Диалог добавления (record=None) или редактирования записи."""
        raise NotImplementedError

    def delete_question(self, record) -> str:
        """Текст подтверждения удаления."""
        raise NotImplementedError

    def extra_toolbar_widgets(self) -> list[QWidget]:
        """Дополнительные кнопки панели (например, экспорт)."""
        return []

    # --- общая логика --------------------------------------------------

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

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.edit_record)
        layout.addWidget(self.table)

    def reload(self):
        with self.db.session_scope() as session:
            query = session.query(self.model_cls)
            if self.order_by:
                query = query.order_by(getattr(self.model_cls, self.order_by))
            self.model.set_rows(query.all())

    def _selected(self):
        idx = self.table.currentIndex()
        return self.model.record_at(idx.row()) if idx.isValid() else None

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
