import argparse
from collections import Counter
from PIL import Image, ImageDraw
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

def analyze_image_colors(image_path, num_quant_colors=0):
    """分析图片颜色并返回颜色及其计数的字典。

    Args:
        image_path (str): 图片路径。
        num_quant_colors (int): 量化后的目标颜色数量。如果为 0 或 None，则不进行量化。
    """
    try:
        img_original = Image.open(image_path)

        # --- 修改：先将图片统一转换为 RGB --- 
        print("将图片转换为 RGB 模式...")
        img_rgb = img_original.convert('RGB')
        print(f"转换完成，图像模式: {img_rgb.mode}")

        # --- 修改：在 RGB 图像上进行量化 --- 
        img_to_process = img_rgb # 默认使用 RGB 图像
        if num_quant_colors and num_quant_colors > 0:
            print(f"对 RGB 图像进行颜色量化，目标颜色数量: {num_quant_colors}")
            # MEDIANCUT 可以在 RGB 上正常工作
            try:
                # 量化 RGB 图像
                img_quantized = img_rgb.quantize(colors=num_quant_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
                # 将量化后的 'P' 模式图像转换回 RGB 以便获取像素值
                img_to_process = img_quantized.convert('RGB')
                print("颜色量化完成。")
            except Exception as quant_error:
                print(f"警告：颜色量化失败: {quant_error}。将统计转换后的 RGB 颜色。")
                # 量化失败，则继续使用之前转换好的 RGB 图像 (img_rgb)
                img_to_process = img_rgb
        # --- 结束：颜色量化 ---

        # 确保我们有一个图像来处理 (img_to_process 总是存在的)
        # print(f"最终处理的图像模式: {img_to_process.mode}") # Debug
        pixels = list(img_to_process.getdata())
        # print(f"获取了 {len(pixels)} 像素数据") # Debugging line

        color_counts = Counter(pixels)
        # print(f"计数完成，原始不同颜色数: {len(color_counts)}") # Debugging line
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

    try:
        plt.savefig(output_file)
        print(f"直方图已保存到 '{output_file}'")
        plt.close() # 关闭图形，防止在循环中使用时内存泄漏或窗口堆积
    except Exception as e:
        print(f"保存直方图文件时出错: {e}")

def main():
    # --- 修改：简化参数解析器 --- 
    parser = argparse.ArgumentParser(description='生成图片颜色分布直方图 (默认进行 64 色量化并保存结果)。')
    parser.add_argument('image_path', type=str, help='输入图片文件的路径。')
    parser.add_argument('--top', type=int, default=50, help='直方图显示的最常见颜色数量上限 (默认: 50)。')
    # 移除 output, save-to-report, quantize 参数
    args = parser.parse_args()
    # --- 结束修改 ---

    # --- 修改：设定默认行为 --- 
    num_quant_colors_default = 64
    # 根据输入图片名计算输出路径
    input_filename = os.path.basename(args.image_path)
    base_name = os.path.splitext(input_filename)[0]
    output_dir = os.path.join("report", base_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path_for_plot = os.path.join(output_dir, "histogram.png")
    # --- 结束修改 ---

    print(f"正在分析图片: {args.image_path}")
    print(f"默认进行颜色量化 (目标 {num_quant_colors_default} 色)... " ) # 添加提示
    # 传递量化参数
    color_data = analyze_image_colors(args.image_path, num_quant_colors=num_quant_colors_default)

    if color_data:
        print(f"分析完成，找到 {len(color_data)} 种不同的颜色（已量化）。")
        # 传递计算好的输出路径给绘图函数
        plot_color_histogram(color_data, output_path_for_plot, max_colors_to_plot=args.top)

if __name__ == "__main__":
    main() 