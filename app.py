import os
import random
import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy import func

app = Flask(__name__)

# Подключение к БД из переменной окружения
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- ОПИСАНИЕ МОДЕЛЕЙ (строго по заданию) ---
class Coffee(db.Model):
    __tablename__ = 'coffee'
    id = db.Column(db.Integer, primary_key=True) # SERIAL
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200))
    description = db.Column(db.String(200))
    reviews = db.Column(ARRAY(db.String)) # VARCHAR[]

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True) # SERIAL
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50))
    patronymic = db.Column(db.String(50))
    has_sale = db.Column(db.Boolean)
    address = db.Column(JSON) # JSON
    coffee_id = db.Column(db.Integer, db.ForeignKey('coffee.id'))
    
    coffee = db.relationship('Coffee', backref='users')

# --- ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ (Аналог before_first_request) ---
def init_db():
    with app.app_context():
        db.create_all() # Создаем таблицы, если их нет
        
        # Если пользователи уже есть, выходим, чтобы не дублировать данные
        if User.query.first():
            return

        print("Идет заполнение базы данными с DummyJSON...")
        
        # 1. Получаем кофе
        coffee_resp = requests.get('https://dummyjson.com/products/search?q=coffee').json()
        if coffee_resp.get('products'):
            product = coffee_resp['products'][0]
            # Извлекаем комментарии из массива reviews
            reviews_list = [r['comment'] for r in product.get('reviews', [])]
            
            new_coffee = Coffee(
                title=product['title'],
                category=product['category'],
                description=product['description'],
                reviews=reviews_list
            )
            db.session.add(new_coffee)
            db.session.commit()
            coffee_id = new_coffee.id
        else:
            coffee_id = None

        # 2. Получаем 10 пользователей
        users_resp = requests.get('https://dummyjson.com/users?limit=10').json()
        for u in users_resp.get('users', []):
            new_user = User(
                name=f"{u['firstName']} {u['lastName']}",
                has_sale=random.choice([True, False]),
                address=u['address'],
                coffee_id=coffee_id # Привязываем к созданному кофе
            )
            db.session.add(new_user)
        db.session.commit()
        print("База данных успешно заполнена!")

# Вызываем заполнение при старте
init_db()

# --- РОУТЫ ---

@app.route("/")
def hello():
    return "Flask + Gunicorn + PostgreSQL + Docker Compose работают!"

# 1. Добавление пользователя
@app.route("/users/add", methods=['POST'])
def add_user():
    data = request.json
    coffee = Coffee.query.order_by(func.random()).first()
    
    new_user = User(
        name=data.get('name', 'Unknown'),
        has_sale=data.get('has_sale', False),
        address=data.get('address', {}),
        coffee_id=coffee.id if coffee else None
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "id": new_user.id,
        "name": new_user.name,
        "coffee_preference": new_user.coffee.title if new_user.coffee else None
    })

# 2. Поиск кофе по названию (Полнотекстовый поиск)
@app.route("/coffee/search")
def search_coffee():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Параметр q обязателен"}), 400
        
    # Используем to_tsvector и plainto_tsquery для полнотекстового поиска
    results = Coffee.query.filter(
        func.to_tsvector('english', Coffee.title).op('@@')(func.plainto_tsquery('english', query))
    ).all()
    
    return jsonify([{"id": c.id, "title": c.title} for c in results])

# 3. Список уникальных элементов в заметках (reviews)
@app.route("/coffee/unique-reviews")
def unique_reviews():
    # Разворачиваем массив в строки (unnest) и берем уникальные (distinct)
    unique_comments = db.session.query(func.unnest(Coffee.reviews).label('comment')).distinct().all()
    comments_list = [row[0] for row in unique_comments if row[0] is not None]
    return jsonify({"unique_reviews": comments_list})

# 4. Список пользователей, проживающих в стране
@app.route("/users/country")
def users_by_country():
    country = request.args.get('country', '')
    if not country:
        return jsonify({"error": "Параметр country обязателен"}), 400
        
    # Обращаемся к ключу 'country' внутри JSON поля address
    users = User.query.filter(User.address['country'].astext == country).all()
    
    return jsonify([{"id": u.id, "name": u.name, "country": u.address.get('country')} for u in users])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
