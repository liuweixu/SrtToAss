"""
字幕转换核心模块
"""
from .converter import (
    parse_color,
    generate_ass_header,
    convert_srt_to_ass
)
from .threads import ConversionThread

__all__ = [
    'parse_color',
    'generate_ass_header',
    'convert_srt_to_ass',
    'ConversionThread'
]