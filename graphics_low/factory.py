"""降低画质插件的应用工厂。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from one_dragon.base.operation.application.application_config import ApplicationConfig
from one_dragon.base.operation.application.application_factory import ApplicationFactory
from one_dragon.base.operation.application_base import Application

from . import const
from .app import GraphicsLowApp
from .config import GraphicsLowConfig

if TYPE_CHECKING:
    from one_dragon.base.operation.application.application_run_record import (
        AppRunRecord,
    )

    from zzz_od.context.zzz_context import ZContext


class GraphicsLowAppFactory(ApplicationFactory):

    def __init__(self, ctx: ZContext) -> None:
        ApplicationFactory.__init__(self, const)
        self.ctx: ZContext = ctx
        # 排序值不属于 const.py 也不属于 plugin.json，改在这里指定。
        # 50 让本应用排在一龙里所有应用之前，后续应用都在低画质下运行。
        self.priority: int | None = 50

    def create_application(self, instance_idx: int, group_id: str) -> Application:
        return GraphicsLowApp(self.ctx)

    def create_config(self, instance_idx: int, group_id: str) -> ApplicationConfig:
        return GraphicsLowConfig(instance_idx=instance_idx, group_id=group_id)

    def create_run_record(self, instance_idx: int) -> AppRunRecord | None:
        """不创建每日运行记录，一条龙每次运行都会执行本应用。"""
        return None
