from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from telegram import Bot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'  # قاعدة البيانات
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# إعداد بوت التليجرام
TELEGRAM_TOKEN = "توكن_البوت_هنا"
CHAT_ID = "رقم_التليجرام_خاصتك"
bot = Bot(token=TELEGRAM_TOKEN)

# نماذج قاعدة البيانات
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=False)
    status = db.Column(db.String(50), default="Pending")

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# واجهة المستخدم
@app.route('/')
def index():
    offers = Offer.query.all()
    return render_template('index.html', offers=offers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        new_user = User(username=username, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()

        # إرسال إشعار إلى تليجرام
        bot.send_message(chat_id=CHAT_ID, text=f"مستخدم جديد:\n👤 الاسم: {username}\n📱 الهاتف: {phone}")
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect('/')
        else:
            return "خطأ في تسجيل الدخول!"
    return render_template('login.html')

@app.route('/buy/<int:offer_id>', methods=['POST'])
def buy(offer_id):
    user_id = request.form['user_id']
    offer = Offer.query.get(offer_id)
    user = User.query.get(user_id)
    if user and offer:
        order = Order(user_id=user.id, offer_id=offer.id)
        db.session.add(order)
        db.session.commit()

        # إرسال إشعار بالشراء
        bot.send_message(chat_id=CHAT_ID, text=f"طلب شراء جديد:\n👤 المستخدم: {user.username}\n📱 الهاتف: {user.phone}\n💰 المنتج: {offer.title} - {offer.price}")
        return redirect('/')
    return "فشل العملية!"

@app.route('/add_offer', methods=['GET', 'POST'])
def add_offer():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        new_offer = Offer(title=title, description=description, price=price)
        db.session.add(new_offer)
        db.session.commit()
        return redirect('/')
    return render_template('add_offer.html')

if __name__ == '__main__':
    app.run(debug=True)
