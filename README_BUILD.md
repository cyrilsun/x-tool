# X-Tool 构建说明

本文档介绍如何使用构建脚本来构建X-Tool的多平台可执行文件。

## 构建环境要求

- Python 3.7+
- PyInstaller 6.0+
- PyQt6 6.0+

## 安装构建依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装PyInstaller
pip install pyinstaller
```

## 构建脚本使用方法

### 基本用法

```bash
# 运行构建脚本
python build.py
```

### 命令行参数

```
X-Tool多平台构建脚本

optional arguments:
  -h, --help            show this help message and exit
  --platform {windows,macos,linux,all}
                        选择构建平台 (默认: all)
  --clean               清理构建文件
  --onefile             生成单文件可执行程序
```

### 示例

1. **构建所有平台**
   ```bash
   python build.py
   ```

2. **只构建macOS版本**
   ```bash
   python build.py --platform macos
   ```

3. **构建单文件可执行程序**
   ```bash
   python build.py --platform windows --onefile
   ```

4. **清理构建文件**
   ```bash
   python build.py --clean
   ```

## 构建输出

构建完成后，可执行文件将生成在 `dist` 目录中：

- **Windows**: `dist/X-Tool.exe`
- **macOS**: `dist/X-Tool.app`
- **Linux**: `dist/X-Tool`

## 资源文件

构建过程中会自动包含 `resources` 目录下的资源文件。如果需要添加自定义图标，请将图标文件放在 `resources` 目录下：

- Windows: `resources/icon.ico`
- macOS: `resources/icon.icns`
- Linux: `resources/icon.png`

## 注意事项

1. **跨平台构建限制**：
   - 通常建议在目标平台上进行构建
   - macOS版本需要在macOS系统上构建
   - Windows版本可以在Windows或通过WSL构建
   - Linux版本可以在Linux系统上构建

2. **单文件与文件夹模式**：
   - 默认生成文件夹模式（包含依赖文件），启动速度较慢但便于调试
   - `--onefile` 选项生成单文件可执行程序，便于分发但启动速度较慢

3. **构建问题排查**：
   - 如果构建失败，请检查Python环境和依赖是否正确安装
   - 查看构建日志中的错误信息
   - 尝试使用 `--clean` 选项清理后重新构建

4. **权限问题**：
   - Linux/macOS系统可能需要执行 `chmod +x dist/X-Tool` 来赋予执行权限

## 高级配置

如果需要自定义构建配置，可以直接编辑 `build.py` 文件，修改对应平台的PyInstaller命令参数。
