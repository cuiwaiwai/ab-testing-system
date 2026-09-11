# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 统计计算核心模块
功能：样本量计算、假设检验、效应量计算等AB测试核心统计方法
'''

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from typing import Dict, Any, Tuple, Optional, List


class ABCalculator:
    '''A/B测试统计计算器'''

    # ==================== 样本量计算 ====================

    @staticmethod
    def sample_size_proportion(
        baseline_rate: float,
        minimum_effect: float,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        '''计算比例类指标的每组所需样本量
        基于两样本比例检验的样本量公式

        参数:
            baseline_rate: 对照组基准转化率 (0~1)
            minimum_effect: 最小可检测效应 (绝对差值, 0~1)
            alpha: 显著性水平 (默认0.05)
            power: 检验功效/统计效力 (默认0.80)
            alternative: 备择假设类型 ('two-sided', 'larger', 'smaller')

        返回:
            包含样本量计算结果的字典
        '''
        if alternative == 'two-sided':
            z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = scipy_stats.norm.ppf(1 - alpha)

        z_beta = scipy_stats.norm.ppf(power)

        p1 = baseline_rate
        p2 = baseline_rate + minimum_effect

        # 两样本比例检验样本量公式
        p_bar = (p1 + p2) / 2
        numerator = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
                    z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2

        if denominator == 0:
            return {'每组样本量': float('inf'), '总样本量': float('inf'),
                   '说明': '效应量为零，无法计算有意义的样本量'}

        n_per_group = int(np.ceil(numerator / denominator))
        n_total = n_per_group * 2

        return {
            '每组样本量': n_per_group,
            '总样本量': n_total,
            '对照组转化率': baseline_rate,
            '实验组预期转化率': baseline_rate + minimum_effect,
            '最小可检测效应': minimum_effect,
            '显著性水平(α)': alpha,
            '统计功效(1-β)': power,
            '检验类型': alternative,
            '指标类型': '比例型(转化率等)'
        }

    @staticmethod
    def sample_size_mean(
        baseline_mean: float,
        baseline_std: float,
        minimum_effect: float,
        alpha: float = 0.05,
        power: float = 0.80,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        '''计算均值类指标的每组所需样本量
        基于两样本t检验的样本量公式

        参数:
            baseline_mean: 对照组基准均值
            baseline_std: 对照组标准差
            minimum_effect: 最小可检测效应 (绝对差值)
            alpha: 显著性水平 (默认0.05)
            power: 检验功效 (默认0.80)
            alternative: 备择假设类型

        返回:
            包含样本量计算结果的字典
        '''
        if alternative == 'two-sided':
            z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
        else:
            z_alpha = scipy_stats.norm.ppf(1 - alpha)

        z_beta = scipy_stats.norm.ppf(power)

        effect_size = minimum_effect / baseline_std if baseline_std > 0 else 0

        if effect_size == 0:
            return {'每组样本量': float('inf'), '总样本量': float('inf'),
                   '说明': '效应量为零，无法计算有意义的样本量'}

        # Cohen's d的样本量公式(近似)
        n_per_group = int(np.ceil(2 * (z_alpha + z_beta) ** 2 / effect_size ** 2))

        return {
            '每组样本量': n_per_group,
            '总样本量': n_per_group * 2,
            '对照组均值': baseline_mean,
            '实验组预期均值': baseline_mean + minimum_effect,
            '标准差': baseline_std,
            '最小可检测效应': minimum_effect,
            '效应量(Cohens d)': effect_size,
            '显著性水平(α)': alpha,
            '统计功效(1-β)': power,
            '检验类型': alternative,
            '指标类型': '均值型(连续指标)'
        }

    # ==================== 假设检验 ====================

    @staticmethod
    def two_sample_t_test(
        group_a: np.ndarray,
        group_b: np.ndarray,
        alpha: float = 0.05,
        alternative: str = 'two-sided',
        equal_var: bool = False
    ) -> Dict[str, Any]:
        '''两独立样本t检验 (Welch's t-test)
        用于比较两组连续型指标的均值差异

        参数:
            group_a: 对照组数据
            group_b: 实验组数据
            alpha: 显著性水平
            alternative: 备择假设 ('two-sided', 'greater', 'less')
            equal_var: 是否假设方差相等 (默认False, Welch's)

        返回:
            包含检验结果的字典
        '''
        clean_a = group_a[~np.isnan(group_a)]
        clean_b = group_b[~np.isnan(group_b)]

        if len(clean_a) < 2 or len(clean_b) < 2:
            return {'错误': '每组至少需要2个有效观测值'}

        # 描述性统计
        mean_a, mean_b = np.mean(clean_a), np.mean(clean_b)
        std_a, std_b = np.std(clean_a, ddof=1), np.std(clean_b, ddof=1)

        # t检验
        t_stat, p_value = scipy_stats.ttest_ind(
            clean_a, clean_b,
            equal_var=equal_var,
            alternative=alternative
        )

        # 自由度 (Welch-Satterthwaite近似)
        if not equal_var:
            v_numer = (std_a**2/len(clean_a) + std_b**2/len(clean_b))**2
            v_denom = ((std_a**2/len(clean_a))**2/(len(clean_a)-1) +
                      (std_b**2/len(clean_b))**2/(len(clean_b)-1))
            df = v_numer / v_denom if v_denom > 0 else len(clean_a) + len(clean_b) - 2
        else:
            df = len(clean_a) + len(clean_b) - 2

        # 效应量 Cohen's d
        pooled_std = np.sqrt(((len(clean_a)-1)*std_a**2 + (len(clean_b)-1)*std_b**2) /
                            (len(clean_a) + len(clean_b) - 2))
        cohens_d = (mean_b - mean_a) / pooled_std if pooled_std > 0 else 0

        # 置信区间
        diff = mean_b - mean_a
        se_diff = np.sqrt(std_a**2/len(clean_a) + std_b**2/len(clean_b))
        if alternative == 'two-sided':
            t_crit = scipy_stats.t.ppf(1 - alpha/2, df)
            ci_lower = diff - t_crit * se_diff
            ci_upper = diff + t_crit * se_diff
        elif alternative == 'greater':
            t_crit = scipy_stats.t.ppf(1 - alpha, df)
            ci_lower = diff - t_crit * se_diff
            ci_upper = float('inf')
        else:
            t_crit = scipy_stats.t.ppf(1 - alpha, df)
            ci_lower = float('-inf')
            ci_upper = diff + t_crit * se_diff

        significant = p_value < alpha

        return {
            '检验方法': "Welch's t-test" if not equal_var else "Student's t-test",
            '对照组样本量': len(clean_a),
            '实验组样本量': len(clean_b),
            '对照组均值': round(mean_a, 4),
            '实验组均值': round(mean_b, 4),
            '均值差异(B-A)': round(diff, 4),
            '对照组标准差': round(std_a, 4),
            '实验组标准差': round(std_b, 4),
            't统计量': round(t_stat, 4),
            '自由度': round(df, 1),
            'p值': round(p_value, 6),
            '显著性水平(α)': alpha,
            '是否显著': '是' if significant else '否',
            '结论': f'差异{"显著" if significant else "不显著"} (p={p_value:.4f} {"<" if significant else "≥"} {alpha})',
            '效应量(Cohens d)': round(cohens_d, 4),
            '效应量解释': ABCalculator._interpret_cohens_d(cohens_d),
            '均值差异95%CI': (round(ci_lower, 4), round(ci_upper, 4)) if ci_upper != float('inf') else (round(ci_lower, 4), '∞'),
            '置信区间': (round(ci_lower, 4), round(ci_upper, 4)),
        }

    @staticmethod
    def proportions_z_test(
        successes_a: int, trials_a: int,
        successes_b: int, trials_b: int,
        alpha: float = 0.05,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        '''两样本比例Z检验
        用于比较两组转化率/点击率等比例类指标

        参数:
            successes_a, trials_a: 对照组成功数和总样本量
            successes_b, trials_b: 实验组成功数和总样本量
            alpha: 显著性水平
            alternative: 备择假设

        返回:
            包含检验结果的字典
        '''
        p_a = successes_a / trials_a if trials_a > 0 else 0
        p_b = successes_b / trials_b if trials_b > 0 else 0

        # 合并比例
        p_pooled = (successes_a + successes_b) / (trials_a + trials_b)

        # 标准误
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/trials_a + 1/trials_b))

        if se == 0:
            return {'错误': '标准误为零，无法进行检验'}

        # Z统计量
        z_stat = (p_b - p_a) / se

        # p值
        if alternative == 'two-sided':
            p_value = 2 * (1 - scipy_stats.norm.cdf(abs(z_stat)))
        elif alternative == 'greater':
            p_value = 1 - scipy_stats.norm.cdf(z_stat)
        else:
            p_value = scipy_stats.norm.cdf(z_stat)

        # 置信区间
        se_unpooled = np.sqrt(p_a*(1-p_a)/trials_a + p_b*(1-p_b)/trials_b)
        diff = p_b - p_a
        if alternative == 'two-sided':
            z_crit = scipy_stats.norm.ppf(1 - alpha/2)
            ci_lower = diff - z_crit * se_unpooled
            ci_upper = diff + z_crit * se_unpooled
        elif alternative == 'greater':
            z_crit = scipy_stats.norm.ppf(1 - alpha)
            ci_lower = diff - z_crit * se_unpooled
            ci_upper = float('inf')
        else:
            z_crit = scipy_stats.norm.ppf(1 - alpha)
            ci_lower = float('-inf')
            ci_upper = diff + z_crit * se_unpooled

        # 相对提升
        relative_lift = (p_b - p_a) / p_a * 100 if p_a > 0 else float('inf')

        significant = p_value < alpha

        return {
            '检验方法': '两样本比例Z检验',
            '对照组转化数/总数': f'{successes_a}/{trials_a}',
            '实验组转化数/总数': f'{successes_b}/{trials_b}',
            '对照组转化率': round(p_a, 4),
            '实验组转化率': round(p_b, 4),
            '绝对提升': round(diff, 4),
            '相对提升(%)': round(relative_lift, 2),
            'Z统计量': round(z_stat, 4),
            'p值': round(p_value, 6),
            '显著性水平(α)': alpha,
            '是否显著': '是' if significant else '否',
            '结论': f'差异{"显著" if significant else "不显著"} (p={p_value:.4f} {"<" if significant else "≥"} {alpha})',
            '差异95%CI': (round(ci_lower, 4), round(ci_upper, 4)) if ci_upper != float('inf') else (round(ci_lower, 4), '∞'),
        }

    @staticmethod
    def chi_square_test(
        observed: np.ndarray,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        '''卡方独立性检验
        用于比较两组分类变量的分布差异

        参数:
            observed: 2×k的列联表 (实际观测频数)
            alpha: 显著性水平

        返回:
            包含检验结果的字典
        '''
        chi2, p_value, dof, expected = scipy_stats.chi2_contingency(observed)

        significant = p_value < alpha

        # Cramer's V (效应量)
        n = observed.sum()
        min_dim = min(observed.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

        return {
            '检验方法': '卡方独立性检验',
            'χ²统计量': round(chi2, 4),
            '自由度': dof,
            'p值': round(p_value, 6),
            '显著性水平(α)': alpha,
            '是否显著': '是' if significant else '否',
            '结论': f'分布差异{"显著" if significant else "不显著"} (p={p_value:.4f})',
            '效应量(Cramérs V)': round(cramers_v, 4),
            '总样本量': int(n),
        }

    @staticmethod
    def mann_whitney_u_test(
        group_a: np.ndarray,
        group_b: np.ndarray,
        alpha: float = 0.05,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        '''Mann-Whitney U检验 (非参数检验)
        当数据不满足正态性假设时使用

        参数:
            group_a, group_b: 两组数据
            alpha: 显著性水平
            alternative: 备择假设

        返回:
            包含检验结果的字典
        '''
        clean_a = group_a[~np.isnan(group_a)]
        clean_b = group_b[~np.isnan(group_b)]

        stat, p_value = scipy_stats.mannwhitneyu(
            clean_a, clean_b,
            alternative=alternative
        )

        significant = p_value < alpha

        # 效应量 (rank-biserial correlation)
        n_a, n_b = len(clean_a), len(clean_b)
        r = 1 - (2 * stat) / (n_a * n_b) if n_a * n_b > 0 else 0

        return {
            '检验方法': 'Mann-Whitney U检验 (非参数)',
            '对照组样本量': n_a,
            '实验组样本量': n_b,
            'U统计量': stat,
            'p值': round(p_value, 6),
            '显著性水平(α)': alpha,
            '是否显著': '是' if significant else '否',
            '结论': f'差异{"显著" if significant else "不显著"} (p={p_value:.4f})',
            '效应量(秩双列相关)': round(r, 4),
            '对照组中位数': round(np.median(clean_a), 4),
            '实验组中位数': round(np.median(clean_b), 4),
        }

    # ==================== 辅助方法 ====================

    @staticmethod
    def _interpret_cohens_d(d: float) -> str:
        '''解释Cohen's d效应量大小'''
        abs_d = abs(d)
        if abs_d < 0.2:
            return '可忽略 (|d| < 0.2)'
        elif abs_d < 0.5:
            return '小效应 (0.2 ≤ |d| < 0.5)'
        elif abs_d < 0.8:
            return '中等效应 (0.5 ≤ |d| < 0.8)'
        else:
            return '大效应 (|d| ≥ 0.8)'

    @staticmethod
    def calculate_confidence_interval(
        data: np.ndarray,
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        '''计算均值的置信区间

        参数:
            data: 数据数组
            confidence: 置信水平

        返回:
            (下界, 均值, 上界)
        '''
        clean_data = data[~np.isnan(data)]
        mean = np.mean(clean_data)
        se = scipy_stats.sem(clean_data)
        ci = scipy_stats.t.interval(
            confidence,
            df=len(clean_data)-1,
            loc=mean,
            scale=se
        )
        return (round(ci[0], 4), round(mean, 4), round(ci[1], 4))

    @staticmethod
    def check_normality(data: np.ndarray) -> Dict[str, Any]:
        '''检验数据正态性 (用于判断该用参数检验还是非参数检验)'''
        clean = data[~np.isnan(data)]
        if len(clean) < 3:
            return {'is_normal': False, 'reason': '样本量过小(<3)'}

        if len(clean) <= 5000:
            stat, p = scipy_stats.shapiro(clean)
            method = 'Shapiro-Wilk'
        else:
            stat, p = scipy_stats.normaltest(clean)
            method = "D'Agostino K²"

        return {
            'is_normal': p > 0.05,
            'method': method,
            'statistic': round(stat, 4),
            'p_value': round(p, 6),
            'recommendation': '建议使用参数检验(t检验)' if p > 0.05 else '建议使用非参数检验(Mann-Whitney U)'
        }

    @staticmethod
    def generate_sample_ab_data(
        n_a: int = 1000,
        n_b: int = 1000,
        effect_size: float = 0.3
    ) -> pd.DataFrame:
        '''生成AB测试示例数据

        参数:
            n_a: 对照组样本量
            n_b: 实验组样本量
            effect_size: 效应量 (Cohen's d)

        返回:
            包含分组和多个指标的DataFrame
        '''
        np.random.seed(42)

        # 生成数据
        group_a = pd.DataFrame({
            'group': 'A(对照)',
            'user_id': [f'A{i:05d}' for i in range(n_a)],
            'visit_duration': np.random.normal(120, 30, n_a).clip(10, 300),
            'page_views': np.random.poisson(5, n_a).clip(1, 30),
            'purchase_amount': np.random.lognormal(3, 0.8, n_a).clip(0, 500).round(2),
        })

        group_b = pd.DataFrame({
            'group': 'B(实验)',
            'user_id': [f'B{i:05d}' for i in range(n_b)],
            'visit_duration': np.random.normal(120 + effect_size*30, 30, n_b).clip(10, 300),
            'page_views': np.random.poisson(5 + effect_size*0.5, n_b).clip(1, 30),
            'purchase_amount': np.random.lognormal(3 + effect_size*0.2, 0.8, n_b).clip(0, 500).round(2),
        })

        df = pd.concat([group_a, group_b], ignore_index=True)

        # 添加转化指标 (二分类)
        base_rate = 0.15
        df['converted'] = 0
        df.loc[df['group'] == 'A(对照)', 'converted'] = (
            np.random.random(n_a) < base_rate
        ).astype(int)
        df.loc[df['group'] == 'B(实验)', 'converted'] = (
            np.random.random(n_b) < base_rate * (1 + effect_size * 0.5)
        ).astype(int)

        # 添加分类变量
        df['device_type'] = np.random.choice(
            ['Mobile', 'Desktop', 'Tablet'],
            n_a + n_b,
            p=[0.5, 0.35, 0.15]
        )

        return df
