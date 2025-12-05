from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import base64
import os
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import json

app = Flask(__name__)
CORS(app)

# 配置密钥和数据库
app.secret_key = secrets.token_hex(16)  # 生产环境请使用固定的密钥

# MySQL 数据库配置
# 格式: mysql://用户名:密码@主机:端口/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/monisys'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

db = SQLAlchemy(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(RESULT_FOLDER).mkdir(exist_ok=True)


# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,
                         nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    height = db.Column(db.Float)  # 身高(cm)
    weight = db.Column(db.Float)  # 体重(kg)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    is_active = db.Column(db.Boolean, default=True)  # 账号是否激活
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 关联检测记录
    detection_records = db.relationship(
        'DetectionRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    diet_habits = db.relationship(
        'DietHabit', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """将用户对象转换为字典，确保布尔值正确序列化"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'height': self.height,
            'weight': self.weight,
            'age': self.age,
            'gender': self.gender,
            'is_admin': bool(self.is_admin),  # 显式转换为布尔值
            'is_active': bool(self.is_active),  # 显式转换为布尔值
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


# 饮食习惯模型
class DietHabit(db.Model):
    __tablename__ = 'diet_habits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    diet_type = db.Column(db.String(50))  # 饮食类型：素食、杂食等
    allergies = db.Column(db.Text)  # 过敏食物
    preferences = db.Column(db.Text)  # 饮食偏好
    meals_per_day = db.Column(db.Integer)  # 每天用餐次数
    water_intake = db.Column(db.Float)  # 每天饮水量(L)
    notes = db.Column(db.Text)  # 其他备注
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """将饮食习惯对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'diet_type': self.diet_type,
            'allergies': self.allergies,
            'preferences': self.preferences,
            'meals_per_day': self.meals_per_day,
            'water_intake': self.water_intake,
            'notes': self.notes,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# 检测记录模型
class DetectionRecord(db.Model):
    __tablename__ = 'detection_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    detected_objects = db.Column(db.Text)  # JSON格式存储检测结果
    image_path = db.Column(db.String(255))
    detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

# ==================== 营养数据库模型 ====================


class Canteen(db.Model):
    __tablename__ = 'canteens'
    canteen_id = db.Column(db.String(7), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)

    # 关联菜品
    dishes = db.relationship('Dish', backref='canteen', lazy=True)


class Dish(db.Model):
    __tablename__ = 'dishes'
    dish_id = db.Column(db.String(7), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    canteen_id = db.Column(db.String(7), db.ForeignKey(
        'canteens.canteen_id'), nullable=False)
    cooking_method = db.Column(db.String(50))
    description = db.Column(db.Text)

    # 关联食材
    ingredients = db.relationship('DishIngredient', backref='dish', lazy=True)


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    ingredient_id = db.Column(db.String(7), primary_key=True)
    ingredient_name = db.Column(db.String(100), nullable=False, unique=True)
    unit = db.Column(db.String(20), default='g')

    # 关联营养成分
    nutrition = db.relationship(
        'NutritionFact', backref='ingredient', uselist=False, lazy=True)


class NutritionFact(db.Model):
    __tablename__ = 'nutrition_facts'
    ingredient_id = db.Column(db.String(7), db.ForeignKey(
        'ingredients.ingredient_id'), primary_key=True)
    energy_kcal = db.Column(db.Float)
    protein_g = db.Column(db.Float)
    fat_g = db.Column(db.Float)
    carbohydrate_g = db.Column(db.Float)
    fiber_g = db.Column(db.Float)
    sodium_mg = db.Column(db.Float)
    calcium_mg = db.Column(db.Float)
    vitamin_c_mg = db.Column(db.Float)


class DishIngredient(db.Model):
    __tablename__ = 'dish_ingredients'
    dish_id = db.Column(db.String(7), db.ForeignKey(
        'dishes.dish_id'), primary_key=True)
    ingredient_id = db.Column(db.String(7), db.ForeignKey(
        'ingredients.ingredient_id'), primary_key=True)
    amount_g = db.Column(db.Float, nullable=False)

    # 关联到食材获取营养信息
    ingredient_obj = db.relationship(
        'Ingredient', backref='dish_uses', lazy=True)

    def to_dict(self):
        """将检测记录对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'detected_objects': self.detected_objects,
            'image_path': self.image_path,
            'detection_time': self.detection_time.isoformat() if self.detection_time else None,
            'notes': self.notes
        }


# 创建数据库表
with app.app_context():
    db.create_all()

# 添加自定义Jinja2过滤器


@app.template_filter('from_json')
def from_json_filter(value):
    """将JSON字符串转换为Python对象"""
    try:
        return json.loads(value)
    except:
        return value

# ==================== 营养计算工具函数 ====================


class NutritionCalculator:
    """营养成分计算器"""

    @staticmethod
    def calculate_bmr_tdee(weight_kg, height_cm, age, gender, activity_level):
        """
        基于Mifflin-St Jeor公式计算基础代谢率(BMR)和总能量消耗(TDEE)

        Args:
            weight_kg: 体重(kg)
            height_cm: 身高(cm)
            age: 年龄
            gender: 性别('男' 或 '女')
            activity_level: 活动系数 ('sedentary', 'light', 'moderate', 'heavy')

        Returns:
            dict: 包含BMR、TDEE和宏量营养素推荐摄入量
        """
        # Mifflin-St Jeor 公式
        # 男性: BMR = 10*体重(kg) + 6.25*身高(cm) - 5*年龄 + 5
        # 女性: BMR = 10*体重(kg) + 6.25*身高(cm) - 5*年龄 - 161

        if gender == '男':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # 女
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        # 活动系数
        activity_multipliers = {
            'sedentary': 1.2,    # 久坐(办公室工作，很少运动)
            'light': 1.375,      # 轻度(每周轻度运动1-3天)
            'moderate': 1.55,    # 中度(每周中度运动3-5天)
            'heavy': 1.725       # 重度(每周高强度运动6-7天)
        }

        multiplier = activity_multipliers.get(activity_level, 1.2)
        tdee = bmr * multiplier

        # 宏量营养素分配比例 (基于一般健康饮食指南)
        # 蛋白质: 15-25% (这里取20%)
        # 脂肪: 20-35% (这里取25%)
        # 碳水化合物: 45-65% (这里取55%)

        protein_calories = tdee * 0.20
        fat_calories = tdee * 0.25
        carb_calories = tdee * 0.55

        # 转换为克数 (每克提供热量: 蛋白质4千卡, 脂肪9千卡, 碳水化合物4千卡)
        protein_grams = protein_calories / 4
        fat_grams = fat_calories / 9
        carb_grams = carb_calories / 4

        return {
            'bmr': round(bmr, 2),
            'tdee': round(tdee, 2),
            'activity_multiplier': multiplier,
            'macronutrients': {
                'protein': {
                    'grams': round(protein_grams, 1),
                    'calories': round(protein_calories, 1),
                    'percentage': 20
                },
                'fat': {
                    'grams': round(fat_grams, 1),
                    'calories': round(fat_calories, 1),
                    'percentage': 25
                },
                'carbohydrates': {
                    'grams': round(carb_grams, 1),
                    'calories': round(carb_calories, 1),
                    'percentage': 55
                }
            }
        }

    @staticmethod
    def calculate_dish_nutrition(dish_name, actual_weight_g):
        """
        计算菜品的营养成分

        Args:
            dish_name: 菜品名称
            actual_weight_g: 实际重量（克）

        Returns:
            dict: 营养成分字典，如果菜品不存在返回None
        """
        # 查找菜品
        dish = Dish.query.filter_by(name=dish_name).first()

        if not dish:
            return None

        # 计算配方总重量
        recipe_total_weight = sum(di.amount_g for di in dish.ingredients)

        if recipe_total_weight == 0:
            return None

        # 计算缩放比例（实际重量 / 配方总重量）
        scale_factor = actual_weight_g / recipe_total_weight

        # 初始化营养成分累加器
        nutrition_total = {
            'energy_kcal': 0.0,
            'protein_g': 0.0,
            'fat_g': 0.0,
            'carbohydrate_g': 0.0,
            'fiber_g': 0.0,
            'sodium_mg': 0.0,
            'calcium_mg': 0.0,
            'vitamin_c_mg': 0.0
        }

        # 遍历菜品中的每种食材
        for dish_ingredient in dish.ingredients:
            ingredient = dish_ingredient.ingredient_obj
            nutrition_fact = ingredient.nutrition

            if not nutrition_fact:
                continue

            # 计算该食材的实际用量（配方用量 × 缩放比例）
            actual_ingredient_amount = dish_ingredient.amount_g * scale_factor

            # 计算该食材贡献的营养成分（营养成分是按100g计算的）
            factor = actual_ingredient_amount / 100.0

            nutrition_total['energy_kcal'] += (
                nutrition_fact.energy_kcal or 0) * factor
            nutrition_total['protein_g'] += (
                nutrition_fact.protein_g or 0) * factor
            nutrition_total['fat_g'] += (nutrition_fact.fat_g or 0) * factor
            nutrition_total['carbohydrate_g'] += (
                nutrition_fact.carbohydrate_g or 0) * factor
            nutrition_total['fiber_g'] += (
                nutrition_fact.fiber_g or 0) * factor
            nutrition_total['sodium_mg'] += (
                nutrition_fact.sodium_mg or 0) * factor
            nutrition_total['calcium_mg'] += (
                nutrition_fact.calcium_mg or 0) * factor
            nutrition_total['vitamin_c_mg'] += (
                nutrition_fact.vitamin_c_mg or 0) * factor

        return {
            'dish_id': dish.dish_id,
            'dish_name': dish_name,
            'actual_weight_g': actual_weight_g,
            'recipe_weight_g': recipe_total_weight,
            'canteen_name': dish.canteen.name if dish.canteen else None,
            'cooking_method': dish.cooking_method,
            'nutrition': nutrition_total,
            'ingredient_count': len(dish.ingredients)
        }

    @staticmethod
    def format_nutrition_display(nutrition_data):
        """
        格式化营养成分用于显示

        Returns:
            dict: 格式化后的营养信息
        """
        if not nutrition_data:
            return None

        nutrition = nutrition_data['nutrition']
        return {
            'dish_name': nutrition_data['dish_name'],
            'weight': f"{nutrition_data['actual_weight_g']:.1f}g",
            'canteen': nutrition_data.get('canteen_name', '未知'),
            'cooking_method': nutrition_data.get('cooking_method', '未知'),
            'nutrients': [
                {'name': '热量',
                    'value': f"{nutrition['energy_kcal']:.1f}", 'unit': '千卡'},
                {'name': '蛋白质',
                    'value': f"{nutrition['protein_g']:.1f}", 'unit': 'g'},
                {'name': '脂肪',
                    'value': f"{nutrition['fat_g']:.1f}", 'unit': 'g'},
                {'name': '碳水化合物',
                    'value': f"{nutrition['carbohydrate_g']:.1f}", 'unit': 'g'},
                {'name': '膳食纤维',
                    'value': f"{nutrition['fiber_g']:.1f}", 'unit': 'g'},
                {'name': '钠',
                    'value': f"{nutrition['sodium_mg']:.1f}", 'unit': 'mg'},
                {'name': '钙',
                    'value': f"{nutrition['calcium_mg']:.1f}", 'unit': 'mg'},
                {'name': '维生素C',
                    'value': f"{nutrition['vitamin_c_mg']:.1f}", 'unit': 'mg'}
            ]
        }


# 加载YOLO模型（请根据你的模型路径修改）
# 例如: model = YOLO('yolov8n.pt') 或 model = YOLO('你的模型路径.pt')
try:
    # 默认使用YOLOv8n模型，你可以替换成自己训练的模型
    model = YOLO(r'food_detection4\weights\best.pt')
except:
    model = None
    print("警告: YOLO模型加载失败，请确保模型文件存在")


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                return jsonify({'success': False, 'message': '账号已被禁用，请联系管理员'}), 403

            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = bool(user.is_admin)  # 确保是标准布尔值

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            db.session.commit()

            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        height = data.get('height')
        weight = data.get('weight')
        age = data.get('age')
        gender = data.get('gender')

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '用户名已存在'}), 400

        # 创建新用户
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            height=height,
            weight=weight,
            age=age,
            gender=gender,
            is_admin=False,  # 默认非管理员
            is_active=True  # 默认激活
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': '注册成功'})

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        data = request.get_json()

        # 更新用户信息
        user.height = data.get('height', user.height)
        user.weight = data.get('weight', user.weight)
        user.age = data.get('age', user.age)
        user.gender = data.get('gender', user.gender)
        user.email = data.get('email', user.email)

        db.session.commit()

        return jsonify({'success': True, 'message': '信息更新成功'})

    # GET请求渲染模板
    return render_template('profile.html', user=user)


@app.route('/diet_habits', methods=['GET', 'POST'])
def diet_habits():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    if request.method == 'POST':
        data = request.get_json()

        # 查找或创建饮食习惯记录
        habit = DietHabit.query.filter_by(user_id=session['user_id']).first()

        if habit:
            # 更新现有记录
            habit.diet_type = data.get('diet_type', habit.diet_type)
            habit.allergies = data.get('allergies', habit.allergies)
            habit.preferences = data.get('preferences', habit.preferences)
            habit.meals_per_day = data.get(
                'meals_per_day', habit.meals_per_day)
            habit.water_intake = data.get('water_intake', habit.water_intake)
            habit.notes = data.get('notes', habit.notes)
            habit.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            habit = DietHabit(
                user_id=session['user_id'],
                diet_type=data.get('diet_type'),
                allergies=data.get('allergies'),
                preferences=data.get('preferences'),
                meals_per_day=data.get('meals_per_day'),
                water_intake=data.get('water_intake'),
                notes=data.get('notes')
            )
            db.session.add(habit)

        db.session.commit()
        return jsonify({'success': True, 'message': '饮食习惯保存成功'})

    # GET 请求：返回当前用户的饮食习惯
    habit = DietHabit.query.filter_by(user_id=session['user_id']).first()
    if habit:
        return jsonify({
            'diet_type': habit.diet_type,
            'allergies': habit.allergies,
            'preferences': habit.preferences,
            'meals_per_day': habit.meals_per_day,
            'water_intake': habit.water_intake,
            'notes': habit.notes
        })
    return jsonify({})


@app.route('/calculate_bmr_tdee', methods=['POST'])
def calculate_bmr_tdee():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json()
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        age = int(data.get('age'))
        gender = data.get('gender')
        activity_level = data.get('activity_level', 'sedentary')

        # 验证参数
        if not all([weight, height, age, gender]):
            return jsonify({'success': False, 'message': '请填写完整的身体信息'}), 400

        if gender not in ['男', '女']:
            return jsonify({'success': False, 'message': '性别必须是"男"或"女"'}), 400

        if activity_level not in ['sedentary', 'light', 'moderate', 'heavy']:
            return jsonify({'success': False, 'message': '活动水平无效'}), 400

        # 计算BMR和TDEE
        result = NutritionCalculator.calculate_bmr_tdee(
            weight, height, age, gender, activity_level)

        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'message': '参数格式错误'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'计算出错: {str(e)}'}), 500


@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401

        if model is None:
            return jsonify({'error': '模型未加载'}), 500

        # 获取上传的图片
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        # 获取重量数据（如果有）
        weight_data_str = request.form.get('weight_data', None)

        # 读取图片
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': '无法读取图片'}), 400

        # 使用YOLO模型进行检测
        results = model(img)

        # 在图片上绘制检测结果
        annotated_img = results[0].plot()

        # 将结果图片转换为base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # 提取检测结果信息
        detections = []
        for box in results[0].boxes:
            detection = {
                'class': results[0].names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            }
            detections.append(detection)

        # 如果有重量数据，进行视觉-重量对齐
        alignment_result = None
        if weight_data_str:
            try:
                from weight_alignment import (
                    DetectedFood, WeightEvent, VisualWeightAligner,
                    AlignmentEvaluator
                )

                # 解析重量数据
                weight_data = json.loads(weight_data_str)

                # 构建检测食物列表
                img_height, img_width = img.shape[:2]
                detected_foods = []
                for det in detections:
                    bbox = det['bbox']
                    center_x = (bbox[0] + bbox[2]) / 2
                    center_y = (bbox[1] + bbox[3]) / 2
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])

                    detected_foods.append(DetectedFood(
                        class_name=det['class'],
                        bbox=bbox,
                        confidence=det['confidence'],
                        center_x=center_x,
                        center_y=center_y,
                        area=area
                    ))

                # 构建重量事件列表
                weight_events = []
                for event_data in weight_data:
                    weight_events.append(WeightEvent(
                        timestamp=event_data['timestamp'],
                        cumulative_weight=event_data['cumulative_weight'],
                        delta_weight=event_data.get('delta_weight', 0.0)
                    ))

                # 执行对齐
                aligner = VisualWeightAligner()
                aligned = aligner.align(detected_foods, weight_events)

                # 构建返回结果
                alignment_result = {
                    'aligned_foods': [
                        {
                            'class': a.food.class_name,
                            'weight': round(a.weight, 2),
                            'confidence': round(a.confidence_score, 3),
                            # 确保是布尔值
                            'matched': bool(a.weight_event_index >= 0),
                            'bbox': a.food.bbox
                        }
                        for a in aligned
                    ],
                    'metrics': AlignmentEvaluator.evaluate(aligned)
                }

                # 计算每个菜品的营养成分
                nutrition_results = []
                for a in aligned:
                    nutrition_data = NutritionCalculator.calculate_dish_nutrition(
                        a.food.class_name,
                        a.weight
                    )
                    if nutrition_data:
                        formatted = NutritionCalculator.format_nutrition_display(
                            nutrition_data)
                        nutrition_results.append(formatted)
                    else:
                        # 菜品不在数据库中
                        nutrition_results.append({
                            'dish_name': a.food.class_name,
                            'weight': f"{a.weight:.1f}g",
                            'error': '该菜品暂无营养数据'
                        })

                alignment_result['nutrition'] = nutrition_results

            except Exception as align_err:
                print(f"对齐错误: {align_err}")
                import traceback
                traceback.print_exc()  # 打印完整错误堆栈
                alignment_result = {'error': str(align_err)}

        # 保存检测记录到数据库
        record = DetectionRecord(
            user_id=session['user_id'],
            detected_objects=json.dumps(detections),
            detection_time=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'detections': detections,
            'count': len(detections),
            'alignment': alignment_result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    records = DetectionRecord.query.filter_by(user_id=session['user_id']).order_by(
        DetectionRecord.detection_time.desc()).all()
    return render_template('history.html', records=records)


# ==================== 管理员后台 ====================

def admin_required(f):
    """管理员权限验证装饰器"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/admin')
@admin_required
def admin_dashboard():
    # 统计数据
    total_users = User.query.count()
    total_detections = DetectionRecord.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_count = User.query.filter_by(is_admin=True).count()

    # 最近注册的用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # 最近的检测记录
    recent_detections = DetectionRecord.query.order_by(
        DetectionRecord.detection_time.desc()).limit(10).all()

    stats = {
        'total_users': total_users,
        'total_detections': total_detections,
        'active_users': active_users,
        'admin_count': admin_count
    }

    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users,
                           recent_detections=recent_detections)


@app.route('/admin/users')
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')

        if action == 'toggle_active':
            user.is_active = not user.is_active
            db.session.commit()
            # 确保返回标准布尔值
            return jsonify({'success': True, 'is_active': bool(user.is_active)})

        elif action == 'toggle_admin':
            if user.id == session['user_id']:
                return jsonify({'success': False, 'message': '不能修改自己的管理员权限'}), 400
            user.is_admin = not user.is_admin
            db.session.commit()
            # 确保返回标准布尔值
            return jsonify({'success': True, 'is_admin': bool(user.is_admin)})

        elif action == 'delete':
            if user.id == session['user_id']:
                return jsonify({'success': False, 'message': '不能删除自己的账号'}), 400
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True, 'message': '用户已删除'})

    # 获取用户的检测记录
    records = DetectionRecord.query.filter_by(user_id=user_id).order_by(
        DetectionRecord.detection_time.desc()).limit(10).all()
    diet_habit = DietHabit.query.filter_by(user_id=user_id).first()

    return render_template('admin/user_detail.html', user=user, records=records, diet_habit=diet_habit)


@app.route('/admin/detections')
@admin_required
def admin_detections():
    page = request.args.get('page', 1, type=int)
    per_page = 50

    detections = DetectionRecord.query.order_by(DetectionRecord.detection_time.desc(
    )).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin/detections.html', detections=detections)


@app.route('/admin/stats')
@admin_required
def admin_stats():
    # 按日期统计检测次数
    from sqlalchemy import func

    # 最近7天的检测统计
    daily_stats = db.session.query(
        func.date(DetectionRecord.detection_time).label('date'),
        func.count(DetectionRecord.id).label('count')
    ).group_by(func.date(DetectionRecord.detection_time)).order_by(
        func.date(DetectionRecord.detection_time).desc()).limit(7).all()

    # 用户注册统计
    user_stats = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).group_by(func.date(User.created_at)).order_by(func.date(User.created_at).desc()).limit(7).all()

    # 转换为字典格式，确保数据正确序列化
    daily_stats_list = [{'date': str(date), 'count': count}
                        for date, count in daily_stats]
    user_stats_list = [{'date': str(date), 'count': count}
                       for date, count in user_stats]

    return render_template('admin/stats.html', daily_stats=daily_stats_list, user_stats=user_stats_list)


@app.route('/admin/create_admin', methods=['POST'])
@admin_required
def create_admin():
    """创建管理员账号"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    new_admin = User(
        username=username,
        password_hash=generate_password_hash(password),
        is_admin=True,
        is_active=True
    )

    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'success': True, 'message': '管理员创建成功'})


@app.route('/weight_alignment_demo')
def weight_alignment_demo():
    """视觉-重量对齐算法演示页面"""
    return render_template('weight_alignment_demo.html')


if __name__ == '__main__':
    # 生产环境使用 gunicorn 运行，开发环境可以使用以下命令
    app.run(debug=False, host='0.0.0.0', port=5000)
