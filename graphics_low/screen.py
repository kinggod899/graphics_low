"""设置-画面 页面的 1080p 坐标常量。

这里的坐标全部是 1080p 基准下的实机测量值。框架在截图时会把任意 16:9 分辨率的
画面拉伸到 1920x1080 再识别，点击时又按实际窗口尺寸换算回去，所以只需要维护一套
1080p 坐标，2K / 4K 无需单独适配。
"""

from one_dragon.base.geometry.point import Point
from one_dragon.base.geometry.rectangle import Rect


class GraphicsRow:
    """「画面」页签里的一行下拉选项。

    一行 = 一个标签 + 一个当前值 + 展开后的一列候选项。
    """

    def __init__(
        self,
        config_key: str,
        label: str,
        row_cy: int,
        options: tuple[str, ...],
    ) -> None:
        self.config_key: str = config_key
        self.label: str = label
        self.row_cy: int = row_cy
        self.options: tuple[str, ...] = options

    def option_index(self, option: str) -> int:
        """返回选项在游戏下拉框里的下标，未知选项返回 -1。"""
        try:
            return self.options.index(option)
        except ValueError:
            return -1

    def value_point(self) -> Point:
        """当前值区域的点击点，点这里会展开下拉框。"""
        return Point(VALUE_CENTER_X, self.row_cy)

    def value_rect(self) -> Rect:
        """读取当前值的 OCR 区域。"""
        return Rect(VALUE_LEFT, self.row_cy - VALUE_HALF_HEIGHT,
                    VALUE_RIGHT, self.row_cy + VALUE_HALF_HEIGHT)

    def dropdown_point(self, option: str) -> Point | None:
        """展开后某个候选项的点击点，未知选项返回 None。"""
        idx = self.option_index(option)
        if idx < 0:
            return None
        return Point(DROPDOWN_ITEM_X, self.row_cy + DROPDOWN_OFFSET_Y + DROPDOWN_ROW_HEIGHT * idx)


# 大世界画面与暂停菜单入口
WORLD_SCREEN_NAME: str = '大世界-普通'
WORLD_MENU_BUTTON_AREA: str = '按钮-菜单'
# 暂停菜单底部 tab 条，实机里「设置」就在这条带上
PAUSE_BOTTOM_BAR: Rect = Rect(200, 924, 1728, 1058)
PAUSE_MENU_KEYWORD: str = '设置'

# 设置界面的左侧页签列与右侧标签列
TAB_COLUMN: Rect = Rect(160, 170, 260, 700)
RENDER_TAB_KEYWORD: str = '画面'
LABEL_COLUMN: Rect = Rect(400, 180, 800, 990)
RENDER_PANEL_KEYWORD: str = '渲染精度'

# 左侧页签列最下面的「其他」页签。实测选中态药丸 69~343 × 574~645，取正中点。
# 这里不用 OCR：选中态是深色文字压在亮色药丸上，OCR 不稳，而页签位置是固定的。
OTHER_TAB_POINT: Point = Point(206, 610)
# 切到「其他」页后右侧第一屏就会出现这一行，拿它确认页签切过去了
OTHER_PANEL_KEYWORD: str = '字体选项'

# 设置界面公共点击点
BACK_POINT: Point = Point(70, 36)
BLANK_POINT: Point = Point(900, 160)

# 当前值区域与下拉面板几何（实测公式：条目 y = 行中心 + 76 + 67 * 下标）
VALUE_CENTER_X: int = 1474
VALUE_LEFT: int = 1430
VALUE_RIGHT: int = 1800
VALUE_HALF_HEIGHT: int = 26
DROPDOWN_ITEM_X: int = 1617
DROPDOWN_OFFSET_Y: int = 76
DROPDOWN_ROW_HEIGHT: int = 67

# 各步骤的等待时间（秒），按实机响应速度定的
MENU_WAIT: float = 2.5
DROPDOWN_OPEN_WAIT: float = 1.4
DROPDOWN_PICK_WAIT: float = 1.6
DROPDOWN_CLOSE_WAIT: float = 0.9
BACK_WAIT: float = 1.2

FPS_ROW: GraphicsRow = GraphicsRow('target_fps', '帧率', 444, ('30', '60', '无限制'))
RENDER_SCALE_ROW: GraphicsRow = GraphicsRow('target_render_scale', '渲染精度', 610, ('0.8', '1.0', '1.2'))
ANTIALIAS_ROW: GraphicsRow = GraphicsRow('target_antialias', '抗锯齿', 693, ('关闭', 'TAA', 'SMAA'))

# 「其他」页里的字体选项。行距同样是 83，「字体选项」是第 4 行，所以行中心 479；
# 展开后的下拉面板几何和「画面」页一致，选项同样是 行中心 + 76 + 67 * 下标。
FONT_ROW: GraphicsRow = GraphicsRow(
    'target_font', '字体选项', 479, ('推荐方案', '全局粗体', '全局细体'),
)

# 只有「画面」页的这三行会进快照，字体不在快照里，所以 FONT_ROW 不放进 ROWS
ROWS: tuple[GraphicsRow, ...] = (FPS_ROW, RENDER_SCALE_ROW, ANTIALIAS_ROW)
