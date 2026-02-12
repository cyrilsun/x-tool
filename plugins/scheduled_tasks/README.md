# 定时任务插件模块

完全独立的定时任务管理模块，不依赖 X-Tool 基础框架的数据库。

## 📁 目录结构

```
plugin_market/
├── scheduled_tasks_plugin.py    # 主插件文件
└── scheduled_tasks/             # 独立模块目录
    ├── __init__.py              # 模块初始化
    ├── database.py              # 数据库管理
    ├── scheduler.py             # 任务调度器
    ├── executor.py              # 任务执行器
    └── README.md                # 说明文档（本文件）
```

## 🎯 功能特性

### 支持的任务类型

1. **显示消息** - 在指定时间弹出消息提示
2. **执行命令** - 执行系统命令或脚本

### 支持的触发方式

1. **单次执行** - 在指定的日期时间执行一次
2. **周期执行** - 按指定的时间间隔重复执行
3. **Cron 表达式** - 使用类似 Cron 的规则定期执行

### 主要功能

- ✅ 任务的创建、编辑、删除和启用/禁用
- ✅ 实时查看任务执行状态和日志
- ✅ 任务持久化存储（使用独立的 SQLite 数据库）
- ✅ 重启后自动恢复任务
- ✅ 完全独立于基础框架

## 📦 依赖安装

### 方式一：使用脚本安装（推荐）

```bash
./install_plugin_deps.sh
# 选择 3) 仅安装 scheduled_tasks_plugin 依赖
```

### 方式二：手动安装

```bash
# 安装到 lib 目录
pip install -t lib APScheduler
```

## 🗄️ 数据库

### 数据库位置

```
~/Library/Application Support/X-Tool/scheduled_tasks_plugin/scheduled_tasks.db  (macOS)
~/.local/share/X-Tool/scheduled_tasks_plugin/scheduled_tasks.db                 (Linux)
C:\Users\<用户>\AppData\Local\X-Tool\scheduled_tasks_plugin\scheduled_tasks.db (Windows)
```

### 数据表结构

#### scheduled_tasks 表
存储定时任务配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 任务名称（唯一） |
| description | TEXT | 任务描述 |
| task_type | TEXT | 任务类型 (message/command) |
| trigger_type | TEXT | 触发器类型 (once/interval/cron) |
| trigger_config | TEXT | 触发器配置 (JSON) |
| task_config | TEXT | 任务配置 (JSON) |
| is_enabled | BOOLEAN | 是否启用 |
| next_run_time | TIMESTAMP | 下次运行时间 |
| last_run_time | TIMESTAMP | 上次运行时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### task_execution_logs 表
存储任务执行日志

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 关联任务 ID |
| status | TEXT | 执行状态 (success/failed/running) |
| start_time | TIMESTAMP | 开始时间 |
| end_time | TIMESTAMP | 结束时间 |
| output | TEXT | 执行输出 |
| error_message | TEXT | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |

## 🚀 模块架构

### database.py - 数据库管理

```python
from scheduled_tasks.database import get_database

# 获取数据库单例
db = get_database()

# 添加任务
task_id = db.add_task(
    name="我的任务",
    description="任务描述",
    task_type="message",
    trigger_type="once",
    trigger_config={"run_date": "2026-02-11T09:00:00"},
    task_config={"message": "Hello World"}
)

# 获取所有任务
tasks = db.get_all_tasks()

# 更新任务
db.update_task("我的任务", is_enabled=False)

# 删除任务
db.delete_task("我的任务")
```

### scheduler.py - 任务调度器

```python
from scheduled_tasks.scheduler import TaskScheduler

# 创建调度器
scheduler = TaskScheduler()

# 添加任务
scheduler.add_task(
    task_id=1,
    task_func=lambda: print("Task executed"),
    trigger_type="once",
    trigger_config={"run_date": "2026-02-11T09:00:00"},
    task_name="我的任务"
)

# 获取下次运行时间
next_run = scheduler.get_next_run_time(1)

# 移除任务
scheduler.remove_task(1)

# 关闭调度器
scheduler.shutdown()
```

### executor.py - 任务执行器

```python
from scheduled_tasks.executor import TaskExecutor

# 创建执行器
executor = TaskExecutor(ui_callback=my_callback)

# 执行任务
task = {
    "id": 1,
    "name": "我的任务",
    "task_type": "message",
    "task_config": {"message": "Hello"}
}

success = executor.execute_task(task)
```

## 📝 使用示例

### 示例 1：创建一个消息提醒任务

```python
# 通过 UI 创建
# 1. 打开"定时任务"插件
# 2. 点击"新建任务"
# 3. 填写信息：
#    - 任务名称：喝水提醒
#    - 任务类型：显示消息
#    - 消息内容：该喝水了！
#    - 触发方式：周期执行
#    - 间隔时间：1 小时
# 4. 点击确定
```

### 示例 2：创建定时备份任务

```python
# 通过代码创建
from scheduled_tasks.database import get_database
from scheduled_tasks.scheduler import TaskScheduler

db = get_database()
scheduler = TaskScheduler()

# 创建任务
task_id = db.add_task(
    name="每日备份",
    description="每天凌晨 2 点执行备份",
    task_type="command",
    trigger_type="cron",
    trigger_config={
        "hour": "2",
        "minute": "0",
        "day": "*",
        "day_of_week": "*"
    },
    task_config={
        "command": "/path/to/backup.sh"
    }
)

# 添加到调度器
task = db.get_task_by_id(task_id)
def execute_backup():
    import subprocess
    subprocess.run(["/path/to/backup.sh"], shell=True)

scheduler.add_task(
    task_id,
    execute_backup,
    "cron",
    task["trigger_config"],
    "每日备份"
)
```

## 🔧 开发指南

### 添加新的任务类型

1. 在 `executor.py` 中添加执行方法：

```python
def _execute_my_custom_task(self, task_config):
    # 实现自定义任务逻辑
    pass
```

2. 在 `execute_task` 方法中添加分支：

```python
elif task_type == "my_custom":
    output = self._execute_my_custom_task(task_config)
```

3. 在 UI 中添加选项（`CreateTaskDialog` 类）

### 添加新的触发器类型

1. 在 `scheduler.py` 的 `_create_trigger` 方法中添加新逻辑

2. 在 UI 中添加配置界面

## 🐛 故障排除

### APScheduler 未安装

**错误**：`APScheduler 未安装，请运行: pip install APScheduler`

**解决**：
```bash
# 使用脚本安装
./install_plugin_deps.sh
# 选择 3) 仅安装 scheduled_tasks_plugin 依赖

# 或手动安装
pip install -t lib APScheduler
```

### 数据库文件损坏

**错误**：`sqlite3.DatabaseError: database disk image is malformed`

**解决**：
```bash
# 删除损坏的数据库文件，应用会自动重建
rm ~/Library/Application\ Support/X-Tool/scheduled_tasks_plugin/scheduled_tasks.db
```

## 📄 许可证

本模块遵循 X-Tool 项目的许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
