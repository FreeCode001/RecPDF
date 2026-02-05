"""
工具函数
"""
import shapely.geometry as sg

def _is_near(rect1, rect2, distance = 20):
    """
    检查两个矩形是否靠近，如果它们之间的距离小于目标距离。
    @param rect1: 矩形1
    @param rect2: 矩形2
    @param distance: 目标距离
    @return: 是否靠近
    """
    return rect1.buffer(0.1).distance(rect2.buffer(0.1)) < distance


def _is_horizontal_near(rect1, rect2, distance = 100):
    """
    检查两个矩形是否水平靠近，如果其中一个矩形是水平线。
    @param rect1: 矩形1
    @param rect2: 矩形2
    @param distance: 目标距离
    @return: 是否水平靠近
    """
    result = False
    if abs(rect1.bounds[3] - rect1.bounds[1]) < 0.1 or abs(rect2.bounds[3] - rect2.bounds[1]) < 0.1:
        if abs(rect1.bounds[0] - rect2.bounds[0]) < 0.1 and abs(rect1.bounds[2] - rect2.bounds[2]) < 0.1:
            result = abs(rect1.bounds[3] - rect2.bounds[3]) < distance
    return result


def _union_rects(rect1, rect2):
    """
    合并两个矩形。
    @param rect1: 矩形1
    @param rect2: 矩形2
    @return: 合并后的矩形
    """
    return sg.box(*(rect1.union(rect2).bounds))

# 图形矩形合并函数
def merge_rects(rect_list, distance = 20, horizontal_distance = None):
    """
    合并列表中的矩形，如果它们之间的距离小于目标距离。
    @param rect_list: 矩形列表
    @param distance: 目标距离
    @param horizontal_distance: 水平目标距离
    @return: 合并后的矩形列表
    """
    merged = True
    while merged:
        merged = False
        new_rect_list = []
        while rect_list:
            rect = rect_list.pop(0)
            for other_rect in rect_list:
                if _is_near(rect, other_rect, distance) or (
                        horizontal_distance and _is_horizontal_near(rect, other_rect, horizontal_distance)):
                    rect = _union_rects(rect, other_rect)
                    rect_list.remove(other_rect)
                    merged = True
            new_rect_list.append(rect)
        rect_list = new_rect_list
    return rect_list

# 文本矩形吸附函数
def adsorb_rects_to_rects(source_rects, target_rects, distance=10):
    """
    当距离小于目标距离时，将一组矩形吸附到另一组矩形。
    @param source_rects: 源矩形列表
    @param target_rects: 目标矩形列表
    @param distance: 目标距离
    @return: 吸附后的源矩形列表和目标矩形列表
    """
    new_source_rects = []
    for text_area_rect in source_rects:
        adsorbed = False
        for index, rect in enumerate(target_rects):
            if _is_near(text_area_rect, rect, distance):
                rect = _union_rects(text_area_rect, rect)
                target_rects[index] = rect
                adsorbed = True
                break
        if not adsorbed:
            new_source_rects.append(text_area_rect)
    return new_source_rects, target_rects

def remove_markdown_backticks(content: str) -> str:
    """
    删除markdown中的```字符串。
    """
    if '```markdown' in content:
        content = content.replace('```markdown\n', '')
        last_backticks_pos = content.rfind('```')
        if last_backticks_pos != -1:
            content = content[:last_backticks_pos] + content[last_backticks_pos + 3:]
    return content