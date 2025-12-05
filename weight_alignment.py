"""
视觉-重量对齐算法
实现餐盘图像中检测到的菜品与时序重量数据的精准匹配
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import linear_sum_assignment
import json


@dataclass
class WeightEvent:
    """重量事件数据类"""
    timestamp: float  # 时间戳（秒）
    cumulative_weight: float  # 累积重量（克）
    delta_weight: float  # 增量重量（克）


@dataclass
class DetectedFood:
    """检测到的菜品数据类"""
    class_name: str  # 菜品类别
    bbox: List[float]  # 边界框 [x1, y1, x2, y2]
    confidence: float  # 置信度
    center_x: float  # 中心点x坐标
    center_y: float  # 中心点y坐标
    area: float  # 区域面积


@dataclass
class AlignedFood:
    """对齐后的菜品数据"""
    food: DetectedFood
    weight: float
    weight_event_index: int
    confidence_score: float  # 对齐置信度


class WeightSensorSimulator:
    """重量传感器模拟器"""

    def __init__(self, noise_level: float = 0.5):
        """
        Args:
            noise_level: 噪声水平（克）
        """
        self.noise_level = noise_level

    def simulate_weight_sequence(self,
                                 food_weights: List[float],
                                 take_intervals: List[float] = None) -> List[WeightEvent]:
        """
        模拟取菜过程的重量序列

        Args:
            food_weights: 各菜品实际重量列表（克）
            take_intervals: 取菜时间间隔列表（秒），默认随机0.5-2秒

        Returns:
            重量事件序列
        """
        if take_intervals is None:
            # 随机生成取菜时间间隔
            take_intervals = np.random.uniform(0.5, 2.0, len(food_weights))

        events = []
        cumulative = 0.0
        current_time = 0.0

        # 初始状态
        events.append(WeightEvent(
            timestamp=0.0,
            cumulative_weight=0.0,
            delta_weight=0.0
        ))

        for i, (weight, interval) in enumerate(zip(food_weights, take_intervals)):
            current_time += interval

            # 添加噪声
            noisy_weight = weight + np.random.normal(0, self.noise_level)
            cumulative += noisy_weight

            events.append(WeightEvent(
                timestamp=current_time,
                cumulative_weight=cumulative,
                delta_weight=noisy_weight
            ))

        return events

    def simulate_with_anomalies(self,
                                food_weights: List[float],
                                anomaly_type: str = 'missing') -> List[WeightEvent]:
        """
        模拟带异常情况的重量序列

        Args:
            food_weights: 各菜品实际重量列表
            anomaly_type: 异常类型
                - 'missing': 漏检（重量事件少于视觉检测）
                - 'extra': 误检（重量事件多于视觉检测）
                - 'merged': 合并事件（多个菜品一次取完）

        Returns:
            重量事件序列
        """
        if anomaly_type == 'missing':
            # 随机移除一个重量事件（模拟传感器漏检）
            if len(food_weights) > 1:
                skip_idx = np.random.randint(0, len(food_weights))
                weights = [w for i, w in enumerate(
                    food_weights) if i != skip_idx]
                return self.simulate_weight_sequence(weights)

        elif anomaly_type == 'extra':
            # 添加额外的噪声事件
            extra_weight = np.random.uniform(10, 30)
            insert_pos = np.random.randint(0, len(food_weights))
            weights = food_weights[:insert_pos] + \
                [extra_weight] + food_weights[insert_pos:]
            return self.simulate_weight_sequence(weights)

        elif anomaly_type == 'merged':
            # 模拟同时取多个菜品
            if len(food_weights) >= 2:
                merge_idx = np.random.randint(0, len(food_weights) - 1)
                weights = (food_weights[:merge_idx] +
                           [food_weights[merge_idx] + food_weights[merge_idx + 1]] +
                           food_weights[merge_idx + 2:])
                return self.simulate_weight_sequence(weights)

        return self.simulate_weight_sequence(food_weights)


class VisualWeightAligner:
    """视觉-重量对齐算法"""

    def __init__(self,
                 weight_tolerance: float = 0.2,
                 spatial_weight: float = 0.6,
                 temporal_weight: float = 0.4):
        """
        Args:
            weight_tolerance: 重量匹配容忍度（相对误差）
            spatial_weight: 空间信息权重
            temporal_weight: 时序信息权重
        """
        self.weight_tolerance = weight_tolerance
        self.spatial_weight = spatial_weight
        self.temporal_weight = temporal_weight

    def sort_foods_spatially(self, foods: List[DetectedFood],
                             direction: str = 'left_to_right') -> List[DetectedFood]:
        """
        按空间位置对菜品排序

        Args:
            foods: 检测到的菜品列表
            direction: 排序方向
                - 'left_to_right': 从左到右
                - 'top_to_bottom': 从上到下
                - 'clockwise': 顺时针（从餐盘中心）

        Returns:
            排序后的菜品列表
        """
        if direction == 'left_to_right':
            return sorted(foods, key=lambda f: f.center_x)

        elif direction == 'top_to_bottom':
            return sorted(foods, key=lambda f: f.center_y)

        elif direction == 'clockwise':
            # 计算餐盘中心
            center_x = np.mean([f.center_x for f in foods])
            center_y = np.mean([f.center_y for f in foods])

            # 计算每个菜品相对中心的角度
            def get_angle(food):
                dx = food.center_x - center_x
                dy = food.center_y - center_y
                return np.arctan2(dy, dx)

            return sorted(foods, key=get_angle)

        return foods

    def extract_weight_increments(self,
                                  events: List[WeightEvent]) -> List[float]:
        """
        从重量事件序列中提取增量重量

        Returns:
            增量重量列表（过滤掉初始状态和异常值）
        """
        increments = []
        for event in events[1:]:  # 跳过初始状态
            if event.delta_weight > 0.5:  # 过滤小于0.5g的噪声
                increments.append(event.delta_weight)
        return increments

    def compute_cost_matrix(self,
                            foods: List[DetectedFood],
                            weights: List[float]) -> np.ndarray:
        """
        计算菜品与重量的匹配成本矩阵

        Args:
            foods: 空间排序后的菜品列表
            weights: 时序排序的重量增量列表

        Returns:
            成本矩阵 [n_foods, n_weights]
        """
        n_foods = len(foods)
        n_weights = len(weights)
        cost_matrix = np.zeros((n_foods, n_weights))

        for i, food in enumerate(foods):
            for j, weight in enumerate(weights):
                # 空间-时序一致性成本（位置越近，成本越低）
                spatial_cost = abs(i - j) / max(n_foods, n_weights)

                # 重量-面积相关性成本（基于先验知识）
                # 假设菜品面积与重量有一定相关性
                expected_weight = self._estimate_weight_from_area(food)
                weight_cost = abs(expected_weight - weight) / \
                    max(expected_weight, weight)

                # 综合成本
                cost_matrix[i, j] = (self.spatial_weight * spatial_cost +
                                     self.temporal_weight * weight_cost)

        return cost_matrix

    def _estimate_weight_from_area(self, food: DetectedFood) -> float:
        """
        根据视觉特征估计重量（简化模型）
        实际应用中可以训练一个回归模型

        Returns:
            估计重量（克）
        """
        # 简化假设：面积与重量成正比
        # 这里使用一个经验系数，实际应根据具体菜品调整
        density_factor = 0.1  # 克/像素²
        return food.area * density_factor

    def align(self,
              foods: List[DetectedFood],
              weight_events: List[WeightEvent],
              sort_direction: str = 'left_to_right') -> List[AlignedFood]:
        """
        执行视觉-重量对齐

        Args:
            foods: 检测到的菜品列表
            weight_events: 重量事件序列
            sort_direction: 空间排序方向

        Returns:
            对齐后的菜品列表
        """
        if not foods:
            return []

        # Step 1: 空间排序
        sorted_foods = self.sort_foods_spatially(foods, sort_direction)

        # Step 2: 提取重量增量
        weights = self.extract_weight_increments(weight_events)

        if not weights:
            # 没有有效重量数据，返回未匹配结果
            return [AlignedFood(
                food=food,
                weight=0.0,
                weight_event_index=-1,
                confidence_score=0.0
            ) for food in sorted_foods]

        # Step 3: 处理数量不一致的情况
        aligned_results = []

        if len(sorted_foods) == len(weights):
            # 理想情况：一对一匹配
            aligned_results = self._one_to_one_alignment(
                sorted_foods, weights, weight_events)

        elif len(sorted_foods) > len(weights):
            # 视觉检测数量 > 重量事件数量（可能漏检）
            aligned_results = self._handle_missing_weights(
                sorted_foods, weights, weight_events)

        else:
            # 视觉检测数量 < 重量事件数量（可能误检或合并）
            aligned_results = self._handle_extra_weights(
                sorted_foods, weights, weight_events)

        return aligned_results

    def _one_to_one_alignment(self,
                              foods: List[DetectedFood],
                              weights: List[float],
                              events: List[WeightEvent]) -> List[AlignedFood]:
        """一对一匹配（使用匈牙利算法）"""
        cost_matrix = self.compute_cost_matrix(foods, weights)

        # 使用匈牙利算法求解最优匹配
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        aligned = []
        for food_idx, weight_idx in zip(row_ind, col_ind):
            confidence = 1.0 - cost_matrix[food_idx, weight_idx]
            aligned.append(AlignedFood(
                food=foods[food_idx],
                weight=weights[weight_idx],
                weight_event_index=weight_idx + 1,  # +1 因为跳过了初始状态
                confidence_score=max(0.0, min(1.0, confidence))
            ))

        return sorted(aligned, key=lambda x: x.food.center_x)

    def _handle_missing_weights(self,
                                foods: List[DetectedFood],
                                weights: List[float],
                                events: List[WeightEvent]) -> List[AlignedFood]:
        """处理重量数据缺失的情况"""
        aligned = []

        # 先对有重量数据的进行匹配
        if weights:
            cost_matrix = self.compute_cost_matrix(foods, weights)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)

            matched_food_indices = set(row_ind)

            for food_idx, weight_idx in zip(row_ind, col_ind):
                confidence = 1.0 - cost_matrix[food_idx, weight_idx]
                aligned.append(AlignedFood(
                    food=foods[food_idx],
                    weight=weights[weight_idx],
                    weight_event_index=weight_idx + 1,
                    confidence_score=max(0.0, min(1.0, confidence))
                ))

            # 未匹配的菜品使用估计重量
            for i, food in enumerate(foods):
                if i not in matched_food_indices:
                    estimated_weight = self._estimate_weight_from_area(food)
                    aligned.append(AlignedFood(
                        food=food,
                        weight=estimated_weight,
                        weight_event_index=-1,
                        confidence_score=0.3  # 低置信度
                    ))
        else:
            # 完全没有重量数据
            for food in foods:
                aligned.append(AlignedFood(
                    food=food,
                    weight=self._estimate_weight_from_area(food),
                    weight_event_index=-1,
                    confidence_score=0.0
                ))

        return sorted(aligned, key=lambda x: x.food.center_x)

    def _handle_extra_weights(self,
                              foods: List[DetectedFood],
                              weights: List[float],
                              events: List[WeightEvent]) -> List[AlignedFood]:
        """处理重量数据冗余的情况（可能合并事件）"""
        aligned = []

        # 尝试识别合并事件
        # 检查是否有重量明显大于其他的事件
        weight_median = np.median(weights)

        merged_candidates = []
        normal_weights = []

        for i, w in enumerate(weights):
            if w > 1.8 * weight_median:  # 明显大于中位数
                merged_candidates.append((i, w))
            else:
                normal_weights.append((i, w))

        if merged_candidates and len(foods) == len(normal_weights):
            # 可能是合并事件，使用正常重量进行匹配
            weight_values = [w for _, w in normal_weights]
            cost_matrix = self.compute_cost_matrix(foods, weight_values)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)

            for food_idx, weight_idx in zip(row_ind, col_ind):
                original_idx, weight_value = normal_weights[weight_idx]
                confidence = 1.0 - cost_matrix[food_idx, weight_idx]
                aligned.append(AlignedFood(
                    food=foods[food_idx],
                    weight=weight_value,
                    weight_event_index=original_idx + 1,
                    confidence_score=max(0.0, min(1.0, confidence))
                ))
        else:
            # 简单选择最可能的权重
            cost_matrix = self.compute_cost_matrix(foods, weights)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)

            for food_idx, weight_idx in zip(row_ind, col_ind):
                confidence = 1.0 - cost_matrix[food_idx, weight_idx]
                aligned.append(AlignedFood(
                    food=foods[food_idx],
                    weight=weights[weight_idx],
                    weight_event_index=weight_idx + 1,
                    confidence_score=max(0.0, min(1.0, confidence))
                ))

        return sorted(aligned, key=lambda x: x.food.center_x)


class AlignmentEvaluator:
    """对齐结果评估器"""

    @staticmethod
    def evaluate(aligned: List[AlignedFood],
                 ground_truth_weights: List[float] = None) -> Dict:
        """
        评估对齐结果

        Args:
            aligned: 对齐结果
            ground_truth_weights: 真实重量（如果有）

        Returns:
            评估指标字典
        """
        metrics = {
            'total_foods': len(aligned),
            'matched_foods': sum(1 for a in aligned if a.weight_event_index >= 0),
            'unmatched_foods': sum(1 for a in aligned if a.weight_event_index < 0),
            'avg_confidence': np.mean([a.confidence_score for a in aligned]),
            'total_weight': sum(a.weight for a in aligned)
        }

        if ground_truth_weights:
            # 计算重量误差
            aligned_weights = [a.weight for a in aligned]
            if len(aligned_weights) == len(ground_truth_weights):
                errors = [abs(aw - gw) / gw for aw, gw in
                          zip(aligned_weights, ground_truth_weights)]
                metrics['mean_relative_error'] = np.mean(errors)
                metrics['max_relative_error'] = np.max(errors)

        return metrics

    @staticmethod
    def visualize_alignment(aligned: List[AlignedFood]) -> str:
        """
        可视化对齐结果（文本形式）

        Returns:
            格式化的对齐结果字符串
        """
        result = "\n" + "="*80 + "\n"
        result += "视觉-重量对齐结果\n"
        result += "="*80 + "\n\n"

        for i, item in enumerate(aligned, 1):
            result += f"菜品 #{i}:\n"
            result += f"  名称: {item.food.class_name}\n"
            result += f"  位置: ({item.food.center_x:.1f}, {item.food.center_y:.1f})\n"
            result += f"  重量: {item.weight:.2f}g\n"
            result += f"  匹配状态: {'已匹配' if item.weight_event_index >= 0 else '未匹配（估计值）'}\n"
            result += f"  置信度: {item.confidence_score:.2%}\n"
            result += "-" * 80 + "\n"

        return result


# 使用示例和测试代码
def demo():
    """演示算法功能"""
    print("="*80)
    print("视觉-重量对齐算法演示")
    print("="*80)

    # 1. 模拟检测到的菜品（YOLOv8输出）
    detected_foods = [
        DetectedFood(
            class_name="红烧肉",
            bbox=[100, 150, 200, 250],
            confidence=0.95,
            center_x=150,
            center_y=200,
            area=10000
        ),
        DetectedFood(
            class_name="青菜",
            bbox=[250, 180, 320, 260],
            confidence=0.92,
            center_x=285,
            center_y=220,
            area=5600
        ),
        DetectedFood(
            class_name="米饭",
            bbox=[350, 160, 480, 280],
            confidence=0.98,
            center_x=415,
            center_y=220,
            area=15600
        ),
        DetectedFood(
            class_name="豆腐",
            bbox=[500, 190, 580, 270],
            confidence=0.89,
            center_x=540,
            center_y=230,
            area=6400
        )
    ]

    # 2. 模拟真实重量
    true_weights = [85.0, 45.0, 120.0, 55.0]  # 克

    print(f"\n检测到 {len(detected_foods)} 个菜品:")
    for food in detected_foods:
        print(
            f"  - {food.class_name}: 位置({food.center_x:.0f}, {food.center_y:.0f})")

    # 3. 模拟正常情况
    print("\n" + "="*80)
    print("场景1: 正常情况（数量一致）")
    print("="*80)

    simulator = WeightSensorSimulator(noise_level=1.0)
    weight_events = simulator.simulate_weight_sequence(true_weights)

    print(f"\n重量事件序列 ({len(weight_events)-1} 次取菜):")
    for i, event in enumerate(weight_events[1:], 1):
        print(
            f"  事件{i}: +{event.delta_weight:.2f}g (累计: {event.cumulative_weight:.2f}g)")

    aligner = VisualWeightAligner()
    aligned = aligner.align(detected_foods, weight_events)

    print(AlignmentEvaluator.visualize_alignment(aligned))

    metrics = AlignmentEvaluator.evaluate(aligned, true_weights)
    print("评估指标:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # 4. 模拟异常情况1：重量事件缺失
    print("\n" + "="*80)
    print("场景2: 异常情况 - 重量传感器漏检")
    print("="*80)

    weight_events_missing = simulator.simulate_with_anomalies(
        true_weights, 'missing')
    print(f"\n重量事件序列 ({len(weight_events_missing)-1} 次取菜，少于视觉检测):")
    for i, event in enumerate(weight_events_missing[1:], 1):
        print(
            f"  事件{i}: +{event.delta_weight:.2f}g (累计: {event.cumulative_weight:.2f}g)")

    aligned_missing = aligner.align(detected_foods, weight_events_missing)
    print(AlignmentEvaluator.visualize_alignment(aligned_missing))

    # 5. 模拟异常情况2：合并事件
    print("\n" + "="*80)
    print("场景3: 异常情况 - 同时取多个菜品")
    print("="*80)

    weight_events_merged = simulator.simulate_with_anomalies(
        true_weights, 'merged')
    print(f"\n重量事件序列 ({len(weight_events_merged)-1} 次取菜，有合并事件):")
    for i, event in enumerate(weight_events_merged[1:], 1):
        print(
            f"  事件{i}: +{event.delta_weight:.2f}g (累计: {event.cumulative_weight:.2f}g)")

    aligned_merged = aligner.align(detected_foods, weight_events_merged)
    print(AlignmentEvaluator.visualize_alignment(aligned_merged))

    print("\n" + "="*80)
    print("演示完成")
    print("="*80)


if __name__ == '__main__':
    demo()
