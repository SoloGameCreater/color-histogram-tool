import argparse
from collections import Counter
from PIL import Image
import matplotlib.pyplot as plt
import os

# --- 开始：配置 Matplotlib 支持中文显示 ---
try:
    # 尝试使用 'SimHei' 或 'Microsoft YaHei' 字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题
except Exception as e:
    print(f"警告：设置中文字体时出错: {e}。图表中的中文可能无法正确显示。")
# --- 结束：配置 Matplotlib 支持中文显示 ---

def analyze_image_colors(image_path):
    """分析图片颜色并返回颜色及其计数的字典。"""
    try:
        img = Image.open(image_path)
        # 转换为 RGB 以处理带 Alpha 通道的图片（如 PNG）
        # 如果图像是调色板模式 (P)，先转换为 RGB
        if img.mode == 'P':
            img = img.convert('RGBA') # 先转 RGBA 保留透明度信息
            img = img.convert('RGB') # 再转 RGB，透明部分会变黑，但计数时忽略
        elif img.mode == 'RGBA':
             # 对于 RGBA 图像，我们可以选择将透明像素视为一种颜色或忽略它们
             # 这里我们将其转换为 RGB，透明像素会根据背景（通常是黑色或白色）混合
             # 或者我们可以直接获取所有像素，保留 alpha 值
             # 为了简化，先转换为 RGB，丢失 alpha 信息
             img = img.convert('RGB')
        elif img.mode != 'RGB':
             img = img.convert('RGB')


        pixels = list(img.getdata())
        # 对于非常大的图片，一次性加载所有像素可能消耗大量内存
        # 可以考虑分块处理或使用 img.getcolors()，但 getcolors 对颜色数量有限制

        # 移除纯黑像素 (0, 0, 0)，如果它们是转换产生的背景
        # color_counts = Counter(p for p in pixels if p != (0, 0, 0)) # 这是一个可选项
        color_counts = Counter(pixels)
        return color_counts
    except FileNotFoundError:
        print(f"错误：文件未找到 '{image_path}'")
        return None
    except Exception as e:
        print(f"打开或处理图片时出错: {e}")
        return None

def plot_color_histogram(color_counts, output_file=None, max_colors_to_plot=50):
    """根据颜色计数绘制直方图，只显示最常见的 N 种颜色。"""
    if not color_counts:
        print("没有颜色数据可供绘制。")
        return

    total_pixels = sum(color_counts.values())
    # 按像素数量降序排序颜色
    sorted_colors = sorted(color_counts.items(), key=lambda item: item[1], reverse=True)

    # 只取前 N 个最常见的颜色
    num_total_colors = len(sorted_colors)
    if num_total_colors > max_colors_to_plot:
        print(f"注意：图片包含 {num_total_colors} 种颜色，只显示最常见的 {max_colors_to_plot} 种。")
        sorted_colors = sorted_colors[:max_colors_to_plot]

    # 提取颜色和它们的百分比
    colors = [item[0] for item in sorted_colors]
    percentages = [(item[1] / total_pixels) * 100 for item in sorted_colors]

    # 将 RGB 颜色元组转换为 matplotlib 接受的格式 (0-1 范围)
    plot_colors = [(r/255, g/255, b/255) for r, g, b in colors]

    num_colors_to_plot = len(colors) # 实际绘制的颜色数量
    plt.figure(figsize=(max(10, num_colors_to_plot * 0.5), 6)) # 基于实际绘制数量调整宽度

    bars = plt.bar(range(num_colors_to_plot), percentages, color=plot_colors, tick_label=None)

    # 在每个柱子上方显示百分比
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{percentages[i]:.2f}%', ha='center', va='bottom', fontsize=8)

    # x 轴标签可以显示颜色值，但如果颜色太多会很拥挤
    # 可以考虑只显示前 N 个颜色的标签或完全隐藏
    if num_colors_to_plot <= 30: # 只在颜色数量较少时显示标签
       plt.xticks(range(num_colors_to_plot), [str(c) for c in colors], rotation=90, fontsize=6)
    else:
       plt.xticks([], []) # 颜色太多则隐藏标签
       plt.xlabel(f"{num_colors_to_plot} 种最常见的颜色 (标签已隐藏)")


    plt.ylabel('像素百分比 (%)')
    # 更新标题
    plt.title(f'图片颜色分布直方图 (显示 Top {num_colors_to_plot} 种颜色)')
    plt.tight_layout() # 调整布局防止标签重叠

    # --- 开始：添加保存颜色报告的功能 ---
    if output_file:
        # 修改：将文本报告保存到与图片相同的目录，但使用固定名称
        output_dir = os.path.dirname(output_file)
        # 确保目录存在 (理论上 main 函数已创建，但以防万一)
        if output_dir:
             os.makedirs(output_dir, exist_ok=True)
        else: # 如果 output_file 没有目录部分 (如 "hist.png")，则使用当前目录
            output_dir = "."

        text_output_path = os.path.join(output_dir, "color_report.txt") # 固定文件名
        try:
            # os.makedirs(os.path.dirname(text_output_path), exist_ok=True) # 上面已处理目录
            with open(text_output_path, 'w', encoding='utf-8') as f:
                f.write(f"图片主要颜色报告 (Top {num_colors_to_plot} 种)\n")
                f.write("=====================================\n")
                for i in range(num_colors_to_plot):
                    rgb_color = colors[i]
                    hex_color = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}".upper()
                    percentage = percentages[i]
                    f.write(f"{hex_color}\t{percentage:.2f}%\n")
            print(f"颜色报告已保存到 '{text_output_path}'")
        except Exception as e:
            print(f"保存颜色报告文件时出错: {e}")
    # --- 结束：添加保存颜色报告的功能 ---

    if output_file:
        try:
            # 确保输出目录存在
            # os.makedirs(os.path.dirname(output_file), exist_ok=True) # 这行在上面已处理
            plt.savefig(output_file)
            print(f"直方图已保存到 '{output_file}'")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='生成图片颜色分布直方图。')
    parser.add_argument('image_path', type=str, help='输入图片文件的路径。')
    parser.add_argument('--top', type=int, default=50, help='直方图显示的最常见颜色数量上限 (默认: 50)。')

    # 使用互斥组来处理输出选项
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        '--output',
        type=str,
        help='将直方图保存到的可选输出文件路径 (例如: report/custom_name.png)。'
    )
    output_group.add_argument(
        '--save-to-report',
        action='store_true',
        help='自动将输出保存到 \'report/\' 目录，文件名与输入图片名一致 (例如: report/input_image_name.png/.txt)。'
    )

    args = parser.parse_args()

    output_path_for_plot = None
    if args.output:
        output_path_for_plot = args.output
        output_dir = os.path.dirname(output_path_for_plot)
        if output_dir:  # 确保目录部分不为空
            os.makedirs(output_dir, exist_ok=True)
    elif args.save_to_report:
        input_filename = os.path.basename(args.image_path)
        base_name = os.path.splitext(input_filename)[0]
        # 修改：创建以图片名命名的子目录
        output_dir = os.path.join("report", base_name)
        os.makedirs(output_dir, exist_ok=True)
        # 修改：使用固定的图片文件名
        output_path_for_plot = os.path.join(output_dir, "histogram.png")

    print(f"正在分析图片: {args.image_path}")
    color_data = analyze_image_colors(args.image_path)

    if color_data:
        print(f"分析完成，找到 {len(color_data)} 种不同的颜色。")
        # 传递计算好的输出路径给绘图函数
        plot_color_histogram(color_data, output_path_for_plot, max_colors_to_plot=args.top)

if __name__ == "__main__":
    main() 