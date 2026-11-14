"""原始画质快照。

快照必须全局只有一份：plugin_data/graphics_low/graphics_low_snapshot.yml（不带实例目录）。
原因是一条龙会按账号顺序跑多个实例，如果每个实例各存一份快照，
第二个实例跑降画质时自己的快照是空的，就会把已经调低的档位当成
「原始档位」记下来，之后恢复画质恢复的是低画质。

游戏客户端本身也只有一套全局画质设置，所以全局一份与实际情况一致。

旧版本写在 config/graphics_low_snapshot.yml，首次打开新文件时迁过来，旧文件保留不删。
"""

from __future__ import annotations

from pathlib import Path

from one_dragon.base.config.yaml_operator import YamlOperator
from one_dragon.utils import os_utils
from one_dragon.utils.log_utils import log

FILE_NAME: str = 'graphics_low_snapshot.yml'
LEGACY_DIR: str = 'config'  # 旧版本存放快照的目录，相对一条龙工作目录，只用于迁移


class GraphicsLowSnapshotConfig(YamlOperator):
    """降画质前记下的原始档位，全局唯一。"""

    def __init__(self, data_dir: Path) -> None:
        YamlOperator.__init__(self, str(Path(data_dir) / FILE_NAME))
        self._migrate_legacy()

    def _migrate_legacy(self) -> None:
        """把旧版本写在 config/ 下的快照搬到新位置，只在目标文件不存在时做一次。"""
        if self.is_file_exists:
            return
        legacy_path = Path(os_utils.get_path_under_work_dir(LEGACY_DIR, FILE_NAME))
        if not legacy_path.is_file():
            return
        legacy = YamlOperator(str(legacy_path))
        if not isinstance(legacy.data, dict) or not legacy.data:
            return
        self.data = dict(legacy.data)
        self.save()
        log.info(f'原始画质快照已从 {legacy_path} 迁移到 {self.file_path}')

    @property
    def original_fps(self) -> str:
        """原始帧率，空串表示没记录到。"""
        return self.get('original_fps', '')

    @original_fps.setter
    def original_fps(self, new_value: str) -> None:
        self.update('original_fps', new_value)

    @property
    def original_render_scale(self) -> str:
        """原始渲染精度，空串表示没记录到。"""
        return self.get('original_render_scale', '')

    @original_render_scale.setter
    def original_render_scale(self, new_value: str) -> None:
        self.update('original_render_scale', new_value)

    @property
    def original_antialias(self) -> str:
        """原始抗锯齿，空串表示没记录到。"""
        return self.get('original_antialias', '')

    @original_antialias.setter
    def original_antialias(self, new_value: str) -> None:
        self.update('original_antialias', new_value)

    @property
    def original_font(self) -> str:
        """原始字体选项，空串表示没记录到。

        字体在「其他」页，只能等切过去之后再记，所以它会比上面三项晚一步写入；
        老版本记下的快照里没有这一项，运行时会补记一次。
        """
        return self.get('original_font', '')

    @original_font.setter
    def original_font(self, new_value: str) -> None:
        self.update('original_font', new_value)

    @property
    def snapshot_date(self) -> str:
        """记录日期，格式 YYYY-MM-DD。"""
        return self.get('snapshot_date', '')

    @snapshot_date.setter
    def snapshot_date(self, new_value: str) -> None:
        self.update('snapshot_date', new_value)

    def clear(self) -> None:
        """清空快照，下次运行重新记录。"""
        self.original_fps = ''
        self.original_render_scale = ''
        self.original_antialias = ''
        self.original_font = ''
        self.snapshot_date = ''
