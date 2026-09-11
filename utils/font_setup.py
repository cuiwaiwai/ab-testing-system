# -*- coding: utf-8 -*-
"""
A/B测试实验设计与分析系统 - 中文字体配置模块
自动探测并适配 Windows / Linux / macOS 环境，
确保 matplotlib 图表在本地和云端服务器上都能正常显示中文。
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager


# 按优先级排列的中文字体候选（覆盖 Windows / Linux / macOS）
CJK_FONT_CANDIDATES = [
    # --- Windows ---
    "Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong",
    # --- Linux / 云服务器 (Streamlit Cloud) ---
    "WenQuanYi Zen Hei", "WenQuanYi Micro Hei",
    "Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Sans SC",
    "Source Han Sans CN", "Source Han Sans SC",
    "Droid Sans Fallback", "AR PL UMing CN", "AR PL UKai CN",
    # --- macOS ---
    "PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS",
    # --- 兜底 ---
    "DejaVu Sans",
]


def _detect_available_font():
    """探测系统中第一个可用的中文字体"""
    try:
        available = {f.name for f in font_manager.fontManager.ttflist}
    except Exception:
        return None

    for name in CJK_FONT_CANDIDATES:
        if name in available:
            return name
    return None


def setup_chinese_font(verbose: bool = False):
    """配置 matplotlib 中文字体，返回实际生效的字体名

    在 Windows 上会使用雅黑/黑体，在 Linux 服务器上会自动切换到
    文泉驿或 Noto CJK 等开源中文字体。
    """
    chosen = _detect_available_font()

    # 生成字体优先级列表：命中字体排第一，其余作为后备
    font_list = []
    if chosen:
        font_list.append(chosen)
    for name in CJK_FONT_CANDIDATES:
        if name not in font_list:
            font_list.append(name)

    plt.rcParams["font.sans-serif"] = font_list
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

    if verbose:
        print(f"[font_setup] 当前使用中文字体: {chosen or '未找到，可能显示方块'}")

    return chosen


# 模块被导入时自动完成配置
ACTIVE_CJK_FONT = setup_chinese_font()
