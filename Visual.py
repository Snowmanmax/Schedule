import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel, QMessageBox
class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расписание")
        self.setGeometry(100, 100, 800, 600)

        # Комбобоксы для выбора группы и дня
        self.group_combo = QComboBox()
        self.day_combo = QComboBox()
        self.load_button = QPushButton("Загрузить расписание")
        self.load_button.clicked.connect(self.load_schedule)

        # Инициализация таблицы
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Лекция", "Время", "Аудитория", "День", "Номер дня", "Группа"])

        # Заполнение комбобоксов
        self.populate_group_combo()

        # Установка макета
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите группу:"))
        layout.addWidget(self.group_combo)
        layout.addWidget(QLabel("Выберите день:"))
        layout.addWidget(self.day_combo)
        layout.addWidget(self.load_button)
        layout.addWidget(self.table_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_group_combo(self):
        try:
            with psycopg2.connect(database="mtusi", user="postgres", password="wml3Kk8El", host="localhost", port="5432") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, GROUP_NAME FROM schedule.GROUP_WEEKS")
                groups = cursor.fetchall()
                for group in groups:
                    self.group_combo.addItem(group[1], group[0])  # Добавляем номер группы и id в качестве данных
                self.populate_day_combo()  # Заполняем дни после загрузки групп
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить группы: {e}")

    def populate_day_combo(self):
        try:
            selected_group_id = self.group_combo.currentData()
            with psycopg2.connect(database="mtusi", user="postgres", password="wml3Kk8El", host="localhost", port="5432") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, DAY_NAME FROM schedule.GROUP_DAYS WHERE WEEK_ID = %s", (selected_group_id,))
                days = cursor.fetchall()
                self.day_combo.clear()  # Очищаем предыдущие дни
                for day in days:
                    self.day_combo.addItem(day[1], day[0])  # Добавляем день и его ID
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить дни: {e}")

    def load_schedule(self):
        selected_group_id = self.group_combo.currentData()
        selected_day_id = self.day_combo.currentData()

        try:
            with psycopg2.connect(database="mtusi", user="postgres", password="wml3Kk8El", host="localhost", port="5432") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT gl.ID, gl.LECTURE_NAME, gl.LECTURE_TIME, gl.LECTURE_ROOM, gd.DAY_NAME, gd.DAY_NUM, gw.GROUP_NAME
                    FROM schedule.GROUP_LECTURES gl
                    JOIN schedule.GROUP_DAYS gd ON gl.DAY_ID = gd.ID
                    JOIN schedule.GROUP_WEEKS gw ON gd.WEEK_ID = gw.ID
                    WHERE gd.ID = %s
                """, (selected_day_id,))
                rows = cursor.fetchall()

                self.table_widget.setRowCount(len(rows))
                for row_index, row_data in enumerate(rows):
                    for column_index, item in enumerate(row_data):
                        self.table_widget.setItem(row_index, column_index, QTableWidgetItem(str(item)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить расписание: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec_())