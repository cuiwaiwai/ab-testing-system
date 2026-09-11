# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 描述统计模块
'''

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ab_calculator import ABCalculator
from utils.plots_ab import ABPlotter
from utils.font_setup import setup_chinese_font

setup_chinese_font()


def render_descriptive():
    '''渲染描述性统计页面'''
    st.header('📊 描述性统计')

    if st.session_state.ab_data is None:
        st.warning('⚠️ 请先在「数据导入」页面加载数据')
        return

    df = st.session_state.ab_data

    # 选择分组列
    possible_group_cols = []
    for col in df.columns:
        if df[col].nunique() == 2:
            possible_group_cols.append(col)
        elif df[col].nunique() <= 5:
            possible_group_cols.append(col)

    if not possible_group_cols:
        st.error('未检测到合适的分组列')
        return

    group_col = st.selectbox('选择分组列', possible_group_cols, key='ab_group_col')
    groups = df[group_col].unique()
    if len(groups) != 2:
        st.warning('请选择一个恰好2个类别的分组列')
        return

    group_a_val, group_b_val = groups[0], groups[1]

    # 分组基本统计
    st.markdown('<div class="output-highlight"><div class="output-label">📊 分组概况</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        n_a = (df[group_col] == group_a_val).sum()
        n_b = (df[group_col] == group_b_val).sum()
        st.metric(f'{group_a_val} 组样本量', f'{n_a:,}')
    with col2:
        st.metric(f'{group_b_val} 组样本量', f'{n_b:,}')
    with col3:
        st.metric('总样本量', f'{n_a+n_b:,}')

    st.markdown("</div>", unsafe_allow_html=True)
    df_a = df[df[group_col] == group_a_val]
    df_b = df[df[group_col] == group_b_val]

    # 数值型指标描述统计
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != group_col and df[c].nunique() > 2]

    if numeric_cols:
        st.subheader('📊 数值型指标描述统计')

        metric = st.selectbox('选择分析指标', numeric_cols, key='desc_metric')

        data_a = df_a[metric].dropna().values
        data_b = df_b[metric].dropna().values

        col1, col2, col3, col4, col5 = st.columns(5)
        stats_a = {
            '样本量': len(data_a),
            '均值': np.mean(data_a),
            '标准差': np.std(data_a, ddof=1),
            '中位数': np.median(data_a),
            'IQR': np.percentile(data_a, 75) - np.percentile(data_a, 25),
        }
        stats_b = {
            '样本量': len(data_b),
            '均值': np.mean(data_b),
            '标准差': np.std(data_b, ddof=1),
            '中位数': np.median(data_b),
            'IQR': np.percentile(data_b, 75) - np.percentile(data_b, 25),
        }

        stat_labels = ['样本量', '均值', '标准差', '中位数', 'IQR']
        for col, label in zip([col1, col2, col3, col4, col5], stat_labels):
            with col:
                st.metric(f'{label}', f'{stats_a[label]:.2f}')
                st.caption(f'{group_a_val}')
                st.metric(f'{label}', f'{stats_b[label]:.2f}')
                st.caption(f'{group_b_val}')

        # 分布对比图
        st.subheader(f'📈 {metric} 分布对比')
        fig = ABPlotter.distribution_comparison(
            data_a, data_b,
            label_a=str(group_a_val), label_b=str(group_b_val),
            metric_name=metric
        )
        st.pyplot(fig)
        plt.close()

    # 分类型指标
    cat_cols = [c for c in df.columns if c not in numeric_cols and c != group_col]
    if cat_cols:
        st.subheader('📊 分类指标对比')
        cat_metric = st.selectbox('选择分类指标', cat_cols, key='cat_metric')

        ct_a = df_a[cat_metric].value_counts()
        ct_b = df_b[cat_metric].value_counts()

        ct_df = pd.DataFrame({
            f'{group_a_val} (频数)': ct_a,
            f'{group_a_val} (%)': (ct_a / n_a * 100).round(2),
            f'{group_b_val} (频数)': ct_b,
            f'{group_b_val} (%)': (ct_b / n_b * 100).round(2),
        }).fillna(0)
        st.dataframe(ct_df, use_container_width=True)

    # 转化率分析
    conversion_cols = [c for c in numeric_cols if set(df[c].dropna().unique()).issubset({0, 1})]
    if conversion_cols:
        st.markdown('<div class="output-highlight"><div class="output-label">📊 转化率对比</div>', unsafe_allow_html=True)
        conv_col = st.selectbox('选择转化指标 (0/1)', conversion_cols, key='conv_metric')

        rate_a = df_a[conv_col].mean()
        rate_b = df_b[conv_col].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f'{group_a_val} 转化率', f'{rate_a*100:.2f}%')
        with col2:
            st.metric(f'{group_b_val} 转化率', f'{rate_b*100:.2f}%')
        with col3:
            lift = ((rate_b - rate_a) / rate_a * 100) if rate_a > 0 else 0
            st.metric('相对提升', f'{lift:+.2f}%')

        fig = ABPlotter.conversion_rate_comparison(
            rate_a, rate_b, n_a, n_b,
            label_a=str(group_a_val), label_b=str(group_b_val)
        )
        st.pyplot(fig)
        plt.close()
        st.markdown("</div>", unsafe_allow_html=True)
