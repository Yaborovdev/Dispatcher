from database.models import Driver
from ui.dialogs.driver_dialog import DriverDialog
from ui.pages.crud_page import CrudPage


class DriversPage(CrudPage):
    model_cls = Driver
    COLUMNS = [
        ("full_name", "ФИО"),
        ("snils", "СНИЛС"),
        ("driver_license", "Вод. удостоверение"),
        ("phone", "Телефон"),
    ]
    order_by = "full_name"
    delete_error_hint = "возможно, есть путевые листы."

    def make_dialog(self, record=None):
        return DriverDialog(driver=record, parent=self)

    def delete_question(self, record) -> str:
        return f"Удалить водителя «{record.full_name}»?"
