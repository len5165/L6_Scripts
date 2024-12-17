import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QWidget, QLineEdit, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class DataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Visualizer")
        self.setGeometry(100, 100, 800, 600)

        self.data = None

        self.initUI()

    def initUI(self):
        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Макет
        self.layout = QVBoxLayout(self.central_widget)

        # Кнопка загрузки
        self.load_button = QPushButton("Загрузить CSV")
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        # Метка для отображения статистики
        self.stats_label = QLabel("Статистика данных:")
        self.layout.addWidget(self.stats_label)

        # Поле для ввода нового значения
        self.add_value_layout = QHBoxLayout()
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Введите значение для добавления")
        self.add_button = QPushButton("Добавить значение")
        self.add_button.clicked.connect(self.add_data)
        self.add_value_layout.addWidget(self.value_input)
        self.add_value_layout.addWidget(self.add_button)
        self.layout.addLayout(self.add_value_layout)

        # Выбор типа графика
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Линейный график", "Гистограмма", "Круговая диаграмма"])
        self.chart_type_combo.currentIndexChanged.connect(self.update_plot)
        self.layout.addWidget(self.chart_type_combo)

        # Поле для отображения графика
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def load_data(self):
        # Открытие диалога для выбора файла
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)

        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.update_stats()
                self.update_plot()
            except Exception as e:
                self.stats_label.setText(f"Ошибка загрузки данных: {e}")

    def update_stats(self):
        if self.data is not None:
            num_rows, num_cols = self.data.shape
            stats = f"Количество строк: {num_rows}\nКоличество столбцов: {num_cols}\n"
            for col in self.data.columns:
                if pd.api.types.is_numeric_dtype(self.data[col]):
                    stats += f"{col} -> Мин: {self.data[col].min()}, Макс: {self.data[col].max()}\n"
            self.stats_label.setText(stats)
        else:
            self.stats_label.setText("Данные не загружены")

    def update_plot(self):
        if self.data is not None:
            chart_type = self.chart_type_combo.currentText()

            # Очистка фигуры перед построением нового графика
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            try:
                if chart_type == "Линейный график":
                    if "Date" in self.data.columns and "Value1" in self.data.columns:
                        ax.plot(self.data["Date"], self.data["Value1"], marker='o')
                        ax.set_title("Линейный график")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Value1")
                elif chart_type == "Гистограмма":
                    if "Date" in self.data.columns and "Value2" in self.data.columns:
                        ax.bar(self.data["Date"], self.data["Value2"], color='orange')
                        ax.set_title("Гистограмма")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Value2")
                elif chart_type == "Круговая диаграмма":
                    if "Category" in self.data.columns:
                        category_counts = self.data["Category"].value_counts()
                        ax.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%", startangle=90)
                        ax.set_title("Круговая диаграмма")
            except Exception as e:
                self.stats_label.setText(f"Ошибка построения графика: {e}")

            # Обновление графического компонента
            self.canvas.draw()
        else:
            self.stats_label.setText("Данные не загружены")

    def add_data(self):
        if self.data is not None and not self.value_input.text().strip() == "":
            new_value = self.value_input.text().strip()

            try:
                chart_type = self.chart_type_combo.currentText()

                if chart_type in ["Линейный график", "Гистограмма"]:
                    # Проверяем, является ли введенное значение числом
                    new_value = float(new_value)

                    # Генерация нового значения для "Date"
                    new_date = f"New_{len(self.data)}"

                    if chart_type == "Линейный график" and "Value1" in self.data.columns:
                        self.data = pd.concat([self.data, pd.DataFrame({"Date": [new_date], "Value1": [new_value]})],
                                              ignore_index=True)
                    elif chart_type == "Гистограмма" and "Value2" in self.data.columns:
                        self.data = pd.concat([self.data, pd.DataFrame({"Date": [new_date], "Value2": [new_value]})],
                                              ignore_index=True)
                elif chart_type == "Круговая диаграмма":
                    # Для круговой диаграммы добавляем новую категорию
                    if "Category" in self.data.columns:
                        self.data = pd.concat([self.data, pd.DataFrame({"Category": [new_value]})], ignore_index=True)
                else:
                    self.stats_label.setText("Неизвестный тип графика или данные не поддерживаются.")

                # Обновляем статистику и график
                self.update_stats()
                self.update_plot()
            except ValueError:
                self.stats_label.setText(
                    "Некорректный ввод. Введите числовое значение для графика или строку для категорий.")
        else:
            self.stats_label.setText("Данные не загружены или поле ввода пусто.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DataVisualizer()
    main_window.show()
    sys.exit(app.exec_())
