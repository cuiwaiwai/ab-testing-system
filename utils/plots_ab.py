# -*- coding: utf-8 -*-
"""
A/B测试实验设计与分析系统 - 可视化模块 V2.0
功能：提供AB测试相关的专业图表，支持动态配色主题
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional, Dict, Any, Tuple

# 中文字体（自动适配 Windows / Linux 云端服务器）
from utils.font_setup import setup_chinese_font

sns.set_style("whitegrid")
setup_chinese_font()


def _get_theme_colors():
    """从Streamlit会话状态获取当前配色方案的颜色"""
    try:
        import streamlit as st
        if "color_theme" in st.session_state:
            from app import COLOR_THEMES
            theme = COLOR_THEMES[st.session_state.color_theme]
            return {
                "color_a": theme.get("chart_a", "#3498db"),
                "color_b": theme.get("chart_b", "#e74c3c"),
                "primary": theme.get("primary", "#FF6B6B"),
                "secondary": theme.get("secondary", "#4ECDC4"),
                "bg_card": theme.get("bg_card", "#FFFFFF"),
            }
    except Exception:
        pass
    return {"color_a": "#3498db", "color_b": "#e74c3c", "primary": "#3498db", "secondary": "#e74c3c", "bg_card": "#FFFFFF"}


class ABPlotter:
    """AB测试专用图表绘制器"""

    @staticmethod
    def _get_colors():
        return _get_theme_colors()

    @staticmethod
    def mean_comparison_bar(
        mean_a: float, mean_b: float,
        std_a: float, std_b: float,
        label_a: str = "对照组(A)", label_b: str = "实验组(B)",
        metric_name: str = "指标值",
        ci_a: Optional[Tuple[float, float]] = None,
        ci_b: Optional[Tuple[float, float]] = None,
    ) -> plt.Figure:
        """绘制均值比较柱状图(含误差线)"""
        colors = _get_theme_colors()
        fig, ax = plt.subplots(figsize=(8, 6))
        groups = [label_a, label_b]
        means = [mean_a, mean_b]
        errors = [std_a, std_b]
        bar_colors = [colors["color_a"], colors["color_b"]]

        bars = ax.bar(groups, means, yerr=errors, color=bar_colors, alpha=0.8,
                     edgecolor="white", linewidth=1.5, capsize=10,
                     error_kw={"elinewidth": 2, "ecolor": "gray"})

        for bar, mean in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errors[0]*0.1,
                   f"{mean:.2f}", ha="center", va="bottom", fontsize=12, fontweight="bold")

        lift_pct = ((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0
        ax.text(0.5, 0.97, f"提升: {lift_pct:+.2f}%", transform=ax.transAxes,
               ha="center", fontsize=12, fontweight="bold",
               color="green" if lift_pct > 0 else "red",
               bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f"{metric_name} - AB组均值比较", fontsize=14, fontweight="bold")
        ax.grid(True, axis="y", alpha=0.3)

        if ci_a:
            ax.plot([0, 0], [ci_a[0], ci_a[1]], "k-", linewidth=2)
            ax.plot([-0.1, 0.1], [ci_a[0], ci_a[0]], "k-", linewidth=1)
            ax.plot([-0.1, 0.1], [ci_a[1], ci_a[1]], "k-", linewidth=1)
        if ci_b:
            ax.plot([1, 1], [ci_b[0], ci_b[1]], "k-", linewidth=2)
            ax.plot([0.9, 1.1], [ci_b[0], ci_b[0]], "k-", linewidth=1)
            ax.plot([0.9, 1.1], [ci_b[1], ci_b[1]], "k-", linewidth=1)

        plt.tight_layout()
        return fig

    @staticmethod
    def distribution_comparison(
        group_a: np.ndarray, group_b: np.ndarray,
        label_a: str = "对照组(A)", label_b: str = "实验组(B)",
        metric_name: str = "指标值",
    ) -> plt.Figure:
        """绘制两组分布对比图(直方图+密度曲线)"""
        colors = _get_theme_colors()
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        clean_a = group_a[~np.isnan(group_a)]
        clean_b = group_b[~np.isnan(group_b)]

        ax = axes[0]
        ax.hist(clean_a, bins=30, alpha=0.6, color=colors["color_a"],
               label=label_a, density=True, edgecolor="white")
        ax.hist(clean_b, bins=30, alpha=0.6, color=colors["color_b"],
               label=label_b, density=True, edgecolor="white")
        ax.set_title(f"{metric_name} 分布直方图", fontsize=13, fontweight="bold")
        ax.set_xlabel(metric_name)
        ax.set_ylabel("密度")
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        bp = ax.boxplot([clean_a, clean_b], labels=[label_a, label_b],
                       patch_artist=True)
        bp["boxes"][0].set_facecolor(colors["color_a"])
        bp["boxes"][0].set_alpha(0.7)
        bp["boxes"][1].set_facecolor(colors["color_b"])
        bp["boxes"][1].set_alpha(0.7)
        ax.set_title(f"{metric_name} 箱线图", fontsize=13, fontweight="bold")
        ax.set_ylabel(metric_name)
        ax.grid(True, axis="y", alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def conversion_rate_comparison(
        rate_a: float, rate_b: float,
        n_a: int, n_b: int,
        label_a: str = "对照组(A)", label_b: str = "实验组(B)",
    ) -> plt.Figure:
        """绘制转化率比较图"""
        colors = _get_theme_colors()
        fig, ax = plt.subplots(figsize=(8, 5))

        groups = [label_a, label_b]
        rates = [rate_a, rate_b]

        se_a = np.sqrt(rate_a * (1 - rate_a) / n_a) if n_a > 0 else 0
        se_b = np.sqrt(rate_b * (1 - rate_b) / n_b) if n_b > 0 else 0

        bar_colors = [colors["color_a"], colors["color_b"]]
        bars = ax.bar(groups, rates, color=bar_colors, alpha=0.8,
                     edgecolor="white", linewidth=2)

        ax.errorbar(groups, rates, yerr=[se_a, se_b], fmt="none",
                   ecolor="gray", capsize=8, linewidth=2)

        for bar, rate in zip(bars, rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(se_a, se_b)*0.5,
                   f"{rate*100:.2f}%", ha="center", fontsize=13, fontweight="bold",
                   color=colors["primary"])

        abs_lift = rate_b - rate_a
        rel_lift = (abs_lift / rate_a * 100) if rate_a > 0 else 0
        ax.text(0.5, 0.97,
               f"绝对提升: {abs_lift*100:+.2f}%\n相对提升: {rel_lift:+.2f}%",
               transform=ax.transAxes, ha="center", fontsize=11,
               bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

        ax.set_ylabel("转化率", fontsize=12)
        ax.set_title("转化率比较", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(rates) * 1.3)
        ax.grid(True, axis="y", alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def confidence_interval_plot(
        diff: float, ci_lower: float, ci_upper: float,
        alpha: float = 0.05,
    ) -> plt.Figure:
        """绘制效应量置信区间图"""
        colors = _get_theme_colors()
        fig, ax = plt.subplots(figsize=(10, 3))

        ax.axvline(x=0, color="black", linestyle="-", linewidth=2, label="零效应线")
        ax.axvline(x=diff, color=colors["color_b"], linestyle="--", linewidth=2, label=f"观测差异: {diff:.4f}")

        ax.plot([ci_lower, ci_upper], [0, 0], "b-", linewidth=3, label=f"{int((1-alpha)*100)}%置信区间")
        ax.scatter([ci_lower, ci_upper], [0, 0], color="blue", s=80, zorder=5)

        ax.annotate(f"{ci_lower:.4f}", xy=(ci_lower, 0), xytext=(ci_lower, -0.5),
                   ha="center", fontsize=10)
        ax.annotate(f"{ci_upper:.4f}", xy=(ci_upper, 0), xytext=(ci_upper, -0.5),
                   ha="center", fontsize=10)

        if ci_lower > 0 or ci_upper < 0:
            ax.text(0.5, 0.5, "[SIG] 统计显著 (区间不包含0)", transform=ax.transAxes,
                   ha="center", va="center", fontsize=12, fontweight="bold", color="green")
        else:
            ax.text(0.5, 0.5, "[NS] 不显著 (区间包含0)", transform=ax.transAxes,
                   ha="center", va="center", fontsize=12, fontweight="bold", color="red")

        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.set_xlabel("效应量 (B组 - A组)", fontsize=12)
        ax.set_title(f"效应量及{(1-alpha)*100:.0f}%置信区间", fontsize=14, fontweight="bold")
        ax.legend(loc="upper right")
        ax.grid(True, axis="x", alpha=0.3)

        plt.tight_layout()
        return fig

    @staticmethod
    def power_curve(
        baseline_rate: float = 0.10,
        max_effect: float = 0.05,
        n_per_group: int = 1000,
        alpha: float = 0.05,
    ) -> go.Figure:
        """绘制统计功效曲线"""
        from scipy import stats as scipy_stats
        colors = _get_theme_colors()

        effects = np.linspace(0, max_effect, 50)
        powers = []

        for effect in effects:
            if effect == 0:
                powers.append(alpha)
                continue
            p1 = baseline_rate
            p2 = baseline_rate + effect
            p_bar = (p1 + p2) / 2
            se = np.sqrt(2 * p_bar * (1 - p_bar) / n_per_group)
            z_alpha = scipy_stats.norm.ppf(1 - alpha/2)
            z_power = (effect / se) - z_alpha
            power = scipy_stats.norm.cdf(z_power)
            powers.append(power)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=effects, y=powers,
            mode="lines+markers",
            name="功效曲线",
            line=dict(color=colors["color_b"], width=2),
            marker=dict(size=6),
        ))

        fig.add_hline(y=0.80, line_dash="dash", line_color="green",
                     annotation_text="80%功效线")

        fig.update_layout(
            title=f"统计功效曲线 (n={n_per_group}/组)",
            xaxis_title="最小可检测效应 (绝对差值)",
            yaxis_title="统计功效 (1-β)",
            template="plotly_white",
            height=400,
        )

        return fig

    @staticmethod
    def cumulative_lift_plot(
        data_a: np.ndarray, data_b: np.ndarray,
        metric_name: str = "指标",
    ) -> go.Figure:
        """绘制累积提升图 (随时间/样本量的累积效应)"""
        colors = _get_theme_colors()
        n = min(len(data_a), len(data_b))
        cumulative_lifts = []

        for i in range(1, n+1):
            mean_a = np.mean(data_a[:i])
            mean_b = np.mean(data_b[:i])
            lift = ((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0
            cumulative_lifts.append(lift)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, n+1)), y=cumulative_lifts,
            mode="lines",
            name="累积提升",
            line=dict(color=colors["color_b"], width=2),
            fill="tozeroy",
            fillcolor="rgba(231, 76, 60, 0.1)",
        ))

        fig.add_hline(y=0, line_dash="solid", line_color="gray")

        fig.update_layout(
            title=f"{metric_name} 累积提升趋势",
            xaxis_title="样本量",
            yaxis_title="累积提升 (%)",
            template="plotly_white",
            height=400,
        )

        return fig
