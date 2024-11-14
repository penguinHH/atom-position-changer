import sys
import numpy as np
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel, QFileDialog, QLineEdit, QCheckBox, QComboBox
from PyQt5.QtCore import Qt

class AtomChangerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atom Coordinates Changer")
        self.setGeometry(200, 200, 800, 600)

        # GUI elements
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        self.language_selector = QComboBox()
        self.language_selector.addItem("English")
        self.language_selector.addItem("日本語")
        self.language_selector.addItem("中文")  # Added Chinese language option
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.layout.addWidget(self.language_selector)

        self.range_label = QLabel("Enter atom number range (e.g., 1-5, 10-15):")
        self.layout.addWidget(self.range_label)

        self.range_input = QLineEdit(self)
        self.layout.addWidget(self.range_input)

        self.value_label = QLabel("Enter coordinate change value (in Angstrom):")
        self.layout.addWidget(self.value_label)

        self.value_input = QLineEdit(self)
        self.layout.addWidget(self.value_input)

        self.axis_x_checkbox = QCheckBox("Modify X axis")
        self.layout.addWidget(self.axis_x_checkbox)

        self.axis_y_checkbox = QCheckBox("Modify Y axis")
        self.layout.addWidget(self.axis_y_checkbox)

        self.axis_z_checkbox = QCheckBox("Modify Z axis")
        self.layout.addWidget(self.axis_z_checkbox)

        self.coord_text = QTextEdit(self)
        self.coord_text.setReadOnly(True)
        self.layout.addWidget(self.coord_text)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.header_input = QTextEdit()
        self.header_input.setPlaceholderText("Enter custom file header here...")
        self.layout.addWidget(QLabel("File Header"))
        self.layout.addWidget(self.header_input)

        self.footer_input = QTextEdit()
        self.footer_input.setPlaceholderText("Enter custom file footer here...")
        self.layout.addWidget(QLabel("File Footer"))
        self.layout.addWidget(self.footer_input)

        self.load_file_button = QPushButton("Load .gjf File")
        self.load_file_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_file_button)

        self.modify_button = QPushButton("Modify Coordinates")
        self.modify_button.clicked.connect(self.modify_coordinates)
        self.layout.addWidget(self.modify_button)

        self.save_file_button = QPushButton("Save Modified File")
        self.save_file_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_file_button)

        self.setCentralWidget(self.central_widget)

        # Variables to store data
        self.file_name = None
        self.line_data = []  # Store lines from file (both atom and non-atom)

        # Initial language setting
        self.language = 'en'
        self.update_ui_text()

    def change_language(self):
        if self.language_selector.currentIndex() == 0:
            self.language = 'en'
        elif self.language_selector.currentIndex() == 1:
            self.language = 'ja'
        else:
            self.language = 'zh'  # Set language to Chinese
        self.update_ui_text()

    def update_ui_text(self):
        if self.language == 'en':
            self.range_label.setText("Enter atom number range (e.g., 1-5, 10-15):")
            self.value_label.setText("Enter coordinate change value (in Angstrom):")
            self.load_file_button.setText("Load .gjf File")
            self.modify_button.setText("Modify Coordinates")
            self.save_file_button.setText("Save Modified File")
            self.header_input.setPlaceholderText("Enter custom file header here...")
            self.footer_input.setPlaceholderText("Enter custom file footer here...")
        elif self.language == 'ja':
            self.range_label.setText("原子番号範囲を入力してください（例：1-5, 10-15）:")
            self.value_label.setText("座標変更値を入力してください（単位：Å）:")
            self.load_file_button.setText("ファイルを読み込む")
            self.modify_button.setText("座標を変更する")
            self.save_file_button.setText("変更されたファイルを保存する")
            self.header_input.setPlaceholderText("カスタムファイルヘッダーをここに入力...")
            self.footer_input.setPlaceholderText("カスタムファイルフッターをここに入力...")
        else:  # For Chinese (zh)
            self.range_label.setText("请输入原子编号范围（例如：1-5, 10-15）：")
            self.value_label.setText("请输入坐标修改值（单位：Å）：")
            self.load_file_button.setText("加载 .gjf 文件")
            self.modify_button.setText("修改坐标")
            self.save_file_button.setText("保存修改后的文件")
            self.header_input.setPlaceholderText("在此输入自定义文件头...")
            self.footer_input.setPlaceholderText("在此输入自定义文件尾...")

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .gjf File", "", "Gaussian Files (*.gjf);;All Files (*)", options=options)
        if file_name:
            self.file_name = file_name
            self.result_text.append(f"File Loaded: {file_name}")
            self.read_file(file_name)

    def read_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()

            self.line_data = []
            self.atom_lines = []

            for line in lines:
                # Match atom lines with elements and 3 coordinates
                match = re.match(r"^\s*(\w+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)", line)
                if match:
                    element, x, y, z = match.groups()
                    self.atom_lines.append({
                        'line': line,  # Keep the entire line
                        'element': element,
                        'x': float(x),
                        'y': float(y),
                        'z': float(z)
                    })
            # Rebuild the whole content with atom lines and non-atom lines
            self.display_coordinates()

        except Exception as e:
            self.result_text.append(f"Error reading file: {str(e)}")

    def display_coordinates(self):
        self.coord_text.clear()
        for idx, atom in enumerate(self.atom_lines):
            self.coord_text.append(f"Atom {idx + 1}: {atom['element']} ({atom['x']:.6f}, {atom['y']:.6f}, {atom['z']:.6f})")

    def modify_coordinates(self):
        if not self.file_name:
            self.result_text.append("Please load a file first.")
            return

        try:
            range_input = self.range_input.text().strip()
            value_input = self.value_input.text().strip()

            if not value_input:
                self.result_text.append("Please provide a coordinate change value.")
                return

            increment_value = float(value_input)
            selected_atoms = self.parse_atom_range(range_input)

            if not selected_atoms:
                self.result_text.append(f"Invalid atom number range: {range_input}")
                return

            modify_x = self.axis_x_checkbox.isChecked()
            modify_y = self.axis_y_checkbox.isChecked()
            modify_z = self.axis_z_checkbox.isChecked()

            # Modify the selected atoms' coordinates
            for idx in selected_atoms:
                if idx < len(self.atom_lines):
                    atom = self.atom_lines[idx]
                    if modify_x:
                        atom['x'] += increment_value
                    if modify_y:
                        atom['y'] += increment_value
                    if modify_z:
                        atom['z'] += increment_value
                    self.atom_lines[idx] = atom

            # Rebuild the coordinates and display them again
            self.display_coordinates()

            self.result_text.append("Coordinates modified successfully!")

        except ValueError:
            self.result_text.append("Invalid input value. Please enter a number.")

    def parse_atom_range(self, range_input):
        selected_atoms = []
        try:
            ranges = range_input.split(',')
            for r in ranges:
                if '-' in r:
                    start, end = map(int, r.split('-'))
                    selected_atoms.extend(range(start - 1, end))  # 1-based to 0-based index
                else:
                    selected_atoms.append(int(r) - 1)  # 1-based to 0-based index
        except ValueError:
            self.result_text.append("Invalid atom number range format.")
            return []
        return selected_atoms

    def save_file(self):
        if not self.file_name:
            self.result_text.append("Please load a file first.")
            return
        header = self.header_input.toPlainText()
        footer = self.footer_input.toPlainText()

        options = QFileDialog.Options()
        save_name, _ = QFileDialog.getSaveFileName(self, "Save Modified .gjf File", "", "Gaussian Files (*.gjf);;All Files (*)", options=options)

        if save_name:
            
            try:
                    # Write modified atom lines
                new_content = header + '\n'
                for atom in self.atom_lines:
                    new_content += (f"{atom['element']:2}  {atom['x']:.6f}  {atom['y']:.6f}  {atom['z']:.6f}\n")
                    
                new_content += footer
                with open(save_name, 'w') as file:
                    file.write(new_content)

                self.result_text.append(f"Modified file saved as: {save_name}")
            except Exception as e:
                self.result_text.append(f"Error saving file: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AtomChangerApp()
    window.show()
    sys.exit(app.exec_())
