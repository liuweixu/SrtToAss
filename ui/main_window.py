import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QSpinBox, QDoubleSpinBox, QFormLayout, QColorDialog, QFileDialog,
    QMessageBox, QTextEdit, QComboBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFontDatabase, QColor, QFont
from PySide6.QtWidgets import QStyledItemDelegate  
from core.converter import parse_color
from core.threads import ConversionThread
import sys
from PySide6.QtCore import QTimer  

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SrtToAss")
        self.setup_ui()
        self.setMinimumSize(1020, 750)

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

        # ========= 参数布局调整部分 =========
        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(15)

        # 第一行：字体参数
        self.font_combo = QComboBox()
        delegate = QStyledItemDelegate()
        self.font_combo.setItemDelegate(delegate)
        self.font_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.font_status_label = QLabel()
        
        # 字体加载状态提示
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体名称:"))
        font_layout.addWidget(self.font_combo)
        font_layout.addWidget(self.font_status_label)
        form_layout.addRow(font_layout)

        # 第二行：字号、间距、颜色（1×3布局）
        row2_layout = QHBoxLayout()
        
        # 字号
        fontsize_layout = QVBoxLayout()
        self.font_size = QSpinBox()
        self.font_size.setRange(1, 100)
        self.font_size.setValue(20)
        fontsize_layout.addWidget(QLabel("字号"))
        fontsize_layout.addWidget(self.font_size)
        
        # 间距
        spacing_layout = QVBoxLayout()
        self.spacing = QDoubleSpinBox()
        self.spacing.setRange(0, 10)
        self.spacing.setValue(2.6)
        self.spacing.setSingleStep(0.1)
        spacing_layout.addWidget(QLabel("间距"))
        spacing_layout.addWidget(self.spacing)
        
        # 颜色
        color_layout = QVBoxLayout()
        self.primary_color_edit = QLineEdit("#FFFFFF")
        self.btn_primary_color = QPushButton("字幕颜色")
        color_sub_layout = QHBoxLayout()
        color_sub_layout.addWidget(self.primary_color_edit)
        color_sub_layout.addWidget(self.btn_primary_color)
        color_layout.addWidget(QLabel("字幕颜色"))
        color_layout.addLayout(color_sub_layout)
        
        row2_layout.addLayout(fontsize_layout)
        row2_layout.addLayout(spacing_layout)
        row2_layout.addLayout(color_layout)
        form_layout.addRow(row2_layout)

        # 第三行：边框颜色、边框大小（1×2布局）
        row3_layout = QHBoxLayout()
        
        # 边框颜色
        border_color_layout = QVBoxLayout()
        self.border_color_edit = QLineEdit("#F58709")
        self.btn_border_color = QPushButton("边框颜色")
        border_color_sub = QHBoxLayout()
        border_color_sub.addWidget(self.border_color_edit)
        border_color_sub.addWidget(self.btn_border_color)
        border_color_layout.addWidget(QLabel("边框颜色"))
        border_color_layout.addLayout(border_color_sub)
        
        # 边框大小
        border_size_layout = QVBoxLayout()
        self.border_size = QDoubleSpinBox()
        self.border_size.setRange(0, 10)
        self.border_size.setValue(2.6)
        self.border_size.setSingleStep(0.1)
        border_size_layout.addWidget(QLabel("边框大小"))
        border_size_layout.addWidget(self.border_size)
        
        row3_layout.addLayout(border_color_layout)
        row3_layout.addLayout(border_size_layout)
        form_layout.addRow(row3_layout)

        # 第四行：其他参数（粗体、斜体、缩放）
        row4_layout = QHBoxLayout()
        
        # 粗体/斜体
        style_layout = QVBoxLayout()
        self.bold_check = QCheckBox("粗体")
        self.bold_check.setChecked(True)
        self.italic_check = QCheckBox("斜体")
        style_layout.addWidget(QLabel("字体样式"))
        style_sub = QHBoxLayout()
        style_sub.addWidget(self.bold_check)
        style_sub.addWidget(self.italic_check)
        style_layout.addLayout(style_sub)
        
        # 缩放比例
        scale_layout = QVBoxLayout()
        self.scale_x = QSpinBox()
        self.scale_x.setRange(1, 500)
        self.scale_x.setValue(100)
        self.scale_y = QSpinBox()
        self.scale_y.setRange(1, 500)
        self.scale_y.setValue(100)
        scale_sub = QHBoxLayout()
        scale_sub.addWidget(QLabel("横向"))
        scale_sub.addWidget(self.scale_x)
        scale_sub.addWidget(QLabel("纵向"))
        scale_sub.addWidget(self.scale_y)
        scale_layout.addWidget(QLabel("缩放比例 (%)"))
        scale_layout.addLayout(scale_sub)
        
        row4_layout.addLayout(style_layout)
        row4_layout.addLayout(scale_layout)
        form_layout.addRow(row4_layout)

        # 第五行：边距设置
        margin_layout = QHBoxLayout()
        self.margin_l = QSpinBox()
        self.margin_l.setRange(0, 500)
        self.margin_l.setValue(10)
        self.margin_r = QSpinBox()
        self.margin_r.setRange(0, 500)
        self.margin_r.setValue(10)
        self.margin_v = QSpinBox()
        self.margin_v.setRange(0, 500)
        self.margin_v.setValue(20)
        margin_layout.addWidget(QLabel("左边距:"))
        margin_layout.addWidget(self.margin_l)
        margin_layout.addWidget(QLabel("右边距:"))
        margin_layout.addWidget(self.margin_r)
        margin_layout.addWidget(QLabel("垂直边距:"))
        margin_layout.addWidget(self.margin_v)
        form_layout.addRow("边距设置:", margin_layout)

        # 对齐方式和编码
        self.alignment = QComboBox()
        self.alignment.addItems(["左下", "下方居中", "右下"])
        self.alignment.setCurrentIndex(1)
        self.encoding = QComboBox()
        self.encoding.addItems(["ANSI (0)", "Unicode (1)"])
        self.encoding.setCurrentIndex(1)
        
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(QLabel("对齐方式:"))
        advanced_layout.addWidget(self.alignment)
        advanced_layout.addWidget(QLabel("编码:"))
        advanced_layout.addWidget(self.encoding)
        form_layout.addRow("高级设置:", advanced_layout)

        # 输出选项
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
                padding: 10px;
                font-family: 'Consolas';
            }
        """)

        # 控制按钮
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

        # 组装布局
        layout.addLayout(folder_layout)
        layout.addLayout(form_layout)
        layout.addLayout(output_layout)
        layout.addWidget(QLabel("操作日志:"))
        layout.addWidget(self.log)
        layout.addWidget(self.btn_convert, alignment=Qt.AlignCenter)

        # 连接信号
        btn_browse.clicked.connect(self.select_folder)
        self.btn_primary_color.clicked.connect(lambda: self.choose_color(self.primary_color_edit))
        self.btn_border_color.clicked.connect(lambda: self.choose_color(self.border_color_edit))
        self.btn_output_browse.clicked.connect(self.select_output_folder)
        self.btn_convert.clicked.connect(self.start_conversion)

        self.setLayout(layout)
        self.thread = None

        # 延迟加载字体列表
        QTimer.singleShot(100, self.load_font_list)

    def get_style_parameters(self):
        return {
            'fontname': self.font_combo.currentText(),
            'fontsize': self.font_size.value(),
            'spacing': self.spacing.value(),
            'primary_color': parse_color(self.primary_color_edit.text()),
            'border_color': parse_color(self.border_color_edit.text()),
            'border_size': self.border_size.value(),
            'bold': self.bold_check.isChecked(),
            'italic': self.italic_check.isChecked(),
            'scale_x': self.scale_x.value(),
            'scale_y': self.scale_y.value(),
            'margin_l': self.margin_l.value(),
            'margin_r': self.margin_r.value(),
            'margin_v': self.margin_v.value(),
            'alignment': 2,  # 固定为居中
            'encoding': 1      # 固定为Unicode
        }

    def load_font_list(self):
        """延迟加载字体列表以加快启动速度"""
        font_db = QFontDatabase()
        system_fonts = sorted(font_db.families())  # 直接获取已排序的字体名称列表
        self.font_combo.addItems(system_fonts)
        self.font_combo.addItems(system_fonts)

    def create_color_layout(self, edit, btn):
        layout = QHBoxLayout()
        layout.addWidget(edit)
        layout.addWidget(btn)
        return layout

    def check_font_availability(self, font_name):
        """检查选择的字体是否可用"""
        font_db = QFontDatabase()
        available = font_db.families()  # 直接获取字体名称列表
        
        if font_name in available:
            self.font_status_label.setText("")
        else:
            self.font_status_label.setText(f"⚠ 当前系统未安装 {font_name}")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path_edit.setText(folder)
            self.output_dir_edit.setText(folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_dir_edit.setText(folder)

    def choose_color(self, edit):
        color = QColorDialog.getColor()
        if color.isValid():
            edit.setText(color.name())

    def start_conversion(self):
        folder_path = self.folder_path_edit.text()
        output_dir = self.output_dir_edit.text()

        if not os.path.isdir(folder_path):
            QMessageBox.critical(self, "错误", "输入的路径不是有效文件夹")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建输出文件夹: {str(e)}")
                return

        style = self.get_style_parameters()
        self.thread = ConversionThread(folder_path, output_dir, style)
        self.thread.progress.connect(self.log.append)
        self.thread.error.connect(lambda msg: QMessageBox.warning(self, "警告", msg))
        self.thread.finished.connect(lambda: self.btn_convert.setEnabled(True))
        self.btn_convert.setEnabled(False)
        self.thread.start()

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()