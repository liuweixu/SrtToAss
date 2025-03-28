from PySide6.QtCore import QThread, Signal
import os
from core.converter import convert_srt_to_ass

class ConversionThread(QThread):
    progress = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, folder_path, output_dir, style):
        super().__init__()
        self.folder_path = folder_path
        self.output_dir = output_dir
        self.style = style
        self.running = True


    def run(self):
        srt_files = [
            f for f in os.listdir(self.folder_path)
            if os.path.splitext(f)[1].lower() == '.srt'
            and os.path.isfile(os.path.join(self.folder_path, f))
        ]

        if not srt_files:
            self.error.emit("未找到任何SRT字幕文件")
            return

        total = len(srt_files)
        for idx, filename in enumerate(srt_files):
            if not self.running:
                break
            srt_path = os.path.join(self.folder_path, filename)
            ass_filename = os.path.splitext(filename)[0] + '.ass'
            ass_path = os.path.join(self.output_dir, ass_filename)
            
            # 在转换前检查文件是否存在
            file_exists = os.path.exists(ass_path)
            
            try:
                convert_srt_to_ass(srt_path, ass_path, self.style)
                # 根据转换前的检查结果显示不同日志
                if file_exists:
                    self.progress.emit(f"已覆盖：{ass_filename}")
                else:
                    self.progress.emit(f"已创建：{ass_filename}")
            except Exception as e:
                self.error.emit(f"转换失败：{filename} - {str(e)}")
        
        self.finished.emit()

    def stop(self):
        self.running = False