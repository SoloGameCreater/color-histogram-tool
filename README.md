# 颜色直方图工具

这是一个 Python 工具，用于分析图片中的颜色分布并生成直方图。

## 安装

1.  确保您已安装 Python 3。
2.  克隆此仓库或下载代码。
3.  安装所需的依赖库：
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

```bash
python color_histogram.py <图片路径> [--top N] [--output <输出文件名> | --save-to-report]
```

*   `<图片路径>`: 您要分析的图片文件的路径。
*   `--top N` (可选): 指定直方图中显示的最常见颜色数量上限 (默认: 50)。
*   `--output <输出文件名>` (可选): 将生成的直方图图片保存为指定的文件名（例如 `results/my_hist.png`），并在同一目录下生成固定的 `color_report.txt` 报告。如果未提供此选项或 `--save-to-report`，直方图将直接显示。
*   `--save-to-report` (可选): 自动在 `./report/` 目录下创建一个以输入图片名命名的子文件夹 (例如 `./report/input_image_name/`)，并在该子文件夹中保存固定名称的 `histogram.png` 和 `color_report.txt` 文件。

**注意**: `--output` 和 `--save-to-report` 选项不能同时使用。

## 示例

```bash
python color_histogram.py example.png
```

```bash
python color_histogram.py assets/my_image.jpg --output report/color_distribution.png
``` 