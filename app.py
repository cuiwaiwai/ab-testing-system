# -*- coding: utf-8 -*-
"""
A/B测试实验设计与分析系统 V2.0
AB Testing Experiment Design & Analysis System

功能概述：
    本系统是一个专业的A/B测试实验设计与分析工具，覆盖从实验设计、
    数据导入、描述统计、假设检验到决策建议的完整工作流。

主要功能模块：
    1. 实验设计 - 样本量计算(比例型/均值型)、功效分析
    2. 数据导入 - 多格式数据上传、示例数据生成、手动输入
    3. 描述统计 - 分组描述分析、分布对比、转化率对比
    4. 假设检验 - t检验、比例Z检验、卡方检验、Mann-Whitney U检验
    5. 结果可视化 - 分布图、均值比较、累积提升、置信区间
    6. 决策建议 - 基于显著性和效应量的四象限决策框架

新增功能 (V2.0):
    - 7套自定义配色方案（多巴胺/莫兰迪/清新绿/粉/紫/黑/白）
    - 窄化侧边栏设计
    - 输出区域鲜明提示
    - 首页详细理论介绍与方法选择指南

技术栈:
    - Python 3.8+
    - Streamlit (Web框架)
    - Pandas, NumPy (数据处理)
    - Matplotlib, Seaborn, Plotly (可视化)
    - SciPy (统计检验)

适用场景:
    - 互联网产品AB测试分析
    - 市场营销实验评估
    - 用户体验优化决策
    - 统计学教学演示

开发者：应用统计专业
版本：V2.0
"""

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.experiment_design import render_experiment_design
from modules.data_import import render_data_import
from modules.descriptive import render_descriptive
from modules.hypothesis_test import render_hypothesis_test
from modules.visualization import render_visualization
from modules.decision import render_decision


# ======================== 配色方案定义 ========================
COLOR_THEMES = {
    "🎨 多巴胺色系": {
        "primary": "#FF6B6B",
        "primary_light": "#FF8E8E",
        "secondary": "#4ECDC4",
        "accent": "#FFE66D",
        "accent2": "#A8E6CF",
        "bg_main": "#FFF5F5",
        "bg_card": "#FFFFFF",
        "sidebar_bg": "#2C3E50",
        "sidebar_text": "#ECF0F1",
        "sidebar_active": "#FF6B6B",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "border": "#FF6B6B",
        "success": "#27AE60",
        "warning": "#F39C12",
        "error": "#E74C3C",
        "info": "#3498DB",
        "metric_bg": "#FFF0F0",
        "output_bg": "#FFF8F0",
        "output_border": "#FF6B6B",
        "output_icon": "🔥",
        "chart_a": "#FF6B6B",
        "chart_b": "#4ECDC4",
        "desc": "高饱和撞色，活力四射，适合教学演示场景",
    },
    "🖌️ 莫兰迪色系": {
        "primary": "#C4A484",
        "primary_light": "#D4B896",
        "secondary": "#A8B5A0",
        "accent": "#B8A9C9",
        "accent2": "#D4C5B9",
        "bg_main": "#F5F0EB",
        "bg_card": "#FAF7F4",
        "sidebar_bg": "#6B5B4F",
        "sidebar_text": "#E8DDD4",
        "sidebar_active": "#C4A484",
        "text_primary": "#4A3728",
        "text_secondary": "#8B7D6B",
        "border": "#C4A484",
        "success": "#8FBC8F",
        "warning": "#D4A76A",
        "error": "#C4887C",
        "info": "#8FAABF",
        "metric_bg": "#F0EBE3",
        "output_bg": "#F8F4EF",
        "output_border": "#C4A484",
        "output_icon": "🎨",
        "chart_a": "#C4A484",
        "chart_b": "#A8B5A0",
        "desc": "低饱和高级灰调，温润优雅，适合正式报告场景",
    },
    "🌿 绿色清新色系": {
        "primary": "#27AE60",
        "primary_light": "#58D68D",
        "secondary": "#2ECC71",
        "accent": "#A8E6CF",
        "accent2": "#D5F5E3",
        "bg_main": "#F0FFF4",
        "bg_card": "#FFFFFF",
        "sidebar_bg": "#1E8449",
        "sidebar_text": "#D5F5E3",
        "sidebar_active": "#2ECC71",
        "text_primary": "#1A5C2A",
        "text_secondary": "#6B8E6B",
        "border": "#27AE60",
        "success": "#27AE60",
        "warning": "#F4D03F",
        "error": "#E74C3C",
        "info": "#3498DB",
        "metric_bg": "#E8F8F0",
        "output_bg": "#F4FEF8",
        "output_border": "#27AE60",
        "output_icon": "🌱",
        "chart_a": "#27AE60",
        "chart_b": "#3498DB",
        "desc": "自然清新绿调，护眼舒适，适合长时间使用",
    },
    "💗 粉色纯色": {
        "primary": "#E91E63",
        "primary_light": "#F06292",
        "secondary": "#EC407A",
        "accent": "#FCE4EC",
        "accent2": "#F8BBD0",
        "bg_main": "#FFF5F7",
        "bg_card": "#FFFFFF",
        "sidebar_bg": "#AD1457",
        "sidebar_text": "#FCE4EC",
        "sidebar_active": "#F06292",
        "text_primary": "#880E4F",
        "text_secondary": "#C2185B",
        "border": "#E91E63",
        "success": "#66BB6A",
        "warning": "#FFA726",
        "error": "#EF5350",
        "info": "#42A5F5",
        "metric_bg": "#FCE4EC",
        "output_bg": "#FFF0F5",
        "output_border": "#E91E63",
        "output_icon": "💗",
        "chart_a": "#E91E63",
        "chart_b": "#7B1FA2",
        "desc": "柔和粉色主调，温暖亲和，适合展示型报告",
    },
    "💜 紫色纯色": {
        "primary": "#7B1FA2",
        "primary_light": "#AB47BC",
        "secondary": "#9C27B0",
        "accent": "#E1BEE7",
        "accent2": "#CE93D8",
        "bg_main": "#FDF5FF",
        "bg_card": "#FFFFFF",
        "sidebar_bg": "#4A148C",
        "sidebar_text": "#E1BEE7",
        "sidebar_active": "#AB47BC",
        "text_primary": "#4A148C",
        "text_secondary": "#7B1FA2",
        "border": "#7B1FA2",
        "success": "#66BB6A",
        "warning": "#FFA726",
        "error": "#EF5350",
        "info": "#42A5F5",
        "metric_bg": "#F3E5F5",
        "output_bg": "#FAF0FF",
        "output_border": "#7B1FA2",
        "output_icon": "💜",
        "chart_a": "#7B1FA2",
        "chart_b": "#E91E63",
        "desc": "深邃紫色主调，科技感强，适合数据科学场景",
    },
    "🖤 黑色纯色": {
        "primary": "#1A1A1A",
        "primary_light": "#444444",
        "secondary": "#333333",
        "accent": "#888888",
        "accent2": "#CCCCCC",
        "bg_main": "#FAFAFA",
        "bg_card": "#FFFFFF",
        "sidebar_bg": "#111111",
        "sidebar_text": "#CCCCCC",
        "sidebar_active": "#666666",
        "text_primary": "#111111",
        "text_secondary": "#666666",
        "border": "#333333",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#2196F3",
        "metric_bg": "#F5F5F5",
        "output_bg": "#F8F8F8",
        "output_border": "#333333",
        "output_icon": "🖤",
        "chart_a": "#333333",
        "chart_b": "#888888",
        "desc": "经典黑白极简，专业严谨，适合企业级应用",
    },
    "🤍 白色纯色": {
        "primary": "#6C757D",
        "primary_light": "#ADB5BD",
        "secondary": "#495057",
        "accent": "#DEE2E6",
        "accent2": "#E9ECEF",
        "bg_main": "#FFFFFF",
        "bg_card": "#F8F9FA",
        "sidebar_bg": "#E9ECEF",
        "sidebar_text": "#495057",
        "sidebar_active": "#6C757D",
        "text_primary": "#212529",
        "text_secondary": "#6C757D",
        "border": "#DEE2E6",
        "success": "#28A745",
        "warning": "#FFC107",
        "error": "#DC3545",
        "info": "#17A2B8",
        "metric_bg": "#F8F9FA",
        "output_bg": "#FAFAFA",
        "output_border": "#DEE2E6",
        "output_icon": "🤍",
        "chart_a": "#6C757D",
        "chart_b": "#17A2B8",
        "desc": "纯净简约白调，干净清爽，适合日常办公场景",
    },
}


# ======================== 会话初始化 ========================
def init_session():
    if "ab_data" not in st.session_state:
        st.session_state.ab_data = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 首页"
    if "color_theme" not in st.session_state:
        st.session_state.color_theme = "🎨 多巴胺色系"


def get_theme():
    return COLOR_THEMES[st.session_state.color_theme]


# ======================== CSS注入 ========================
def inject_theme_css():
    theme = get_theme()
    css = f"""
    <style>
    /* ===== 全局CSS变量 ===== */
    :root {{
        --primary: {theme["primary"]};
        --primary-light: {theme["primary_light"]};
        --secondary: {theme["secondary"]};
        --accent: {theme["accent"]};
        --bg-main: {theme["bg_main"]};
        --bg-card: {theme["bg_card"]};
        --sidebar-bg: {theme["sidebar_bg"]};
        --sidebar-text: {theme["sidebar_text"]};
        --text-primary: {theme["text_primary"]};
        --text-secondary: {theme["text_secondary"]};
        --border: {theme["border"]};
        --output-bg: {theme["output_bg"]};
        --output-border: {theme["output_border"]};
    }}

    /* ===== 侧边栏缩窄为约2cm(160px) ===== */
    [data-testid="stSidebar"] {{
        min-width: 170px !important;
        max-width: 170px !important;
        width: 170px !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding: 0.5rem 0.3rem !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        font-size: 11px !important;
        padding: 0.3rem 0.2rem !important;
        margin-bottom: 2px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    [data-testid="stSidebar"] h2 {{
        font-size: 13px !important;
    }}
    [data-testid="stSidebar"] p {{
        font-size: 10px !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label {{
        font-size: 11px !important;
    }}

    /* ===== 全局主背景 ===== */
    .stApp {{
        background-color: {theme["bg_main"]};
    }}

    /* ===== 主页标题区 ===== */
    .hero-section {{
        background: linear-gradient(135deg, {theme["primary"]}15, {theme["secondary"]}15);
        border-radius: 16px;
        padding: 35px 30px;
        margin-bottom: 25px;
        border: 2px solid {theme["border"]}30;
        text-align: center;
    }}

    /* ===== 输出高亮区域框 ===== */
    .output-highlight {{
        background: {theme["output_bg"]};
        border: 2px solid {theme["output_border"]};
        border-left: 5px solid {theme["output_border"]};
        border-radius: 10px;
        padding: 20px 25px;
        margin: 18px 0;
        position: relative;
    }}
    .output-highlight::before {{
        content: "{theme['output_icon']}";
        position: absolute;
        top: -14px;
        left: 15px;
        font-size: 24px;
    }}
    .output-highlight .output-label {{
        font-weight: bold;
        font-size: 14px;
        color: {theme["primary"]};
        margin-bottom: 8px;
        padding-top: 5px;
    }}

    /* ===== 首页功能卡片 ===== */
    .feature-card {{
        background: {theme["bg_card"]};
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid {theme["border"]}20;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .feature-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }}

    /* ===== 提示框样式 ===== */
    .tip-box {{
        background: {theme["accent"]}30;
        border-left: 4px solid {theme["primary"]};
        border-radius: 8px;
        padding: 12px 18px;
        margin: 12px 0;
        font-size: 14px;
    }}

    /* ===== 方法指南表格 ===== */
    .guide-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 14px;
    }}
    .guide-table th {{
        background: {theme["primary"]};
        color: white;
        padding: 12px 15px;
        text-align: left;
    }}
    .guide-table td {{
        padding: 10px 15px;
        border-bottom: 1px solid {theme["border"]}30;
    }}
    .guide-table tr:hover td {{
        background: {theme["accent"]}20;
    }}

    /* ===== 页面头部 ===== */
    h1 {{ color: {theme["primary"]} !important; }}
    h2 {{ color: {theme["text_primary"]} !important; }}
    h3 {{ color: {theme["text_primary"]} !important; }}

    /* ===== 指标卡片 ===== */
    [data-testid="stMetric"] {{
        background: {theme["metric_bg"]} !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid {theme["border"]}20 !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {theme["primary"]} !important;
    }}

    /* ===== 主按钮 ===== */
    .stButton > button[kind="primary"] {{
        background-color: {theme["primary"]} !important;
        border-color: {theme["primary"]} !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: {theme["primary_light"]} !important;
    }}

    /* ===== 分割线 ===== */
    hr {{
        border-color: {theme["border"]}30 !important;
    }}

    /* ===== Radio按钮选中态 ===== */
    .stRadio [data-checked="true"] {{
        color: {theme["primary"]} !important;
    }}

    /* ===== 侧边栏本体 ===== */
    [data-testid="stSidebar"] {{
        background-color: {theme["sidebar_bg"]} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {theme["sidebar_text"]} !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background-color: transparent !important;
        border: 1px solid {theme["sidebar_text"]}30 !important;
        color: {theme["sidebar_text"]} !important;
    }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background-color: {theme["sidebar_active"]} !important;
        border-color: {theme["sidebar_active"]} !important;
        color: white !important;
    }}

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar-thumb {{
        background: {theme["primary"]}50;
        border-radius: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {theme["bg_main"]};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ======================== 首页 ========================
def render_home():
    theme = get_theme()
    st.markdown(f"""
    <div class="hero-section">
        <h1 style="font-size: 2.5rem; color: {theme['primary']}; margin-bottom: 10px;">
            {theme['output_icon']} A/B测试实验设计与分析系统
        </h1>
        <p style="font-size: 1.2rem; color: {theme['text_secondary']};">
            AB Testing Experiment Design & Analysis System V2.0
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- 工作流程图 ----
    st.markdown(f"""
    <div style="background: {theme['bg_card']}; border-radius: 12px; padding: 25px; margin: 20px 0; border: 1px solid {theme['border']}30;">
        <h3 style="text-align: center; margin-bottom: 15px; color: {theme['text_primary']};">🔄 A/B测试标准工作流程</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px;">
            <div style="background: {theme['accent']}30; border-radius: 8px; padding: 15px; text-align: center; min-width: 100px;">
                <p style="font-size: 24px;">🎯</p>
                <p style="font-weight: bold;">实验设计</p>
                <p style="font-size: 12px; color: {theme['text_secondary']};">样本量计算</p>
            </div>
            <p style="font-size: 24px; color: {theme['border']}; align-self: center;">→</p>
            <div style="background: {theme['accent']}30; border-radius: 8px; padding: 15px; text-align: center; min-width: 100px;">
                <p style="font-size: 24px;">📥</p>
                <p style="font-weight: bold;">数据导入</p>
                <p style="font-size: 12px; color: {theme['text_secondary']};">多格式支持</p>
            </div>
            <p style="font-size: 24px; color: {theme['border']}; align-self: center;">→</p>
            <div style="background: {theme['accent']}30; border-radius: 8px; padding: 15px; text-align: center; min-width: 100px;">
                <p style="font-size: 24px;">🧪</p>
                <p style="font-weight: bold;">假设检验</p>
                <p style="font-size: 12px; color: {theme['text_secondary']};">多种检验方法</p>
            </div>
            <p style="font-size: 24px; color: {theme['border']}; align-self: center;">→</p>
            <div style="background: {theme['accent']}30; border-radius: 8px; padding: 15px; text-align: center; min-width: 100px;">
                <p style="font-size: 24px;">📊</p>
                <p style="font-weight: bold;">可视化</p>
                <p style="font-size: 12px; color: {theme['text_secondary']};">图表展示</p>
            </div>
            <p style="font-size: 24px; color: {theme['border']}; align-self: center;">→</p>
            <div style="background: {theme['accent']}30; border-radius: 8px; padding: 15px; text-align: center; min-width: 100px;">
                <p style="font-size: 24px;">📋</p>
                <p style="font-weight: bold;">决策建议</p>
                <p style="font-size: 12px; color: {theme['text_secondary']};">科学决策</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 数据状态提示 ----
    st.markdown(f"""
    <div class="output-highlight">
        <div class="output-label">📊 系统状态</div>
        <p style="margin: 0; color: {theme['text_primary']};">{'✅ 已加载数据: ' + str(st.session_state.ab_data.shape[0]) + ' 条记录' if st.session_state.ab_data is not None else '💡 请先通过左侧菜单「📥 数据导入」加载或生成数据，再使用分析功能'}</p>
    </div>
    """, unsafe_allow_html=True)

    # ==================== 详细理论介绍 ====================
    st.divider()
    st.subheader("📖 A/B测试核心理论详解")

    tabs = st.tabs([
        "📐 实验设计理论",
        "📊 假设检验理论",
        "📈 效应量与功效",
        "🔬 检验方法对比",
        "🎯 方法选择指南",
    ])

    # Tab 1: 实验设计理论
    with tabs[0]:
        st.markdown("""
        ### 📐 实验设计理论基础

        **1. 随机化 (Randomization)**
        
        随机化是A/B测试最核心的原则。将用户随机分配到对照组(A)和实验组(B)，确保两组在实验开始前
        在所有已知和未知的维度上**统计等价**。这样就排除了混淆变量的影响，任何观察到的结果差异
        都可以归因于实验变量。

        **2. 样本量计算**

        样本量由四个因素决定：
        - **显著性水平 α**：愿意接受的假阳性概率（通常取0.05）
        - **统计功效 1-β**：检测到真实效应的概率（通常取0.80）
        - **基准转化率/均值**：对照组的表现
        - **最小可检测效应 (MDE)**：希望检测到的最小差异

        **3. 控制变量法**

        实验过程中，**只有目标变量**发生变化，其他所有条件（流量来源、时间窗口、用户群体等）
        保持一致。这保证了观察到的差异能准确归因于实验变量。

        **4. 实验时长设计**

        - 至少覆盖 **1-2个完整的业务周期**（如周/月循环）
        - 考虑 **新奇效应** (Novelty Effect)：用户对新界面的短期好奇
        - 考虑 **首日效应** (Primacy Effect)：首次体验对后续行为的影响
        """)

    # Tab 2: 假设检验理论
    with tabs[1]:
        st.markdown("""
        ### 📊 假设检验理论基础

        **1. 原假设与备择假设**

        | 概念 | 定义 | 示例 |
        |------|------|------|
        | 原假设 H₀ | 两组没有差异 | "A组转化率 = B组转化率" |
        | 备择假设 H₁ | 两组存在差异 | "A组转化率 ≠ B组转化率" |

        **2. 两类错误**

        | 错误类型 | 定义 | 概率 | 后果 |
        |----------|------|------|------|
        | 第一类错误 (Type I) | H₀为真但被拒绝 | α (通常0.05) | 假阳性：误以为有效果 |
        | 第二类错误 (Type II) | H₁为真但未被拒绝 | β (通常0.20) | 假阴性：错过了真实效果 |

        **3. p值的正确理解**

        - p值是 **在原假设成立的前提下**，观察到当前结果（或更极端结果）的概率
        - p < 0.05 意味着：如果H₀为真，观察到这样差异的概率小于5%
        - ⚠️ p值 **不是** "H₁为真的概率"
        - ⚠️ p > 0.05 **不代表** "两组没有差异"，只能说不拒绝H₀

        **4. 置信区间**

        - 95%置信区间的含义：如果重复实验100次，大约95次计算出的区间包含真实值
        - 置信区间不包含0 → 差异在统计上显著
        - 置信区间的宽度反映了估计的精确度
        """)

    # Tab 3: 效应量与功效
    with tabs[2]:
        st.markdown("""
        ### 📈 效应量与统计功效

        **1. 统计显著性 ≠ 实际意义**

        在大样本下，微小的差异也可能达到统计显著，但这种差异可能缺乏业务价值。
        因此需要同时关注**效应量** (Effect Size)。

        **2. Cohen's d (标准化均值差)**

        | d值范围 | 效应大小 | 说明 |
        |---------|----------|------|
        | < 0.2 | 可忽略 | 差异几乎没有实际意义 |
        | 0.2 - 0.5 | 小效应 | 需在大样本下才能检测 |
        | 0.5 - 0.8 | 中等效应 | 有实际应用价值 |
        | > 0.8 | 大效应 | 差异非常明显 |

        **3. 统计功效 (Statistical Power)**

        - 功效 = 1 - β = 正确拒绝错误H₀的概率
        - 通常目标：80%功效
        - 影响功效的因素：样本量↑、效应量↑、α↑ → 功效↑
        - 功效不足 = 浪费资源（可能错过真实效果）

        **4. 功效分析实践**

        功效分析可以用于：
        - **先验分析**：实验前计算所需样本量（→ 实验设计模块）
        - **后验分析**：实验后评估结果的可靠性
        - **敏感性分析**：给定样本量，能检测到的最小效应
        """)

    # Tab 4: 检验方法对比
    with tabs[3]:
        st.markdown("""
        ### 🔬 检验方法详细对比

        | 检验方法 | 适用数据类型 | 假设条件 | 优势 | 局限 |
        |----------|------------|----------|------|------|
        | **两样本t检验** | 连续型指标 | 正态性、方差齐性(可选) | 统计功效高、经典方法 | 对异常值敏感 |
        | **Welch t检验** | 连续型指标 | 近似正态 | 不要求方差齐性 | 自由度需校正 |
        | **比例Z检验** | 二元指标(0/1) | 大样本(n>30) | 转化率分析标准方法 | 小样本不准 |
        | **卡方检验** | 分类变量 | 期望频数≥5 | 多类别比较、分布检验 | 仅判断是否有差异 |
        | **Mann-Whitney U** | 顺序/连续型 | 无分布假设 | 对异常值鲁棒 | 功效略低于t检验 |
        | **Bootstrap检验** | 任意类型 | 无分布假设 | 完全数据驱动 | 计算量大 |
        """)

    # Tab 5: 方法选择指南
    with tabs[4]:
        st.markdown("""
        ### 🎯 方法选择决策指南

        **按数据类型选择：**
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **连续型指标（如客单价、停留时长）**
            ```
            数据是否正态？
            ├── 是 → 两样本t检验 (Welch)
            └── 否 → Mann-Whitney U检验
                     或 Bootstrap检验
            ```
            """)
        with col2:
            st.markdown("""
            **比例型指标（如转化率、点击率）**
            ```
            样本量是否足够？
            ├── 是(n>30) → 比例Z检验
            └── 否 → Fisher精确检验
            ```

            **分类变量（如设备类型分布）**
            ```
            → 卡方检验
            ```
            """)

        st.markdown("""
        ---
        ### 📋 快速决策表

        | 你的数据长这样 | 用这个方法 | 关键判断依据 |
        |---------------|-----------|-------------|
        | 两组用户的购买金额 | 两样本t检验 / MWU | 先做正态性检验 |
        | 两组用户的转化(是/否) | 比例Z检验 | 样本量>30即可 |
        | 两组用户的设备分布 | 卡方检验 | 检查期望频数 |
        | 数据有很多异常值 | Mann-Whitney U | 非参数，不受影响 |
        | 不确定数据分布 | Bootstrap检验 | 万能但计算慢 |

        ---
        ### ⚠️ 常见误区提醒

        1. **不要偷看结果**：预设样本量，不到目标不停止实验
        2. **不要多重比较**：同时检验10个指标，至少1个会"显著"（纯属偶然）
        3. **不要忽略效应量**：p<0.05但效应量极小=无业务价值
        4. **不要混淆相关与因果**：AB测试通过随机化保证因果推断
        5. **不要过早全量**：先小流量验证，再逐步放量
        """)

    # ---- 关键概念速览 ----
    st.divider()
    st.subheader("📊 关键统计概念速查")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <h4>α (显著性水平)</h4>
            <p style="font-size:13px; color:{theme['text_secondary']};">犯第一类错误的概率<br>通常取0.05</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <h4>β (第二类错误)</h4>
            <p style="font-size:13px; color:{theme['text_secondary']};">漏报真实效应的概率<br>通常取0.20</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <h4>统计功效 (1-β)</h4>
            <p style="font-size:13px; color:{theme['text_secondary']};">检测到真实效应的能力<br>通常要求≥80%</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="feature-card">
            <h4>效应量 (Effect Size)</h4>
            <p style="font-size:13px; color:{theme['text_secondary']};">差异的实际大小<br>Cohen's d标准</p>
        </div>
        """, unsafe_allow_html=True)

    # ---- 底部 ----
    st.divider()
    st.caption("© 2024 A/B测试实验设计与分析系统 V2.0 | 应用统计专业")


# ======================== 侧边栏 ========================
def render_sidebar():
    theme = get_theme()
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <h3 style="color: {theme['sidebar_active']} !important; font-size: 13px; margin: 0;">
                🧪 AB测试
            </h3>
            <p style="color: {theme['sidebar_text']}80 !important; font-size: 9px; margin: 2px 0;">
                V2.0
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ---- 配色方案选择器 ----
        st.markdown(f"<p style='font-size:10px; color:{theme['sidebar_text']}80; margin:0;'>🎨 配色</p>", unsafe_allow_html=True)
        theme_choice = st.selectbox(
            "配色方案",
            list(COLOR_THEMES.keys()),
            index=list(COLOR_THEMES.keys()).index(st.session_state.color_theme),
            label_visibility="collapsed",
            key="theme_selector",
        )
        if theme_choice != st.session_state.color_theme:
            st.session_state.color_theme = theme_choice
            st.rerun()

        st.divider()

        # ---- 页面导航 ----
        pages = {
            "🏠 首页": "home",
            "🎯 实验设计": "design",
            "📥 数据导入": "import",
            "📊 描述统计": "descriptive",
            "🧪 假设检验": "hypothesis",
            "📈 可视化": "visualization",
            "📋 决策建议": "decision",
        }

        for label, key in pages.items():
            btn_type = "primary" if st.session_state.current_page == label else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state.current_page = label
                st.rerun()

        st.divider()

        if st.session_state.ab_data is not None:
            st.success("📊 数据已加载")
            if st.button("🗑️ 清除", use_container_width=True):
                st.session_state.ab_data = None
                st.rerun()

        st.caption(f"当前配色：{st.session_state.color_theme[:2]}")


# ======================== 主入口 ========================
def main():
    st.set_page_config(
        page_title="A/B测试实验设计与分析系统",
        page_icon="🧪",
        layout="wide",
    )

    init_session()
    inject_theme_css()
    render_sidebar()

    pages = {
        "🏠 首页": render_home,
        "🎯 实验设计": render_experiment_design,
        "📥 数据导入": render_data_import,
        "📊 描述统计": render_descriptive,
        "🧪 假设检验": render_hypothesis_test,
        "📈 可视化": render_visualization,
        "📋 决策建议": render_decision,
    }

    current = st.session_state.current_page
    if current in pages:
        pages[current]()


if __name__ == "__main__":
    main()
