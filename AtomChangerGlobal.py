import sys
import copy
import re
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QTextEdit, QVBoxLayout,
                             QLabel, QFileDialog, QLineEdit, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt

class AtomChangerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atom Coordinates Changer")
        self.setGeometry(200, 200, 950, 750)

        # GUI elements
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # 语言选择
        self.language_selector = QComboBox()
        self.language_selector.addItem("English")
        self.language_selector.addItem("日本語")
        self.language_selector.addItem("中文")
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.layout.addWidget(self.language_selector)

        # 原子编号范围输入
        self.range_label = QLabel("Enter atom number range (e.g., 1-5, 10-15):")
        self.layout.addWidget(self.range_label)
        self.range_input = QLineEdit(self)
        self.layout.addWidget(self.range_input)

        # 第一组调整值输入
        self.x_value_label = QLabel("Enter first adjustment X value (in Angstrom):")
        self.layout.addWidget(self.x_value_label)
        self.x_value_input = QLineEdit(self)
        self.layout.addWidget(self.x_value_input)

        self.y_value_label = QLabel("Enter first adjustment Y value (in Angstrom):")
        self.layout.addWidget(self.y_value_label)
        self.y_value_input = QLineEdit(self)
        self.layout.addWidget(self.y_value_input)

        self.z_value_label = QLabel("Enter first adjustment Z value (in Angstrom):")
        self.layout.addWidget(self.z_value_label)
        self.z_value_input = QLineEdit(self)
        self.layout.addWidget(self.z_value_input)

        # 第一组文件后缀
        self.suffix_label = QLabel("Enter first adjustment file suffix (default 'modified'):")
        self.layout.addWidget(self.suffix_label)
        self.suffix_input = QLineEdit(self)
        self.suffix_input.setText("modified")
        self.layout.addWidget(self.suffix_input)

        # 第一组调整次数
        self.iteration_label = QLabel("Enter number of first adjustments:")
        self.layout.addWidget(self.iteration_label)
        self.iteration_input = QLineEdit(self)
        self.layout.addWidget(self.iteration_input)

        # 二次调整选项
        self.double_adjust_checkbox = QCheckBox("Double Adjustment")
        self.double_adjust_checkbox.stateChanged.connect(self.toggle_double_adjust)
        self.layout.addWidget(self.double_adjust_checkbox)

        # 二次调整的控件（默认隐藏）
        self.second_adjust_widget = QWidget()
        self.second_adjust_layout = QVBoxLayout(self.second_adjust_widget)

        self.x2_value_label = QLabel("Enter second adjustment X value (in Angstrom):")
        self.second_adjust_layout.addWidget(self.x2_value_label)
        self.x2_value_input = QLineEdit(self)
        self.second_adjust_layout.addWidget(self.x2_value_input)

        self.y2_value_label = QLabel("Enter second adjustment Y value (in Angstrom):")
        self.second_adjust_layout.addWidget(self.y2_value_label)
        self.y2_value_input = QLineEdit(self)
        self.second_adjust_layout.addWidget(self.y2_value_input)

        self.z2_value_label = QLabel("Enter second adjustment Z value (in Angstrom):")
        self.second_adjust_layout.addWidget(self.z2_value_label)
        self.z2_value_input = QLineEdit(self)
        self.second_adjust_layout.addWidget(self.z2_value_input)

        self.suffix2_label = QLabel("Enter second adjustment file suffix (default 'modified2'):")
        self.second_adjust_layout.addWidget(self.suffix2_label)
        self.suffix2_input = QLineEdit(self)
        self.suffix2_input.setText("modified2")
        self.second_adjust_layout.addWidget(self.suffix2_input)

        self.iteration2_label = QLabel("Enter number of second adjustments:")
        self.second_adjust_layout.addWidget(self.iteration2_label)
        self.iteration2_input = QLineEdit(self)
        self.second_adjust_layout.addWidget(self.iteration2_input)

        self.second_adjust_widget.setVisible(False)
        self.layout.addWidget(self.second_adjust_widget)

        # 显示原子坐标
        self.coord_text = QTextEdit(self)
        self.coord_text.setReadOnly(True)
        self.layout.addWidget(self.coord_text)

        # 显示结果信息
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        # 自定义文件头与文件尾输入
        self.header_input = QTextEdit()
        self.header_input.setPlaceholderText("Enter custom file header here...")
        self.layout.addWidget(QLabel("File Header"))
        self.layout.addWidget(self.header_input)

        self.footer_input = QTextEdit()
        self.footer_input.setPlaceholderText("Enter custom file footer here...")
        self.layout.addWidget(QLabel("File Footer"))
        self.layout.addWidget(self.footer_input)

        # 加载文件按钮
        self.load_file_button = QPushButton("Load .gjf File")
        self.load_file_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_file_button)

        # 修改坐标并保存多个文件按钮
        self.modify_button = QPushButton("Modify and Save Files")
        self.modify_button.clicked.connect(self.modify_and_save_files)
        self.layout.addWidget(self.modify_button)

        self.setCentralWidget(self.central_widget)

        # Variables to store data
        self.file_name = None
        self.line_data = []  # 文件行数据（包含原子行和非原子行）
        self.atom_lines_original = []  # 原始原子坐标

        # 初始语言设置
        self.language = 'en'
        self.update_ui_text()

    def toggle_double_adjust(self, state):
        self.second_adjust_widget.setVisible(state == Qt.Checked)

    def change_language(self):
        if self.language_selector.currentIndex() == 0:
            self.language = 'en'
        elif self.language_selector.currentIndex() == 1:
            self.language = 'ja'
        else:
            self.language = 'zh'
        self.update_ui_text()

    def update_ui_text(self):
        if self.language == 'en':
            self.range_label.setText("Enter atom number range (e.g., 1-5, 10-15):")
            self.x_value_label.setText("Enter first adjustment X value (in Angstrom):")
            self.y_value_label.setText("Enter first adjustment Y value (in Angstrom):")
            self.z_value_label.setText("Enter first adjustment Z value (in Angstrom):")
            self.suffix_label.setText("Enter first adjustment file suffix (default 'modified'):")
            self.iteration_label.setText("Enter number of first adjustments:")
            self.double_adjust_checkbox.setText("Double Adjustment")
            self.x2_value_label.setText("Enter second adjustment X value (in Angstrom):")
            self.y2_value_label.setText("Enter second adjustment Y value (in Angstrom):")
            self.z2_value_label.setText("Enter second adjustment Z value (in Angstrom):")
            self.suffix2_label.setText("Enter second adjustment file suffix (default 'modified2'):")
            self.iteration2_label.setText("Enter number of second adjustments:")
            self.load_file_button.setText("Load .gjf File")
            self.modify_button.setText("Modify and Save Files")
            self.header_input.setPlaceholderText("Enter custom file header here...")
            self.footer_input.setPlaceholderText("Enter custom file footer here...")
        elif self.language == 'ja':
            self.range_label.setText("原子番号範囲を入力してください（例：1-5, 10-15）:")
            self.x_value_label.setText("第一の調整 X 値を入力してください（単位：Å）:")
            self.y_value_label.setText("第一の調整 Y 値を入力してください（単位：Å）:")
            self.z_value_label.setText("第一の調整 Z 値を入力してください（単位：Å）:")
            self.suffix_label.setText("第一の調整ファイルサフィックスを入力してください (例: 'modified'):")
            self.iteration_label.setText("第一の調整回数を入力してください:")
            self.double_adjust_checkbox.setText("二次調整")
            self.x2_value_label.setText("第二の調整 X 値を入力してください（単位：Å）:")
            self.y2_value_label.setText("第二の調整 Y 値を入力してください（単位：Å）:")
            self.z2_value_label.setText("第二の調整 Z 値を入力してください（単位：Å）:")
            self.suffix2_label.setText("第二の調整ファイルサフィックスを入力してください (例: 'modified2'):")
            self.iteration2_label.setText("第二の調整回数を入力してください:")
            self.load_file_button.setText("ファイルを読み込む")
            self.modify_button.setText("座標を変更して保存")
            self.header_input.setPlaceholderText("カスタムファイルヘッダーをここに入力...")
            self.footer_input.setPlaceholderText("カスタムファイルフッターをここに入力...")
        else:  # 中文
            self.range_label.setText("请输入原子编号范围（例如：1-5, 10-15）：")
            self.x_value_label.setText("请输入第一组调整 X 坐标值（单位：Å）：")
            self.y_value_label.setText("请输入第一组调整 Y 坐标值（单位：Å）：")
            self.z_value_label.setText("请输入第一组调整 Z 坐标值（单位：Å）：")
            self.suffix_label.setText("请输入第一组文件后缀（默认 'modified'）：")
            self.iteration_label.setText("请输入第一组调整次数：")
            self.double_adjust_checkbox.setText("二次调整")
            self.x2_value_label.setText("请输入第二组调整 X 坐标值（单位：Å）：")
            self.y2_value_label.setText("请输入第二组调整 Y 坐标值（单位：Å）：")
            self.z2_value_label.setText("请输入第二组调整 Z 坐标值（单位：Å）：")
            self.suffix2_label.setText("请输入第二组文件后缀（默认 'modified2'）：")
            self.iteration2_label.setText("请输入第二组调整次数：")
            self.load_file_button.setText("加载 .gjf 文件")
            self.modify_button.setText("修改坐标并保存文件")
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
            self.line_data = lines
            atoms = []
            # 解析原子行，匹配元素及3个坐标
            for line in lines:
                match = re.match(r"^\s*(\w+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)", line)
                if match:
                    element, x, y, z = match.groups()
                    atoms.append({
                        'line': line,
                        'element': element,
                        'x': float(x),
                        'y': float(y),
                        'z': float(z)
                    })
            self.atom_lines_original = atoms  # 原始数据
            self.display_coordinates(atoms)
        except Exception as e:
            self.result_text.append(f"Error reading file: {str(e)}")

    def display_coordinates(self, atoms):
        self.coord_text.clear()
        for idx, atom in enumerate(atoms):
            self.coord_text.append(f"Atom {idx + 1}: {atom['element']} ({atom['x']:.6f}, {atom['y']:.6f}, {atom['z']:.6f})")

    def parse_atom_range(self, range_input):
        selected_atoms = []
        try:
            parts = range_input.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected_atoms.extend(range(start - 1, end))
                elif part != "":
                    selected_atoms.append(int(part) - 1)
        except ValueError:
            self.result_text.append("Invalid atom number range format.")
            return []
        return selected_atoms

    def modify_and_save_files(self):
        if not self.file_name:
            self.result_text.append("Please load a file first.")
            return

        # 解析原子范围
        range_input = self.range_input.text().strip()
        selected_atoms = self.parse_atom_range(range_input)
        if not selected_atoms:
            self.result_text.append(f"Invalid atom number range: {range_input}")
            return

        # 解析第一组调整值
        try:
            delta_x = float(self.x_value_input.text().strip()) if self.x_value_input.text().strip() else 0.0
            delta_y = float(self.y_value_input.text().strip()) if self.y_value_input.text().strip() else 0.0
            delta_z = float(self.z_value_input.text().strip()) if self.z_value_input.text().strip() else 0.0
        except ValueError:
            self.result_text.append("Invalid first adjustment coordinate values.")
            return

        suffix1 = self.suffix_input.text().strip() or "modified"

        try:
            first_iter = int(self.iteration_input.text().strip())
            if first_iter < 0:
                self.result_text.append("Number of first adjustments must be non-negative.")
                return
        except ValueError:
            self.result_text.append("Invalid number of first adjustments.")
            return

        # 保存第一组调整的各状态：包括原始状态作为第0次调整
        first_states = []
        # 原始状态（第0次调整）
        orig_state = [copy.deepcopy(atom) for atom in self.atom_lines_original]
        first_states.append(orig_state)
        
        # 选择保存目录
        save_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Files")
        if not save_dir:
            self.result_text.append("No directory selected.")
            return

        header = self.header_input.toPlainText()
        footer = self.footer_input.toPlainText()
        base_name = os.path.splitext(os.path.basename(self.file_name))[0]

        # 保存原文件作为第一组调整的第0次调整，文件名格式：[原文件名]_[第一组后缀]_0.gjf
        content0 = ""
        if header:
            content0 += header + "\n"
        for atom in orig_state:
            content0 += f"{atom['element']:2}  {atom['x']:.6f}  {atom['y']:.6f}  {atom['z']:.6f}\n"
        if footer:
            content0 += footer
        save_path = os.path.join(save_dir, f"{base_name}_{suffix1}_0.gjf")
        try:
            with open(save_path, 'w') as file:
                file.write(content0)
            self.result_text.append(f"Saved file: {save_path}")
        except Exception as e:
            self.result_text.append(f"Error saving file {save_path}: {str(e)}")

        # 第一组调整迭代
        current_state = copy.deepcopy(orig_state)
        for i in range(1, first_iter + 1):
            for idx in selected_atoms:
                if idx < len(current_state):
                    current_state[idx]['x'] += delta_x
                    current_state[idx]['y'] += delta_y
                    current_state[idx]['z'] += delta_z
            first_states.append(copy.deepcopy(current_state))
            content = ""
            if header:
                content += header + "\n"
            for atom in current_state:
                content += f"{atom['element']:2}  {atom['x']:.6f}  {atom['y']:.6f}  {atom['z']:.6f}\n"
            if footer:
                content += footer
            save_path = os.path.join(save_dir, f"{base_name}_{suffix1}_{i}.gjf")
            try:
                with open(save_path, 'w') as file:
                    file.write(content)
                self.result_text.append(f"Saved file: {save_path}")
            except Exception as e:
                self.result_text.append(f"Error saving file {save_path}: {str(e)}")

        # 如果启用二次调整
        if self.double_adjust_checkbox.isChecked():
            try:
                delta2_x = float(self.x2_value_input.text().strip()) if self.x2_value_input.text().strip() else 0.0
                delta2_y = float(self.y2_value_input.text().strip()) if self.y2_value_input.text().strip() else 0.0
                delta2_z = float(self.z2_value_input.text().strip()) if self.z2_value_input.text().strip() else 0.0
            except ValueError:
                self.result_text.append("Invalid second adjustment coordinate values.")
                return
            suffix2 = self.suffix2_input.text().strip() or "modified2"
            try:
                second_iter = int(self.iteration2_input.text().strip())
                if second_iter < 0:
                    self.result_text.append("Number of second adjustments must be non-negative.")
                    return
            except ValueError:
                self.result_text.append("Invalid number of second adjustments.")
                return

            # 对于每个第一组调整状态（索引 j，从 0 到 first_iter），进行第二组调整
            for j, state in enumerate(first_states):
                # 保存第二组调整的第0次调整（即未做第二次调整），文件名格式：[原文件名]_[第二组后缀]_0_[j].gjf
                content2_0 = ""
                if header:
                    content2_0 += header + "\n"
                for atom in state:
                    content2_0 += f"{atom['element']:2}  {atom['x']:.6f}  {atom['y']:.6f}  {atom['z']:.6f}\n"
                if footer:
                    content2_0 += footer
                save_path = os.path.join(save_dir, f"{base_name}_{suffix2}_0_{j}.gjf")
                try:
                    with open(save_path, 'w') as file:
                        file.write(content2_0)
                    self.result_text.append(f"Saved file: {save_path}")
                except Exception as e:
                    self.result_text.append(f"Error saving file {save_path}: {str(e)}")
                
                # 累计第二组调整
                second_state = copy.deepcopy(state)
                for k in range(1, second_iter + 1):
                    for idx in selected_atoms:
                        if idx < len(second_state):
                            second_state[idx]['x'] += delta2_x
                            second_state[idx]['y'] += delta2_y
                            second_state[idx]['z'] += delta2_z
                    content2 = ""
                    if header:
                        content2 += header + "\n"
                    for atom in second_state:
                        content2 += f"{atom['element']:2}  {atom['x']:.6f}  {atom['y']:.6f}  {atom['z']:.6f}\n"
                    if footer:
                        content2 += footer
                    save_path = os.path.join(save_dir, f"{base_name}_{suffix2}_{k}_{suffix1}_{j}.gjf")
                    try:
                        with open(save_path, 'w') as file:
                            file.write(content2)
                        self.result_text.append(f"Saved file: {save_path}")
                    except Exception as e:
                        self.result_text.append(f"Error saving file {save_path}: {str(e)}")

        self.result_text.append("All adjustments completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AtomChangerApp()
    window.show()
    sys.exit(app.exec_())
