#!/usr/bin/env python3
"""
状态管理器 - 跟踪修复过程的状态和进度
"""

import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from .logger_setup import get_logger

logger = get_logger("state")


class FixStatus(Enum):
    """修复状态枚举"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class FixType(Enum):
    """修复类型枚举"""
    ROM_CREATION = "rom_creation"
    ROM_REPAIR = "rom_repair"
    EMULATOR_INSTALL = "emulator_install"
    EMULATOR_CONFIG = "emulator_config"
    SYSTEM_CHECK = "system_check"
    CLEANUP = "cleanup"

@dataclass

class FixItem:
    """修复项目"""
    id: str
    type: FixType
    name: str
    description: str
    status: FixStatus = FixStatus.NOT_STARTED
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_completed(self):
        """是否已完成"""
        return self.status == FixStatus.COMPLETED

    @property
    def is_failed(self):
        """是否失败"""
        return self.status == FixStatus.FAILED

    def start(self) -> None:
        """开始执行"""
        self.status = FixStatus.IN_PROGRESS
        self.start_time = time.time()
        logger.debug(f"🚀 开始执行: {self.name}")

    def complete(self, details: Optional[Dict[str, Any]] = None) -> None:
        """完成执行"""
        self.status = FixStatus.COMPLETED
        self.end_time = time.time()
        if details:
            self.details.update(details)
        logger.info(f"✅ 完成: {self.name} (耗时: {self.duration:.2f}s)")

    def fail(self, error_message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """执行失败"""
        self.status = FixStatus.FAILED
        self.end_time = time.time()
        self.error_message = error_message
        if details:
            self.details.update(details)
        logger.error(f"❌ 失败: {self.name} - {error_message}")

    def skip(self, reason: str) -> None:
        """跳过执行"""
        self.status = FixStatus.SKIPPED
        self.details["skip_reason"] = reason
        logger.info(f"⏭️ 跳过: {self.name} - {reason}")

@dataclass

class FixSession:
    """修复会话"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    items: List[FixItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """获取会话时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def total_items(self) -> int:
        """总项目数"""
        return len(self.items)

    @property
    def completed_items(self) -> int:
        """已完成项目数"""
        return len([item for item in self.items if item.is_completed])

    @property
    def failed_items(self) -> int:
        """失败项目数"""
        return len([item for item in self.items if item.is_failed])

    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total_items == 0:
            return 0.0
        finished = len([item for item in self.items if item.status in [FixStatus.COMPLETED, FixStatus.FAILED, FixStatus.SKIPPED]])
        return (finished / self.total_items) * 100

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100

    def add_item(self, item: FixItem) -> None:
        """添加修复项目"""
        self.items.append(item)
        logger.debug(f"📝 添加修复项目: {item.name}")

    def get_item(self, item_id: str) -> Optional[FixItem]:
        """获取修复项目"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def finish(self) -> None:
        """结束会话"""
        self.end_time = time.time()
        logger.info(f"🏁 修复会话结束: {self.session_id} (耗时: {self.duration:.2f}s)")


class StateManager:
    """状态管理器"""

    def __init__(self, state_file: Optional[Path] = None):
        """初始化状态管理器"""
        if state_file is None:
            state_file = Path("data/state/fix_state.json")

        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[FixSession] = None
        self.sessions: List[FixSession] = []

        self._load_state()

    def start_session(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> FixSession:
        """开始新的修复会话"""
        if session_id is None:
            session_id = f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if metadata is None:
            metadata = {}

        self.current_session = FixSession(
            session_id=session_id,
            start_time=time.time(),
            metadata=metadata
        )

        logger.info(f"🎯 开始修复会话: {session_id}")
        return self.current_session

    def add_fix_item(self,
        """TODO: Add docstring"""
                    item_id: str,
                    fix_type: FixType,
                    name: str,
                    description: str,
                    details: Optional[Dict[str, Any]] = None) -> FixItem:
        """添加修复项目"""
        if self.current_session is None:
            raise RuntimeError("没有活动的修复会话")

        item = FixItem(
            id=item_id,
            type=fix_type,
            name=name,
            description=description,
            details=details or {}
        )

        self.current_session.add_item(item)
        self._save_state()
        return item

    def get_current_item(self, item_id: str) -> Optional[FixItem]:
        """获取当前会话的修复项目"""
        if self.current_session is None:
            return None
        return self.current_session.get_item(item_id)

    def finish_session(self) -> Optional[FixSession]:
        """结束当前会话"""
        if self.current_session is None:
            return None

        self.current_session.finish()
        self.sessions.append(self.current_session)

        # 保存状态
        self._save_state()

        session = self.current_session
        self.current_session = None
        return session

    def get_session_summary(self, session: Optional[FixSession] = None) -> Dict[str, Any]:
        """获取会话摘要"""
        if session is None:
            session = self.current_session

        if session is None:
            return {}

        return {
            "session_id": session.session_id,
            "duration": session.duration,
            "total_items": session.total_items,
            "completed_items": session.completed_items,
            "failed_items": session.failed_items,
            "progress_percentage": session.progress_percentage,
            "success_rate": session.success_rate,
            "start_time": datetime.fromtimestamp(session.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(session.end_time).isoformat() if session.end_time else None
        }

    def _load_state(self) -> None:
        """加载状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 加载历史会话
                for session_data in data.get("sessions", []):
                    session = FixSession(
                        session_id=session_data["session_id"],
                        start_time=session_data["start_time"],
                        end_time=session_data.get("end_time"),
                        metadata=session_data.get("metadata", {})
                    )

                    for item_data in session_data.get("items", []):
                        item = FixItem(
                            id=item_data["id"],
                            type=FixType(item_data["type"]),
                            name=item_data["name"],
                            description=item_data["description"],
                            status=FixStatus(item_data["status"]),
                            start_time=item_data.get("start_time"),
                            end_time=item_data.get("end_time"),
                            error_message=item_data.get("error_message"),
                            details=item_data.get("details", {})
                        )
                        session.items.append(item)

                    self.sessions.append(session)

                logger.debug(f"📂 加载状态: {len(self.sessions)} 个历史会话")
        except Exception as e:
            logger.warning(f"⚠️ 加载状态失败: {e}")

    def _save_state(self) -> None:
        """保存状态"""
        try:
            data = {
                "sessions": []
            }

            # 保存所有会话
            all_sessions = self.sessions.copy()
            if self.current_session:
                all_sessions.append(self.current_session)

            for session in all_sessions:
                session_data = {
                    "session_id": session.session_id,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "metadata": session.metadata,
                    "items": []
                }

                for item in session.items:
                    item_data = {
                        "id": item.id,
                        "type": item.type.value,
                        "name": item.name,
                        "description": item.description,
                        "status": item.status.value,
                        "start_time": item.start_time,
                        "end_time": item.end_time,
                        "error_message": item.error_message,
                        "details": item.details
                    }
                    session_data["items"].append(item_data)

                data["sessions"].append(session_data)

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ 保存状态失败: {e}")

# 全局状态管理器实例
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """获取状态管理器单例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

if __name__ == "__main__":
    # 测试状态管理器
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        state_file = Path(temp_dir) / "test_state.json"
        manager = StateManager(state_file)

        # 开始会话
        session = manager.start_session("test_session")

        # 添加修复项目
        item1 = manager.add_fix_item("rom1", FixType.ROM_CREATION, "创建ROM1", "创建测试ROM文件")
        item2 = manager.add_fix_item("emu1", FixType.EMULATOR_INSTALL, "安装模拟器1", "安装测试模拟器")

        # 模拟执行
        item1.start()
        time.sleep(0.1)
        item1.complete({"size": 1024})

        item2.start()
        time.sleep(0.1)
        item2.fail("安装失败")

        # 结束会话
        finished_session = manager.finish_session()

        # 打印摘要
        summary = manager.get_session_summary(finished_session)
        print("📊 会话摘要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        print("✅ 状态管理器测试完成")
