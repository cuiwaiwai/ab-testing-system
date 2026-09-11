# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 结果可视化模块
'''

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.plots_ab import ABPlotter

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def render_visualization():
    '''渲染可视化页面'''
    st.header('📈 结果可视化')

    if st.session_state.ab_data is None:
        st.warning('⚠️ 请先在「数据导入」页面加载数据')
        return

    df = st.session_state.ab_data

    possible_group_cols = [c for c in df.columns if df[c].nunique() == 2]
    if not possible_group_cols:
        st.error('未检测到分组列')
        return

    group_col = st.selectbox('选择分组列', possible_group_cols, key='viz_group')
    groups = sorted(df[group_col].unique())

    df_a = df[df[group_col] == groups[0]]
    df_b = df[df[group_col] == groups[1]]

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != group_col and df[c].nunique() > 2]

    viz_type = st.radio(
        '图表类型',
        ['分布对比', '均值比较', '累积提升', '转化率对比'],
        horizontal=True
    )

    st.divider()

    if viz_type == '分布对比':
        metric = st.selectbox('选择指标', numeric_cols, key='viz_dist_metric')

        data_a = df_a[metric].dropna().values
        data_b = df_b[metric].dropna().values

        fig = ABPlotter.distribution_comparison(
            data_a, data_b,
            label_a=groups[0], label_b=groups[1],
            metric_name=metric
        )
        st.pyplot(fig)
        plt.close()

        # 累计分布函数对比
        st.subheader('累积分布函数 (CDF) 对比')
        import plotly.graph_objects as go

        fig_cdf = go.Figure()
        for data, name, color in [(data_a, groups[0], ABPlotter._get_colors()["color_a"]), (data_b, groups[1], ABPlotter._get_colors()["color_b"])]:
            sorted_data = np.sort(data)
            cdf = np.arange(1, len(sorted_data)+1) / len(sorted_data)
            fig_cdf.add_trace(go.Scatter(
                x=sorted_data, y=cdf, mode='lines', name=str(name),
                line=dict(color=color, width=2)
            ))

        fig_cdf.update_layout(
            title=f'{metric} 累积分布函数对比',
            xaxis_title=metric, yaxis_title='累积概率',
            template='plotly_white', height=400
        )
        st.plotly_chart(fig_cdf, use_container_width=True)

    elif viz_type == '均值比较':
        metric = st.selectbox('选择指标', numeric_cols, key='viz_mean_metric')

        mean_a = np.mean(df_a[metric].dropna())
        mean_b = np.mean(df_b[metric].dropna())
        std_a = np.std(df_a[metric].dropna(), ddof=1)
        std_b = np.std(df_b[metric].dropna(), ddof=1)

        fig = ABPlotter.mean_comparison_bar(
            mean_a, mean_b, std_a, std_b,
            label_a=groups[0], label_b=groups[1],
            metric_name=metric
        )
        st.pyplot(fig)
        plt.close()

    elif viz_type == '累积提升':
        metric = st.selectbox('选择指标', numeric_cols, key='viz_cum_metric')

        data_a = df_a[metric].dropna().values
        data_b = df_b[metric].dropna().values

        fig = ABPlotter.cumulative_lift_plot(data_a, data_b, metric_name=metric)
        st.plotly_chart(fig, use_container_width=True)

        st.caption('累积提升图展示随着样本量增加，两组间差异的稳定性变化趋势')

    elif viz_type == '转化率对比':
        conversion_cols = [c for c in numeric_cols if set(df[c].dropna().unique()).issubset({0, 1})]

        if not conversion_cols:
            st.warning('未检测到0/1转化指标')
            return

        metric = st.selectbox('选择转化指标', conversion_cols, key='viz_conv_metric')
        rate_a = df_a[metric].mean()
        rate_b = df_b[metric].mean()

        fig = ABPlotter.conversion_rate_comparison(
            rate_a, rate_b, len(df_a), len(df_b),
            label_a=groups[0], label_b=groups[1]
        )
        st.pyplot(fig)
        plt.close()
