# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 高级检验模块
功能：Bootstrap检验、方差分析(ANOVA)、序贯检验、多重比较校正
'''
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from typing import Dict, Any, Tuple, List, Optional


class AdvancedTests:
    '''高级统计检验方法'''

    @staticmethod
    def bootstrap_test(
        group_a: np.ndarray,
        group_b: np.ndarray,
        n_bootstrap: int = 10000,
        statistic: str = 'mean',
        alpha: float = 0.05,
        seed: int = 42
    ) -> Dict[str, Any]:
        '''Bootstrap假设检验
        非参数方法，不对数据分布做假设
        '''
        np.random.seed(seed)
        clean_a = group_a[~np.isnan(group_a)]
        clean_b = group_b[~np.isnan(group_b)]

        if statistic == 'mean':
            observed_diff = np.mean(clean_b) - np.mean(clean_a)
        elif statistic == 'median':
            observed_diff = np.median(clean_b) - np.median(clean_a)
        else:
            observed_diff = np.mean(clean_b) - np.mean(clean_a)

        # 合并后Bootstrap
        combined = np.concatenate([clean_a, clean_b])
        n_a = len(clean_a)
        boot_diffs = np.zeros(n_bootstrap)

        for i in range(n_bootstrap):
            np.random.shuffle(combined)
            boot_a = combined[:n_a]
            boot_b = combined[n_a:]

            if statistic == 'mean':
                boot_diffs[i] = np.mean(boot_b) - np.mean(boot_a)
            elif statistic == 'median':
                boot_diffs[i] = np.median(boot_b) - np.median(boot_a)
            else:
                boot_diffs[i] = np.mean(boot_b) - np.mean(boot_a)

        # 双侧p值
        p_value = np.mean(np.abs(boot_diffs) >= np.abs(observed_diff))

        # Bootstrap置信区间 (百分位法)
        ci_lower = np.percentile(boot_diffs, alpha/2 * 100)
        ci_upper = np.percentile(boot_diffs, (1 - alpha/2) * 100)

        significant = p_value < alpha

        return {
            '检验方法': 'Bootstrap检验',
            'Bootstrap次数': n_bootstrap,
            '统计量类型': statistic,
            '观测差异': round(float(observed_diff), 4),
            'p值': round(float(p_value), 6),
            '显著性水平': alpha,
            '是否显著': '是' if significant else '否',
            f'{int((1-alpha)*100)}%置信区间': (round(float(ci_lower), 4), round(float(ci_upper), 4)),
            '结论': f'差异{"显著" if significant else "不显著"} (Bootstrap p={p_value:.4f})'
        }

    @staticmethod
    def one_way_anova(
        groups: Dict[str, np.ndarray],
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        '''单因素方差分析
        用于比较三个及以上组的均值差异
        '''
        values = []
        labels = []
        for name, data in groups.items():
            clean = data[~np.isnan(data)]
            values.append(clean)
            labels.extend([name] * len(clean))

        if len(groups) < 2:
            return {'错误': '至少需要两组数据'}

        # ANOVA
        f_stat, p_value = scipy_stats.f_oneway(*values)

        # 效应量 η² (Eta-squared)
        all_values = np.concatenate(values)
        grand_mean = np.mean(all_values)
        ss_total = np.sum((all_values - grand_mean)**2)
        ss_between = sum(
            len(v) * (np.mean(v) - grand_mean)**2 for v in values
        )
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        significant = p_value < alpha

        # 组统计
        group_stats = {}
        for name, data in groups.items():
            clean = data[~np.isnan(data)]
            group_stats[name] = {
                '样本量': len(clean),
                '均值': round(float(np.mean(clean)), 4),
                '标准差': round(float(np.std(clean, ddof=1)), 4)
            }

        return {
            '检验方法': '单因素方差分析(One-Way ANOVA)',
            'F统计量': round(float(f_stat), 4),
            'p值': round(float(p_value), 6),
            '显著性水平': alpha,
            '是否显著': '是' if significant else '否',
            '效应量(η²)': round(float(eta_squared), 4),
            '结论': f'组间差异{"显著" if significant else "不显著"} (F={f_stat:.2f}, p={p_value:.4f})',
            '各组统计': group_stats,
        }

    @staticmethod
    def multiple_comparison_correction(
        p_values: List[float],
        method: str = 'bonferroni'
    ) -> Dict[str, Any]:
        '''多重比较校正

        当同时进行多个假设检验时，需要进行校正以控制整体错误率。
        '''
        n = len(p_values)
        original_significant = sum(p < 0.05 for p in p_values)

        if method == 'bonferroni':
            corrected = [min(p * n, 1.0) for p in p_values]
        elif method == 'holm':
            sorted_indices = np.argsort(p_values)
            corrected = [0.0] * n
            for rank, idx in enumerate(sorted_indices):
                corrected[idx] = min(p_values[idx] * (n - rank), 1.0)
        elif method == 'fdr_bh':
            # Benjamini-Hochberg
            sorted_indices = np.argsort(p_values)
            corrected = [0.0] * n
            for rank, idx in enumerate(sorted_indices):
                corrected[idx] = min(p_values[idx] * n / (rank + 1), 1.0)
            # 确保单调性
            for i in range(n-2, -1, -1):
                idx1 = sorted_indices[i]
                idx2 = sorted_indices[i+1]
                corrected[idx1] = min(corrected[idx1], corrected[idx2])
        else:
            return {'错误': f'不支持的方法: {method}'}

        corrected_significant = sum(p < 0.05 for p in corrected)

        return {
            '方法': method,
            '检验次数': n,
            '原始显著数': original_significant,
            '校正后显著数': corrected_significant,
            '原始p值': [round(p, 6) for p in p_values],
            '校正后p值': [round(p, 6) for p in corrected],
            '说明': {
                'bonferroni': '最保守，每个p值乘以检验次数',
                'holm': '逐步方法，比Bonferroni更powerful',
                'fdr_bh': '控制错误发现率(FDR)，适用于探索性分析'
            }[method]
        }

    @staticmethod
    def calculate_mde(
        baseline_rate: float,
        n_per_group: int,
        alpha: float = 0.05,
        power: float = 0.80
    ) -> Dict[str, Any]:
        '''反向计算：给定样本量，可以检测到的最小效应
        用于判断当前样本量是否足够
        '''
        from scipy.optimize import brentq

        def power_diff(effect):
            if effect <= 0 or baseline_rate + effect >= 1:
                return float('inf')
            p1 = baseline_rate
            p2 = baseline_rate + effect
            p_bar = (p1 + p2) / 2
            se = np.sqrt(p_bar * (1 - p_bar) * 2 / n_per_group)
            z_alpha = scipy_stats.norm.ppf(1 - alpha/2)
            z_power = abs(effect) / se - z_alpha
            return scipy_stats.norm.cdf(z_power) - power

        try:
            if power_diff(0.001) < 0 and power_diff(0.50) > 0:
                mde = brentq(power_diff, 0.001, 0.50)
            elif power_diff(0.001) > 0:
                mde = 0.001
            else:
                mde = float('inf')
        except:
            mde = float('inf')

        return {
            '每组样本量': n_per_group,
            '基准转化率': baseline_rate,
            '最小可检测效应(MDE)': round(float(mde), 4),
            'MDE百分比': f'{mde*100:.2f}%' if mde != float('inf') else '∞',
            '说明': '在当前样本量下，可以检测到的最小绝对转化率提升'
        }

    @staticmethod
    def sequential_test_analysis(
        p_values_over_time: List[float],
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        '''序贯检验分析
        分析在实验过程中多次查看结果的影响
        '''
        n_checks = len(p_values_over_time)

        # 未校正的显著性判断
        naive_decision = [p < alpha for p in p_values_over_time]

        # Bonferroni校正
        bonferroni_threshold = alpha / n_checks
        bonferroni_decision = [p < bonferroni_threshold for p in p_values_over_time]

        # Pocock边界 (简化)
        pocock_z = scipy_stats.norm.ppf(1 - alpha / (2 * np.sqrt(n_checks)))
        pocock_threshold = 2 * (1 - scipy_stats.norm.cdf(pocock_z))

        # 偷看惩罚
        peeking_penalty = 1 - (1 - alpha) ** (1 / n_checks) if n_checks > 0 else alpha

        return {
            '检查次数': n_checks,
            '原始α': alpha,
            'Bonferroni校正α': round(bonferroni_threshold, 6),
            '偷看惩罚后α': round(peeking_penalty, 6),
            '各次p值': [round(p, 6) for p in p_values_over_time],
            '未校正判断': ['显著' if d else '不显著' for d in naive_decision],
            'Bonferroni判断': ['显著' if d else '不显著' for d in bonferroni_decision],
            '建议': ('❌ 未经校正的多次查看会大幅增加假阳性率！'
                    if any(naive_decision) and not any(bonferroni_decision)
                    else '✅ 校正后结论与原始结论一致' if any(naive_decision) == any(bonferroni_decision)
                    else '⚠️ 建议使用校正后的结论')
        }
