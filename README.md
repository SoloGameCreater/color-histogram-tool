# 颜色直方图工具

这是一个 Python 工具，用于分析图片中的颜色分布并生成直方图和颜色报告。

默认情况下，工具会进行 64 色量化（合并相似颜色）以生成更符合视觉感知的分布，并将结果保存到报告目录。

## 安装

1.  确保您已安装 Python 3 和 pip。
2.  克隆此仓库或下载代码。
3.  在项目根目录打开终端，安装所需的依赖库：
    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

```bash
python color_histogram.py <图片路径> [--top N]
```

*   `<图片路径>`: 您要分析的图片文件的路径 (必需)。
*   `--top N` (可选): 指定直方图中显示的最常见颜色数量上限 (默认: 50)。

**输出:**

脚本执行后，会在项目根目录下创建一个 `report` 文件夹。对于输入的每张图片 (例如 `my_image.jpg`)，会在 `report` 下创建一个同名子文件夹 (`report/my_image/`)，其中包含：
*   `histogram.png`: 显示 Top N 颜色分布的直方图。
*   `color_report.txt`: 包含 Top N 颜色的 HEX 值和百分比的文本文件。

## 示例

```bash
# 分析 example.png 并将结果保存到 report/example/ 目录
python color_histogram.py assets/example.png

# 分析 my_pic.jpeg，只在直方图中显示前 30 种颜色，结果保存到 report/my_pic/
python color_histogram.py images/my_pic.jpeg --top 30
```

## 示例展示

以下是一个示例图片及其通过此工具生成的颜色直方图：

**示例输入 (`assets/sample.jpg`)**

![示例输入图片](./assets/sample.jpg "示例雪山湖景图")

**示例输出 (`assets/histogram.png`)**

![示例输出直方图](./assets/histogram.png "示例图片颜色直方图 (Top 50)") 