import re
from datetime import datetime

COLOR_MAP = {
    'white': '&H00FFFFFF',
    'black': 'H00000000',
    'red': '&H000000FF',
    'green': '&H0000FF00',
    'blue': '&H00FF0000',
    'yellow': '&H0000FFFF',
    'orange': '&H000087F5'
}

# 核心转换函数
def srt_time_to_ass(time_str):
    dt = datetime.strptime(time_str, '%H:%M:%S,%f')
    return dt.strftime('%H:%M:%S.%f')[:-4]

def parse_color(input_color):
    input_color = input_color.strip().lower()
    
    if input_color in COLOR_MAP:
        return COLOR_MAP[input_color]
    
    if input_color.startswith('#'):
        hex_str = input_color[1:]
        if len(hex_str) == 6:
            return f"&H00{hex_str[4:6]}{hex_str[2:4]}{hex_str[0:2]}".upper()
        elif len(hex_str) == 8:
            return f"&H{hex_str[6:8]}{hex_str[4:6]}{hex_str[2:4]}{hex_str[0:2]}".upper()
    
    return '&H00FFFFFF'

def generate_ass_header(style):
    return (
        f"[Script Info]\n"
        f"ScriptType: v4.00+\n"
        f"PlayResX: 384\n"
        f"PlayResY: 288\n"
        f"\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        f"Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        f"Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{style['fontname']},{style['fontsize']},"
        f"{style['primary_color']},&H00000000,{style['border_color']},&H00000000,"
        f"{'-1' if style['bold'] else '0'},"
        f"{'-1' if style['italic'] else '0'},0,0,"
        f"{style['scale_x']},{style['scale_y']},"
        f"{style['spacing']},0,1,{style['border_size']},0,"
        f"{style['alignment']},"
        f"{style['margin_l']},{style['margin_r']},{style['margin_v']},"
        f"{style['encoding']}\n"
        f"\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

def convert_srt_to_ass(srt_path, ass_path, style):
    with open(srt_path, 'r', encoding='utf-8-sig') as f:
        srt_content = f.read()

    blocks = re.split(r'\n{2,}', srt_content.strip())
    ass_events = []
    
    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        
        timecode = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
        if not timecode:
            continue
            
        start = srt_time_to_ass(timecode.group(1))
        end = srt_time_to_ass(timecode.group(2))
        text = '\\N'.join(lines[2:]).strip()
        
        ass_events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(generate_ass_header(style))
        f.write('\n'.join(ass_events))