import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpinBox,
    QDoubleSpinBox, QFormLayout, QTextEdit, QComboBox, QLabel, QFileDialog,
    QMessageBox, QStyledItemDelegate, QColorDialog
)
from PySide6.QtGui import QFontDatabase, QColor
from PySide6.QtCore import Qt, QTimer
from core.converter import parse_color
from core.threads import ConversionThread

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRT转ASS工具")
        self.setup_ui()
        self.setMinimumSize(680, 580)
        self.thread = None

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 文件夹选择
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("请选择包含SRT文件的文件夹...")
        btn_browse = QPushButton("浏览文件夹")
        btn_browse.setFixedWidth(100)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("文件夹路径:"))
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(btn_browse, alignment=Qt.AlignRight)

        # 样式参数
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(15)

        # 字体选择
        self.font_combo = QComboBox()
        self.font_combo.setEditable(False)
        delegate = QStyledItemDelegate()
        self.font_combo.setItemDelegate(delegate)
        self.font_combo.setStyleSheet("""
            QComboBox { font-family: inherit; }
            QComboBox QAbstractItemView::item { 
                font-family: inherit; 
                height: 30px; 
            }
        """)
        self.font_status_label = QLabel()
        self.font_status_label.setStyleSheet("color: #FF6666;")
        form_layout.addRow("字体名称:", self.font_combo)
        form_layout.addRow("", self.font_status_label)

        # 字号
        self.font_size = QSpinBox()
        self.font_size.setRange(1, 100)
        self.font_size.setValue(42)
        form_layout.addRow("字号:", self.font_size)

        # 间距
        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(0, 10)
        self.spacing.setValue(2.6)
        self.spacing.setSingleStep(0.1)
        form_layout.addRow("字幕间距:", self.spacing)

        # 颜色选择
        self.primary_color_edit = QLineEdit("#FFFFFF")
        self.btn_primary_color = QPushButton("选择颜色")
        self.btn_primary_color.setFixedWidth(100)
        form_layout.addRow("字幕颜色:", self.create_color_layout(self.primary_color_edit, self.btn_primary_color))

        self.border_color_edit = QLineEdit("#F58709")
        self.btn_border_color = QPushButton("选择颜色")
        self.btn_border_color.setFixedWidth(100)
        form_layout.addRow("边框颜色:", self.create_color_layout(self.border_color_edit, self.btn_border_color))

        # 边框大小
        self.border_size = QDoubleSpinBox()
        self.border_size.setRange(0, 10)
        self.border_size.setValue(2.6)
        self.border_size.setSingleStep(0.1)
        form_layout.addRow("边框大小:", self.border_size)

        # 输出路径
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("默认与输入文件夹相同")
        self.btn_output_browse = QPushButton("浏览文件夹")
        self.btn_output_browse.setFixedWidth(100)
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件夹:"))
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.btn_output_browse, alignment=Qt.AlignRight)

        # 日志显示
        self.log = QTextEdit()
        self.log.setPlaceholderText("转换日志将显示在此处...")
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas';
            }
        """)

        # 转换按钮
        self.btn_convert = QPushButton("🚀 开始转换")
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #00CCCC;
                font-size: 14pt;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #00AAAA;
            }
        """)

        # 组装界面
        layout.addLayout(folder_layout)
        layout.addLayout(form_layout)
        layout.addLayout(output_layout)
        layout.addWidget(QLabel("操作日志:"))
        layout.addWidget(self.log)
        layout.addWidget(self.btn_convert, alignment=Qt.AlignCenter)

        # 信号连接
        btn_browse.clicked.connect(self.select_folder)
        self.btn_primary_color.clicked.connect(lambda: self.choose_color(self.primary_color_edit))
        self.btn_border_color.clicked.connect(lambda: self.choose_color(self.border_color_edit))
        self.btn_output_browse.clicked.connect(self.select_output_folder)
        self.btn_convert.clicked.connect(self.start_conversion)
        self.font_combo.currentTextChanged.connect(self.check_font_availability)

        self.setLayout(layout)

        # 延迟加载字体列表
        QTimer.singleShot(100, self.load_font_list)

    def create_color_layout(self, edit, btn):
        layout = QHBoxLayout()
        layout.addWidget(edit)
        layout.addWidget(btn)
        return layout

    def load_font_list(self):
        """加载系统字体列表"""
        font_db = QFontDatabase()
        system_fonts = sorted(font_db.families())
        self.font_combo.addItems(system_fonts)
        self.font_combo.setCurrentText("FOT-SeuratCapie Pro")

    def check_font_availability(self, font_name):
        """检查字体是否可用"""
        font_db = QFontDatabase()
        available = font_db.families()
        
        if font_name in available:
            self.font_status_label.setText("")
        else:
            self.font_status_label.setText(f"⚠ 当前系统未安装 {font_name}")

    def select_folder(self):
        """选择输入文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path_edit.setText(folder)
            self.output_dir_edit.setText(folder)

    def select_output_folder(self):
        """选择输出文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_dir_edit.setText(folder)

    def choose_color(self, edit):
        """颜色选择对话框"""
        color = QColorDialog.getColor()
        if color.isValid():
            edit.setText(color.name())

    def get_style_parameters(self):
        """获取样式参数"""
        return {
            'fontname': self.font_combo.currentText(),
            'fontsize': self.font_size.value(),
            'spacing': self.spacing.value(),
            'primary_color': parse_color(self.primary_color_edit.text()),
            'border_color': parse_color(self.border_color_edit.text()),
            'border_size': self.border_size.value()
        }

    def start_conversion(self):
        """启动转换线程"""
        folder_path = self.folder_path_edit.text()
        output_dir = self.output_dir_edit.text() or folder_path

        if not os.path.isdir(folder_path):
            QMessageBox.critical(self, "错误", "输入的路径不是有效文件夹")
            return

        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建输出文件夹: {str(e)}")
            return

        style = self.get_style_parameters()
        self.thread = ConversionThread(folder_path, output_dir, style)
        self.thread.progress.connect(self.log.append)
        self.thread.error.connect(self.show_error)
        self.thread.finished.connect(self.conversion_finished)
        self.btn_convert.setEnabled(False)
        self.thread.start()

    def show_error(self, message):
        """显示错误信息"""
        QMessageBox.warning(self, "警告", message)
        self.btn_convert.setEnabled(True)

    def conversion_finished(self):
        """转换完成处理"""
        self.btn_convert.setEnabled(True)
        self.log.append("\n转换完成！")

    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()