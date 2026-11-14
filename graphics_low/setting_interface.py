"""降低画质插件的设置页。

三项目标档位都用下拉框，选项文字必须和游戏里下拉框的文字完全一致，
否则应用运行时会判定「目标值不在可选项里」直接失败。
底部显示第一次运行时记下的原始档位，可以清空让它下次重新记录。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, FluentIcon, PushSettingCard

from one_dragon.base.config.config_item import ConfigItem
from one_dragon.utils.log_utils import log
from one_dragon_qt.services.app_setting.app_setting_provider import GroupIdMixin
from one_dragon_qt.utils.config_utils import get_prop_adapter
from one_dragon_qt.widgets.setting_card.combo_box_setting_card import (
    ComboBoxSettingCard,
)
from one_dragon_qt.widgets.vertical_scroll_interface import VerticalScrollInterface

from . import const
from .config import GraphicsLowConfig
from .graphics_low_snapshot import GraphicsLowSnapshotConfig

if TYPE_CHECKING:
    from one_dragon.base.operation.one_dragon_context import OneDragonContext


# 下拉选项必须和游戏内文字一一对应
FPS_OPTIONS: list[ConfigItem] = [
    ConfigItem('30 帧', '30'),
    ConfigItem('60 帧', '60'),
    ConfigItem('无限制', '无限制'),
]
RENDER_SCALE_OPTIONS: list[ConfigItem] = [
    ConfigItem('0.8', '0.8'),
    ConfigItem('1.0', '1.0'),
    ConfigItem('1.2', '1.2'),
]
ANTIALIAS_OPTIONS: list[ConfigItem] = [
    ConfigItem('关闭', '关闭'),
    ConfigItem('TAA', 'TAA'),
    ConfigItem('SMAA', 'SMAA'),
]
FONT_OPTIONS: list[ConfigItem] = [
    ConfigItem('推荐方案', '推荐方案'),
    ConfigItem('全局粗体', '全局粗体'),
    ConfigItem('全局细体', '全局细体'),
]


class GraphicsLowSettingInterface(VerticalScrollInterface, GroupIdMixin):
    """降低画质的独立设置页。"""

    def __init__(self, ctx: OneDragonContext, parent: QWidget | None = None) -> None:
        super().__init__(
            content_widget=None,
            object_name='graphics_low_setting_interface',
            nav_text_cn='降低游戏画质',
            parent=parent,
        )
        self.ctx: OneDragonContext = ctx
        self.config: GraphicsLowConfig | None = None
        self.snapshot: GraphicsLowSnapshotConfig | None = None
        self.fps_opt: ComboBoxSettingCard | None = None
        self.render_scale_opt: ComboBoxSettingCard | None = None
        self.antialias_opt: ComboBoxSettingCard | None = None
        self.font_opt: ComboBoxSettingCard | None = None
        self.snapshot_opt: PushSettingCard | None = None

    def get_content_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        intro = CaptionLabel(
            '一条龙每次运行都会把游戏「设置 → 画面」里的帧率、渲染精度、抗锯齿，'
            '以及「设置 → 其他」里的字体选项调成下面的档位，'
            '运行结束时由「恢复游戏画质」还原。',
            widget,
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.fps_opt = ComboBoxSettingCard(
            icon=FluentIcon.SPEED_HIGH,
            title='目标帧率',
            content='降低画质时把帧率改成这一档',
            options_list=FPS_OPTIONS,
        )
        layout.addWidget(self.fps_opt)

        self.render_scale_opt = ComboBoxSettingCard(
            icon=FluentIcon.ZOOM,
            title='目标渲染精度',
            content='降低画质时把渲染精度改成这一档',
            options_list=RENDER_SCALE_OPTIONS,
        )
        layout.addWidget(self.render_scale_opt)

        self.antialias_opt = ComboBoxSettingCard(
            icon=FluentIcon.BRUSH,
            title='目标抗锯齿',
            content='降低画质时把抗锯齿改成这一档',
            options_list=ANTIALIAS_OPTIONS,
        )
        layout.addWidget(self.antialias_opt)

        self.font_opt = ComboBoxSettingCard(
            icon=FluentIcon.FONT,
            title='目标字体',
            content='降低画质时把「其他」页的字体选项改成这一档',
            options_list=FONT_OPTIONS,
        )
        layout.addWidget(self.font_opt)

        self.snapshot_opt = PushSettingCard(
            icon=FluentIcon.HISTORY,
            title='原始档位记录',
            content='尚未记录',
            text='清空记录',
        )
        self.snapshot_opt.setFixedHeight(50)
        self.snapshot_opt.clicked.connect(self._on_clear_snapshot_clicked)
        layout.addWidget(self.snapshot_opt)

        layout.addStretch(1)
        return widget

    def on_interface_shown(self) -> None:
        super().on_interface_shown()

        self.config = self.ctx.run_context.get_config(
            app_id=const.APP_ID,
            instance_idx=self.ctx.current_instance_idx,
            group_id=self.group_id,
        )
        self.fps_opt.init_with_adapter(get_prop_adapter(self.config, 'target_fps'))
        self.render_scale_opt.init_with_adapter(
            get_prop_adapter(self.config, 'target_render_scale')
        )
        self.antialias_opt.init_with_adapter(
            get_prop_adapter(self.config, 'target_antialias')
        )
        self.font_opt.init_with_adapter(get_prop_adapter(self.config, 'target_font'))
        # 快照全局一份，所有实例共用，存在插件数据目录里
        self.snapshot = GraphicsLowSnapshotConfig(
            data_dir=self.ctx.get_plugin_data_dir(const.APP_ID),
        )
        self._update_snapshot_display()

    def _update_snapshot_display(self) -> None:
        """刷新原始档位卡片的副标题。"""
        if self.snapshot is None or self.snapshot_opt is None:
            return
        if self.snapshot.original_fps == '':
            self.snapshot_opt.setContent(
                '还没记录，第一次运行成功后会把当时的档位存下来（全局一份，所有账号共用）'
            )
            return
        self.snapshot_opt.setContent(
            f'帧率 {self.snapshot.original_fps} / 渲染精度 '
            f'{self.snapshot.original_render_scale} / 抗锯齿 '
            f'{self.snapshot.original_antialias} / 字体 {self.snapshot.original_font or "未记录"}'
            f'（{self.snapshot.snapshot_date} 记录）'
        )

    def _on_clear_snapshot_clicked(self) -> None:
        """清空原始档位，下次运行重新记录。"""
        if self.snapshot is None:
            return
        self.snapshot.clear()
        log.info('已清空原始档位记录，下次运行会重新记录')
        self._update_snapshot_display()
