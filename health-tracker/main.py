from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date , datetime , timedelta

app = Flask(__name__)
app.secret_key = "supersekrit"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_tracker.db'
db = SQLAlchemy(app)

google_client_id = "your_google_clientid_here"
google_client_secret = "your_google_client_secret_here"

blueprint = make_google_blueprint(
    client_id=google_client_id,
    client_secret=google_client_secret,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

def set_daily_goals(user):
    if user.gender == "Male":
        if user.age < 18:
            user.daily_goal_water = user.daily_goal_water or 2100
            user.daily_goal_calories = user.daily_goal_calories or 2500
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 300
            user.daily_goal_proteins = user.daily_goal_proteins or 75
            user.daily_goal_fats = user.daily_goal_fats or 70
        elif user.age < 55:
            user.daily_goal_water = user.daily_goal_water or 3000
            user.daily_goal_calories = user.daily_goal_calories or 2500
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 300
            user.daily_goal_proteins = user.daily_goal_proteins or 75
            user.daily_goal_fats = user.daily_goal_fats or 70
        else:
            user.daily_goal_water = user.daily_goal_water or 2600
            user.daily_goal_calories = user.daily_goal_calories or 2300
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 280
            user.daily_goal_proteins = user.daily_goal_proteins or 70
            user.daily_goal_fats = user.daily_goal_fats or 65
    elif user.gender == "Female":
        if user.age < 18:
            user.daily_goal_water = user.daily_goal_water or 1900
            user.daily_goal_calories = user.daily_goal_calories or 2000
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 230
            user.daily_goal_proteins = user.daily_goal_proteins or 70
            user.daily_goal_fats = user.daily_goal_fats or 55
        elif user.age < 55:
            user.daily_goal_water = user.daily_goal_water or 2700
            user.daily_goal_calories = user.daily_goal_calories or 2000
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 230
            user.daily_goal_proteins = user.daily_goal_proteins or 70
            user.daily_goal_fats = user.daily_goal_fats or 55
        else:
            user.daily_goal_water = user.daily_goal_water or 2200
            user.daily_goal_calories = user.daily_goal_calories or 1800
            user.daily_goal_carbohydrates = user.daily_goal_carbohydrates or 210
            user.daily_goal_proteins = user.daily_goal_proteins or 65
            user.daily_goal_fats = user.daily_goal_fats or 50
    db.session.commit()

preset_exercises = [
    {"name": "Push-ups", "description": "Do push-ups.", "unit": "reps", "calories_per_unit": 0.29},
    {"name": "Squats", "description": "Do squats.", "unit": "reps", "calories_per_unit": 0.32},
    {"name": "Plank", "description": "Hold a plank.", "unit": "minutes", "calories_per_unit": 5},
    {"name": "Burpees", "description": "Do burpees.", "unit": "reps", "calories_per_unit": 0.44},
    {"name": "Jumping Jacks", "description": "Do jumping jacks.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Mountain Climbers", "description": "Do mountain climbers.", "unit": "reps", "calories_per_unit": 0.4},
    {"name": "Lunges", "description": "Do lunges.", "unit": "reps", "calories_per_unit": 0.3},
    {"name": "Bicep Curls", "description": "Do bicep curls.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Tricep Dips", "description": "Do tricep dips.", "unit": "reps", "calories_per_unit": 0.25},
    {"name": "Bicycle Crunches", "description": "Do bicycle crunches.", "unit": "reps", "calories_per_unit": 0.22},
    {"name": "Sit-ups", "description": "Do sit-ups.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Leg Raises", "description": "Do leg raises.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "High Knees", "description": "Do high knees.", "unit": "minutes", "calories_per_unit": 6},
    {"name": "Russian Twists", "description": "Do Russian twists.", "unit": "reps", "calories_per_unit": 0.18},
    {"name": "Jump Rope", "description": "Jump rope.", "unit": "minutes", "calories_per_unit": 10},
    {"name": "Box Jumps", "description": "Do box jumps.", "unit": "reps", "calories_per_unit": 0.5},
    {"name": "Calf Raises", "description": "Do calf raises.", "unit": "reps", "calories_per_unit": 0.12},
    {"name": "Shoulder Press", "description": "Do shoulder presses.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Deadlift", "description": "Do deadlifts.", "unit": "reps", "calories_per_unit": 0.4},
    {"name": "Pull-ups", "description": "Do pull-ups.", "unit": "reps", "calories_per_unit": 0.35},
    {"name": "Chin-ups", "description": "Do chin-ups.", "unit": "reps", "calories_per_unit": 0.3},
    {"name": "Rowing", "description": "Row on a machine.", "unit": "minutes", "calories_per_unit": 7},
    {"name": "Treadmill Running", "description": "Run on a treadmill.", "unit": "minutes", "calories_per_unit": 10},
    {"name": "Cycling", "description": "Cycle on a stationary bike.", "unit": "minutes", "calories_per_unit": 7},
    {"name": "Squat Jumps", "description": "Do squat jumps.", "unit": "reps", "calories_per_unit": 0.42},
    {"name": "Reverse Crunches", "description": "Do reverse crunches.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Flutter Kicks", "description": "Do flutter kicks.", "unit": "reps", "calories_per_unit": 0.1},
    {"name": "Wall Sit", "description": "Hold a wall sit.", "unit": "minutes", "calories_per_unit": 4},
    {"name": "Side Plank", "description": "Hold a side plank.", "unit": "minutes", "calories_per_unit": 4},
    {"name": "Step-Ups", "description": "Do step-ups.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Hamstring Curls", "description": "Do hamstring curls.", "unit": "reps", "calories_per_unit": 0.18},
    {"name": "Hip Thrusts", "description": "Do hip thrusts.", "unit": "reps", "calories_per_unit": 0.25},
    {"name": "Dumbbell Squats", "description": "Do dumbbell squats.", "unit": "reps", "calories_per_unit": 0.3},
    {"name": "Front Raises", "description": "Do front raises.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Side Lateral Raises", "description": "Do side lateral raises.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Incline Push-ups", "description": "Do incline push-ups.", "unit": "reps", "calories_per_unit": 0.27},
    {"name": "Decline Push-ups", "description": "Do decline push-ups.", "unit": "reps", "calories_per_unit": 0.35},
    {"name": "Boxing", "description": "Shadow box or use a bag.", "unit": "minutes", "calories_per_unit": 8},
    {"name": "Elliptical", "description": "Exercise on the elliptical.", "unit": "minutes", "calories_per_unit": 6.5},
    {"name": "Kickbacks", "description": "Do kickbacks.", "unit": "reps", "calories_per_unit": 0.18},
    {"name": "Side Lunges", "description": "Do side lunges.", "unit": "reps", "calories_per_unit": 0.3},
    {"name": "Reverse Lunges", "description": "Do reverse lunges.", "unit": "reps", "calories_per_unit": 0.3},
    {"name": "Bird Dogs", "description": "Do bird dogs.", "unit": "reps", "calories_per_unit": 0.12},
    {"name": "Donkey Kicks", "description": "Do donkey kicks.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Supermans", "description": "Do supermans.", "unit": "reps", "calories_per_unit": 0.15},
    {"name": "Jump Squats", "description": "Do jump squats.", "unit": "reps", "calories_per_unit": 0.35},
    {"name": "Battle Ropes", "description": "Use battle ropes.", "unit": "minutes", "calories_per_unit": 10},
    {"name": "Scissor Kicks", "description": "Do scissor kicks.", "unit": "reps", "calories_per_unit": 0.1},
    {"name": "Toe Touches", "description": "Do toe touches.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Bicycle Kicks", "description": "Do bicycle kicks.", "unit": "reps", "calories_per_unit": 0.18},
    {"name": "Arm Circles", "description": "Do arm circles.", "unit": "minutes", "calories_per_unit": 4},
    {"name": "Leg Curls", "description": "Do leg curls.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Bent-Over Rows", "description": "Do bent-over rows.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Pull Downs", "description": "Do pull downs.", "unit": "reps", "calories_per_unit": 0.2},
    {"name": "Good Mornings", "description": "Do good mornings.", "unit": "reps", "calories_per_unit": 0.25},
    {"name": "Skaters", "description": "Do skaters.", "unit": "reps", "calories_per_unit": 0.3}
]
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    daily_goal_water = db.Column(db.Integer)
    daily_goal_calories = db.Column(db.Integer)
    daily_goal_carbohydrates = db.Column(db.Float)
    daily_goal_proteins = db.Column(db.Float)
    daily_goal_fats = db.Column(db.Float)

class WaterEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class FoodEntry(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item = db.Column(db.String(80), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

def get_total_water_today(username):
    user = User.query.filter_by(username=username).first()
    today_entries = WaterEntry.query.filter_by(user_id=user.id).filter(WaterEntry.timestamp >= db.func.date('now')).all()
    return sum(entry.amount for entry in today_entries)

def get_food_entries(username):
    user = User.query.filter_by(username=username).first()
    return FoodEntry.query.filter_by(user_id=user.id).all()

def get_daily_nutrient_totals(username):
    user = User.query.filter_by(username=username).first()
    today = date.today()
    
    today_food_entries = FoodEntry.query.filter(
        FoodEntry.user_id == user.id,
        db.func.date(FoodEntry.timestamp) == today
    ).all()
    
    total_calories = sum(entry.calories for entry in today_food_entries)
    total_carbohydrates = sum(entry.carbohydrates for entry in today_food_entries)
    total_proteins = sum(entry.proteins for entry in today_food_entries)
    total_fats = sum(entry.fats for entry in today_food_entries)
    total_water = get_total_water_today(username)
    
    return {
        "calories": total_calories,
        "carbohydrates": total_carbohydrates,
        "proteins": total_proteins,
        "fats": total_fats,
        "water": total_water
    }

@app.route("/food_tracker", methods=['GET', 'POST'])
def food_tracker():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    food_items = [
    {"name": "Apple", "calories": 95, "carbohydrates": 25, "proteins": 0.5, "fats": 0.3},
    {"name": "Banana", "calories": 105, "carbohydrates": 27, "proteins": 1.3, "fats": 0.3},
    {"name": "Orange", "calories": 62, "carbohydrates": 15.4, "proteins": 1.2, "fats": 0.2},
    {"name": "Strawberries", "calories": 49, "carbohydrates": 11.7, "proteins": 1, "fats": 0.5},
    {"name": "Blueberries", "calories": 84, "carbohydrates": 21.4, "proteins": 1.1, "fats": 0.5},
    {"name": "Pineapple", "calories": 82, "carbohydrates": 21.6, "proteins": 0.9, "fats": 0.2},
    {"name": "Mango", "calories": 99, "carbohydrates": 24.7, "proteins": 1.4, "fats": 0.6},
    {"name": "Watermelon", "calories": 30, "carbohydrates": 8, "proteins": 0.6, "fats": 0.2},
    {"name": "Peach", "calories": 59, "carbohydrates": 14, "proteins": 1.4, "fats": 0.4},
    {"name": "Plum", "calories": 30, "carbohydrates": 7.5, "proteins": 0.5, "fats": 0.2},
    {"name": "Grapes", "calories": 69, "carbohydrates": 18, "proteins": 0.7, "fats": 0.2},
    {"name": "Raspberries", "calories": 52, "carbohydrates": 12, "proteins": 1.5, "fats": 0.6},
    {"name": "Papaya", "calories": 59, "carbohydrates": 15, "proteins": 1, "fats": 0.4},
    {"name": "Kiwi", "calories": 42, "carbohydrates": 10, "proteins": 0.8, "fats": 0.4},
    {"name": "Cantaloupe", "calories": 34, "carbohydrates": 8, "proteins": 0.8, "fats": 0.2},
    
    {"name": "Broccoli", "calories": 55, "carbohydrates": 11, "proteins": 4, "fats": 0.6},
    {"name": "Carrot", "calories": 25, "carbohydrates": 6, "proteins": 0.6, "fats": 0.1},
    {"name": "Spinach", "calories": 23, "carbohydrates": 3.6, "proteins": 2.9, "fats": 0.4},
    {"name": "Tomato", "calories": 22, "carbohydrates": 4.8, "proteins": 1.1, "fats": 0.2},
    {"name": "Sweet Potato", "calories": 86, "carbohydrates": 20.1, "proteins": 1.6, "fats": 0.1},
    {"name": "Cauliflower", "calories": 25, "carbohydrates": 5, "proteins": 1.9, "fats": 0.3},
    {"name": "Bell Pepper", "calories": 24, "carbohydrates": 6, "proteins": 1, "fats": 0.2},
    {"name": "Asparagus", "calories": 20, "carbohydrates": 3.7, "proteins": 2.2, "fats": 0.2},
    {"name": "Zucchini", "calories": 17, "carbohydrates": 3.1, "proteins": 1.2, "fats": 0.3},
    {"name": "Green Beans", "calories": 31, "carbohydrates": 7, "proteins": 2, "fats": 0.2},
    {"name": "Kale", "calories": 33, "carbohydrates": 6.7, "proteins": 2.9, "fats": 0.6},
    {"name": "Cabbage", "calories": 25, "carbohydrates": 5.8, "proteins": 1.3, "fats": 0.1},
    {"name": "Celery", "calories": 14, "carbohydrates": 3, "proteins": 0.7, "fats": 0.2},
    {"name": "Onion", "calories": 40, "carbohydrates": 9.3, "proteins": 1.1, "fats": 0.1},
    
    {"name": "Chicken Breast", "calories": 165, "carbohydrates": 0, "proteins": 31, "fats": 3.6},
    {"name": "Egg", "calories": 78, "carbohydrates": 0.6, "proteins": 6, "fats": 5},
    {"name": "Tofu", "calories": 76, "carbohydrates": 1.9, "proteins": 8, "fats": 4.8},
    {"name": "Salmon", "calories": 208, "carbohydrates": 0, "proteins": 20, "fats": 13},
    {"name": "Lentils", "calories": 116, "carbohydrates": 20, "proteins": 9, "fats": 0.4},
    {"name": "Black Beans", "calories": 114, "carbohydrates": 20, "proteins": 7.6, "fats": 0.5},
    {"name": "Turkey Breast", "calories": 135, "carbohydrates": 0, "proteins": 30, "fats": 0.7},
    {"name": "Ground Beef", "calories": 250, "carbohydrates": 0, "proteins": 19, "fats": 20},
    {"name": "Shrimp", "calories": 99, "carbohydrates": 0.2, "proteins": 24, "fats": 0.3},
    {"name": "Edamame", "calories": 121, "carbohydrates": 9.4, "proteins": 11, "fats": 5},
    {"name": "Cottage Cheese", "calories": 98, "carbohydrates": 3.4, "proteins": 11, "fats": 4.3},
    
    {"name": "Brown Rice", "calories": 216, "carbohydrates": 44.8, "proteins": 5, "fats": 1.8},
    {"name": "Quinoa", "calories": 120, "carbohydrates": 21.3, "proteins": 4.1, "fats": 1.9},
    {"name": "Oatmeal", "calories": 158, "carbohydrates": 27.3, "proteins": 6, "fats": 3.2},
    {"name": "Whole Wheat Bread", "calories": 69, "carbohydrates": 11.6, "proteins": 3.6, "fats": 1},
    {"name": "Pasta", "calories": 131, "carbohydrates": 25, "proteins": 5, "fats": 1.1},
    {"name": "Couscous", "calories": 176, "carbohydrates": 36.5, "proteins": 5.9, "fats": 0.3},
    {"name": "Bulgur", "calories": 151, "carbohydrates": 33.8, "proteins": 5.6, "fats": 0.4},
    {"name": "Millet", "calories": 207, "carbohydrates": 41.2, "proteins": 6.1, "fats": 1.7},
    {"name": "Barley", "calories": 354, "carbohydrates": 73.5, "proteins": 12.5, "fats": 2.3},
    {"name": "Buckwheat", "calories": 92, "carbohydrates": 20, "proteins": 3, "fats": 0.6},
    
    {"name": "Milk", "calories": 42, "carbohydrates": 5, "proteins": 3.4, "fats": 1},
    {"name": "Yogurt", "calories": 59, "carbohydrates": 3.6, "proteins": 10, "fats": 0.4},
    {"name": "Cheddar Cheese", "calories": 113, "carbohydrates": 0.4, "proteins": 7, "fats": 9},
    {"name": "Mozzarella", "calories": 85, "carbohydrates": 1, "proteins": 6, "fats": 6},
    {"name": "Butter", "calories": 102, "carbohydrates": 0, "proteins": 0.1, "fats": 11.5},
    {"name": "Cream Cheese", "calories": 99, "carbohydrates": 1.6, "proteins": 1.7, "fats": 10},
    
    {"name": "Almonds", "calories": 164, "carbohydrates": 6.1, "proteins": 6, "fats": 14.2},
    {"name": "Chia Seeds", "calories": 138, "carbohydrates": 12, "proteins": 4.7, "fats": 8.7},
    {"name": "Peanut Butter", "calories": 190, "carbohydrates": 6, "proteins": 8, "fats": 16},
    {"name": "Walnuts", "calories": 185, "carbohydrates": 3.9, "proteins": 4.3, "fats": 18.5},
    {"name": "Pistachios", "calories": 159, "carbohydrates": 8, "proteins": 5.7, "fats": 12.9},
    {"name": "Sunflower Seeds", "calories": 164, "carbohydrates": 6.8, "proteins": 5.8, "fats": 14.6},
    
    {"name": "Coffee (black)", "calories": 2, "carbohydrates": 0, "proteins": 0.3, "fats": 0},
    {"name": "Orange Juice", "calories": 112, "carbohydrates": 26, "proteins": 1.7, "fats": 0.3},
    {"name": "Green Tea", "calories": 0, "carbohydrates": 0, "proteins": 0, "fats": 0},
    {"name": "Red Wine", "calories": 125, "carbohydrates": 4, "proteins": 0.1, "fats": 0},
    {"name": "Beer", "calories": 154, "carbohydrates": 13, "proteins": 1.6, "fats": 0},
    {"name": "Coconut Water", "calories": 46, "carbohydrates": 9, "proteins": 2, "fats": 0.5},
    
    {"name": "Dark Chocolate", "calories": 155, "carbohydrates": 12.8, "proteins": 1.4, "fats": 9},
    {"name": "Popcorn", "calories": 31, "carbohydrates": 6.2, "proteins": 1, "fats": 0.4},
    {"name": "Potato Chips", "calories": 152, "carbohydrates": 15, "proteins": 2, "fats": 10},
    {"name": "Ice Cream", "calories": 137, "carbohydrates": 16, "proteins": 2.3, "fats": 7},
    {"name": "Honey", "calories": 64, "carbohydrates": 17.3, "proteins": 0.1, "fats": 0},
    {"name": "Maple Syrup", "calories": 52, "carbohydrates": 13.5, "proteins": 0, "fats": 0}]

    selected_food = None
    if request.method == 'POST':
        food_item_name = request.form['food_item']
        selected_food = next((food for food in food_items if food["name"] == food_item_name), None)
        if 'submit' in request.form:
            new_food = FoodEntry(
                user_id=user['id'],
                food_item=selected_food['name'],
                calories=selected_food['calories'],
                carbohydrates=selected_food['carbohydrates'],
                proteins=selected_food['proteins'],
                fats=selected_food['fats']
            )
            db.session.add(new_food)
            db.session.commit()
            flash(f"Added food item: {selected_food['name']}!", "success")

    food_entries = get_food_entries(user['username'])
    return render_template('food_tracker.html', food_entries=food_entries, food_items=food_items, selected_food=selected_food)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    user_session = session.get('user')
    if not user_session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_session['username'] = request.form['username']
        user_session['age'] = request.form['age']
        user_session['gender'] = request.form['gender']
        
        user_db = User.query.get(user_session['id'])
        user_db.username = user_session['username']
        user_db.age = user_session['age']
        user_db.gender = user_session['gender']
        
        set_daily_goals(user_db)

        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return render_template('profile.html', user=user_session)

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')


@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    selected_exercise = None
    calories_burned = None
    exercise_done = False

    if request.method == 'POST':
        exercise_name = request.form.get('exercise')
        amount = request.form.get('amount')
        action = request.form.get('action')

        if action == 'calculate':
            if not exercise_name or not amount:
                flash('Please select an exercise and enter an amount.', 'danger')
                return render_template('exercise.html', preset_exercises=preset_exercises)

            try:
                amount = int(amount)
            except ValueError:
                flash('Please enter a valid number for the amount.', 'danger')
                return render_template('exercise.html', preset_exercises=preset_exercises)

            selected_exercise = next((ex for ex in preset_exercises if ex['name'] == exercise_name), None)
            
            if selected_exercise:
                calories_burned = amount * selected_exercise['calories_per_unit']
                calories_burned = round(calories_burned, 2)

        elif action == 'done':
            exercise_done = True
            selected_exercise = None
            flash('Good job! Keep it up!', 'success')

    return render_template('exercise.html', preset_exercises=preset_exercises,
                           selected_exercise=selected_exercise, calories_burned=calories_burned,
                           exercise_done=exercise_done)

@app.route('/logout')
def logout():
    if google.authorized:
        token = google.token["access_token"]
        resp = requests.get(f"https://accounts.google.com/o/oauth2/revoke?token={token}")
        if resp.status_code == 200:
            flash("Logged out successfully.", "success")
        else:
            flash("Error to logout.", "danger")
    
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/google/callback', methods=['GET', 'POST'])
def callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get('/oauth2/v2/userinfo')
        assert resp.ok, resp.text
    except Exception:
        flash('Session expired, please try again.', 'danger')
        return redirect(url_for('google.login'))

    user_info = resp.json()
    username = user_info['email']
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, password='google', age=None, gender=None)
        db.session.add(user)
        db.session.commit()
        session['user'] = {
            'id': user.id,
            'username': user.username,
            'age': user.age,
            'gender': user.gender,
            'daily_goal_water': user.daily_goal_water,
            'daily_goal_calories': user.daily_goal_calories,
            'daily_goal_carbohydrates': user.daily_goal_carbohydrates,
            'daily_goal_proteins': user.daily_goal_proteins,
            'daily_goal_fats': user.daily_goal_fats
        }
        return redirect(url_for('set_profile'))

    session['user'] = {
        'id': user.id,
        'username': user.username,
        'age': user.age,
        'gender': user.gender,
        'daily_goal_water': user.daily_goal_water,
        'daily_goal_calories': user.daily_goal_calories,
        'daily_goal_carbohydrates': user.daily_goal_carbohydrates,
        'daily_goal_proteins': user.daily_goal_proteins,
        'daily_goal_fats': user.daily_goal_fats
    }
    return redirect(url_for('dashboard'))

@app.route('/set_profile', methods=['GET', 'POST'])
def set_profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        user_db = User.query.get(user['id'])
        user_db.age = age
        user_db.gender = gender
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        session['user']['age'] = age
        session['user']['gender'] = gender
        
        return redirect(url_for('dashboard'))
    
    return render_template('set_profile.html', user=user)
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user'] = {
                'id': user.id,
                'username': user.username,
                'age': user.age,
                'gender': user.gender,
            }
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = int(request.form['age'])
        gender = request.form['gender']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, age=age, gender=gender)
        
        db.session.add(new_user)
        db.session.commit()
        
        set_daily_goals(new_user)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/dashboard")
def dashboard():
    username = session.get('user', {}).get('username')
    if not username:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()

    set_daily_goals(user)

    daily_totals = get_daily_nutrient_totals(username)
    daily_water = get_total_water_today(username)
    
    progress = {
        "calories": min((daily_totals["calories"] / user.daily_goal_calories) * 100, 100),
        "carbohydrates": min((daily_totals["carbohydrates"] / user.daily_goal_carbohydrates) * 100, 100),
        "proteins": min((daily_totals["proteins"] / user.daily_goal_proteins) * 100, 100),
        "fats": min((daily_totals["fats"] / user.daily_goal_fats) * 100, 100),
        "water": min((daily_water / user.daily_goal_water) * 100, 100)
    }

    return render_template('dashboard.html', user=user, progress=progress, daily_totals=daily_totals)

@app.route('/')
def index():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/water_tracker', methods=['POST', 'GET'])
def water_tracker():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        water_amount = request.form['water_amount']
        new_entry = WaterEntry(user_id=user['id'], amount=float(water_amount))
        db.session.add(new_entry)
        db.session.commit()
    
    total_water_drank = get_total_water_today(user['username'])
    water_entries = WaterEntry.query.filter_by(user_id=user['id']).all()
    
    return render_template('water_tracker.html', user=user, total_water_drank=total_water_drank, water_entries=water_entries)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

