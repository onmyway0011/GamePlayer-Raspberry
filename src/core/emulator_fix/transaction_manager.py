#!/usr/bin/env python3
"""
事务管理器 - 提供事务性操作，支持回滚
"""

import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from contextlib import contextmanager
from dataclasses import dataclass
from .logger_setup import get_logger

logger = get_logger("transaction")

@dataclass

class TransactionOperation:
    """事务操作"""
    operation_id: str
    operation_type: str
    description: str
    forward_action: Callable[[], Any]
    rollback_action: Callable[[], Any]
    executed: bool = False
    result: Any = None
    error: Optional[Exception] = None


class TransactionManager:
    """事务管理器"""

    def __init__(self):
        """初始化事务管理器"""
        self.operations: List[TransactionOperation] = []
        self.backup_dir: Optional[Path] = None
        self.in_transaction = False
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None

    def start_transaction(self, backup_enabled: bool = True) -> None:
        """开始事务"""
        if self.in_transaction:
            raise RuntimeError("事务已经在进行中")

        self.in_transaction = True
        self.operations.clear()

        if backup_enabled:
            self._temp_dir = tempfile.TemporaryDirectory(prefix="emulator_fix_backup_")
            self.backup_dir = Path(self._temp_dir.name)
            logger.info(f"🔄 开始事务，备份目录: {self.backup_dir}")
        else:
            logger.info("🔄 开始事务（无备份）")

    def add_file_operation(self,
        """TODO: Add docstring"""
                          operation_id: str,
                          operation_type: str,
                          description: str,
                          target_path: Union[str, Path],
                          content: Optional[bytes] = None,
                          source_path: Optional[Union[str, Path]] = None) -> None:
        """添加文件操作"""
        if not self.in_transaction:
            raise RuntimeError("没有活动的事务")

        target_path = Path(target_path)

        # 创建备份
        backup_path = None
        if self.backup_dir and target_path.exists():
            backup_path = self.backup_dir / f"{operation_id}_{target_path.name}"
            shutil.copy2(target_path, backup_path)
            logger.debug(f"📋 创建备份: {target_path} -> {backup_path}")

        # 定义前进和回滚操作
        def forward_action():
            """TODO: Add docstring"""
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if content is not None:
                # 写入内容
                with open(target_path, 'wb') as f:
                    f.write(content)
                logger.debug(f"✏️ 写入文件: {target_path}")
            elif source_path:
                # 复制文件
                shutil.copy2(source_path, target_path)
                logger.debug(f"📁 复制文件: {source_path} -> {target_path}")
            else:
                # 创建空文件
                target_path.touch()
                logger.debug(f"📄 创建文件: {target_path}")

            return target_path

        def rollback_action():
            """TODO: Add docstring"""
            if target_path.exists():
                target_path.unlink()
                logger.debug(f"🗑️ 删除文件: {target_path}")

            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, target_path)
                logger.debug(f"🔙 恢复备份: {backup_path} -> {target_path}")

        operation = TransactionOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            description=description,
            forward_action=forward_action,
            rollback_action=rollback_action
        )

        self.operations.append(operation)
        logger.debug(f"➕ 添加文件操作: {description}")

    def add_directory_operation(self,
        """TODO: Add docstring"""
                               operation_id: str,
                               operation_type: str,
                               description: str,
                               target_path: Union[str, Path],
                               create: bool = True) -> None:
        """添加目录操作"""
        if not self.in_transaction:
            raise RuntimeError("没有活动的事务")

        target_path = Path(target_path)
        existed_before = target_path.exists()

        def forward_action():
            """TODO: Add docstring"""
            if create:
                target_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"📁 创建目录: {target_path}")
            else:
                if target_path.exists():
                    shutil.rmtree(target_path)
                    logger.debug(f"🗑️ 删除目录: {target_path}")
            return target_path

        def rollback_action():
            """TODO: Add docstring"""
            if create and not existed_before and target_path.exists():
                shutil.rmtree(target_path)
                logger.debug(f"🔙 回滚删除目录: {target_path}")
            elif not create and existed_before and not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"🔙 回滚创建目录: {target_path}")

        operation = TransactionOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            description=description,
            forward_action=forward_action,
            rollback_action=rollback_action
        )

        self.operations.append(operation)
        logger.debug(f"➕ 添加目录操作: {description}")

    def add_custom_operation(self,
        """TODO: Add docstring"""
                            operation_id: str,
                            operation_type: str,
                            description: str,
                            forward_action: Callable[[], Any],
                            rollback_action: Callable[[], Any]) -> None:
        """添加自定义操作"""
        if not self.in_transaction:
            raise RuntimeError("没有活动的事务")

        operation = TransactionOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            description=description,
            forward_action=forward_action,
            rollback_action=rollback_action
        )

        self.operations.append(operation)
        logger.debug(f"➕ 添加自定义操作: {description}")

    def execute_operation(self, operation: TransactionOperation):
        """执行单个操作"""
        try:
            logger.info(f"🚀 执行操作: {operation.description}")
            operation.result = operation.forward_action()
            operation.executed = True
            logger.info(f"✅ 操作成功: {operation.description}")
            return True
        except Exception as e:
            operation.error = e
            logger.error(f"❌ 操作失败: {operation.description} - {e}")
            return False

    def commit(self):
        """提交事务"""
        if not self.in_transaction:
            raise RuntimeError("没有活动的事务")

        logger.info(f"💾 提交事务，共 {len(self.operations)} 个操作")

        executed_operations = []

        try:
            # 执行所有操作
            for operation in self.operations:
                if self.execute_operation(operation):
                    executed_operations.append(operation)
                else:
                    # 操作失败，回滚已执行的操作
                    logger.error(f"❌ 操作失败，开始回滚")
                    self._rollback_operations(executed_operations)
                    return False

            # 所有操作成功
            logger.info("✅ 事务提交成功")
            self._cleanup()
            return True

        except Exception as e:
            logger.error(f"❌ 事务执行异常: {e}")
            self._rollback_operations(executed_operations)
            return False

    def rollback(self) -> None:
        """回滚事务"""
        if not self.in_transaction:
            raise RuntimeError("没有活动的事务")

        logger.info("🔙 回滚事务")
        executed_operations = [op for op in self.operations if op.executed]
        self._rollback_operations(executed_operations)
        self._cleanup()

    def _rollback_operations(self, operations: List[TransactionOperation]) -> None:
        """回滚操作列表"""
        # 按相反顺序回滚
        for operation in reversed(operations):
            try:
                logger.info(f"🔙 回滚操作: {operation.description}")
                operation.rollback_action()
                logger.info(f"✅ 回滚成功: {operation.description}")
            except Exception as e:
                logger.error(f"❌ 回滚失败: {operation.description} - {e}")

    def _cleanup(self) -> None:
        """清理事务"""
        self.in_transaction = False
        self.operations.clear()

        if self._temp_dir:
            try:
                self._temp_dir.cleanup()
                logger.debug("🧹 清理临时目录")
            except Exception as e:
                logger.warning(f"⚠️ 清理临时目录失败: {e}")
            finally:
                self._temp_dir = None
                self.backup_dir = None

    def get_operation_summary(self) -> Dict[str, Any]:
        """获取操作摘要"""
        total = len(self.operations)
        executed = len([op for op in self.operations if op.executed])
        failed = len([op for op in self.operations if op.error])

        return {
            "total_operations": total,
            "executed_operations": executed,
            "failed_operations": failed,
            "success_rate": (executed / total * 100) if total > 0 else 0,
            "operations": [
                {
                    "id": op.operation_id,
                    "type": op.operation_type,
                    "description": op.description,
                    "executed": op.executed,
                    "error": str(op.error) if op.error else None
                }
                for op in self.operations
            ]
        }

@contextmanager

def transaction(backup_enabled: bool = True):
    """事务上下文管理器"""
    manager = TransactionManager()
    manager.start_transaction(backup_enabled)

    try:
        yield manager
        if not manager.commit():
            raise RuntimeError("事务提交失败")
    except Exception as e:
        logger.error(f"❌ 事务异常: {e}")
        manager.rollback()
        raise
    finally:
        if manager.in_transaction:
            manager._cleanup()

if __name__ == "__main__":
    # 测试事务管理器
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        test_file = test_dir / "test.txt"

        try:
            # 测试成功的事务
            with transaction() as tx:
                tx.add_file_operation(
                    "create_file",
                    "file_creation",
                    "创建测试文件",
                    test_file,
                    content=b"Hello, World!"
                )

            assert test_file.exists()
            assert test_file.read_text() == "Hello, World!"
            print("✅ 成功事务测试通过")

            # 测试失败的事务
            try:
                with transaction() as tx:
                    tx.add_file_operation(
                        "modify_file",
                        "file_modification",
                        "修改测试文件",
                        test_file,
                        content=b"Modified content"
                    )

                    # 模拟失败
                    tx.add_custom_operation(
                        "fail_operation",
                        "test_failure",
                        "故意失败的操作",
                        lambda: exec('raise Exception("故意失败")'),
                        lambda: None
                    )
            except Exception:
                pass

            # 文件应该回滚到原始内容
            assert test_file.read_text() == "Hello, World!"
            print("✅ 失败事务回滚测试通过")

        except Exception as e:
            print(f"❌ 事务管理器测试失败: {e}")
            raise

        print("✅ 事务管理器测试完成")
