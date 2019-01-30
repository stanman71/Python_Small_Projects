from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import sys


""" ################# """
""" genernal settings """
""" ################# """

# Windows Home
sys.path.insert(0, "C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/RasPi/SmartHome/led/")
PATH_CSS = 'C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/RasPi/SmartHome/static/CDNJS/'

# Windows Work
#sys.path.insert(0, "C:/Users/mstan/GIT/Python_Projects/RasPi/SmartHome/led")
#PATH_CSS = 'C:/Users/mstan/GIT/Python_Projects/RasPi/SmartHome/static/CDNJS/'

# RasPi:
#sys.path.insert(0, "/home/pi/Python/SmartHome/led")
#PATH_CSS = '/home/pi/Python/static/CDNJS/'

from colorpicker_local import colorpicker
from LED_database import *
from LED_control import *
from LED_programs import *


""" ##### """
""" flask """
""" ##### """

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
colorpicker(app)


""" ######## """
""" database """
""" ######## """

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://python:python@localhost/raspi'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# define table structure
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email    = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role     = db.Column(db.String(20), server_default=("user"))

# create all database tables
db.create_all()

# create default user
if User.query.filter_by(username='default').first() is None:
    user = User(
        username='default',
        email='member@example.com',
        password=generate_password_hash('qwer1234', method='sha256'),
        role='superuser'
    )
    db.session.add(user)
    db.session.commit()


""" ############### """
""" Role Management """
""" ############### """

# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
    return wrap

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" ##### """
""" LogIn """
""" ##### """

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email    = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


""" ############ """
""" Landing Page """
""" ############ """

# landing page
@app.route('/', methods=['GET', 'POST'])
def index():

    UPDATE_LED()

    scene = 0
    brightness_global = 100
    value_1 = ""
    value_2 = ""
    value_3 = ""
    value_4 = ""
    value_5 = ""

    if request.method == "GET":     
        # Change scene   
        try:     
            scene = int(request.args.get("radio"))
            brightness_global = request.args.get("brightness_global")
            LED_SET_SCENE(scene,brightness_global)

            if scene == 1:
                value_1 = "checked = 'on'"
            if scene == 2:
                value_2 = "checked = 'on'"
            if scene == 3:
                value_3 = "checked = 'on'"
            if scene == 4:
                value_4 = "checked = 'on'"
            if scene == 5:
                value_5 = "checked = 'on'"        
        except:
            pass

    # get scene names
    scene_name_01 = GET_SCENE(1)[1]
    if scene_name_01 == None:
        scene_name_01 = ""
    scene_name_02 = GET_SCENE(2)[1]
    if scene_name_02 == None:
        scene_name_02 = ""    
    scene_name_03 = GET_SCENE(3)[1]
    if scene_name_03 == None:
        scene_name_03 = ""
    scene_name_04 = GET_SCENE(4)[1]
    if scene_name_04 == None:
        scene_name_04 = ""
    scene_name_05 = GET_SCENE(5)[1]
    if scene_name_05 == None:
        scene_name_05 = ""


    return render_template('index.html', 
                            scene_name_01=scene_name_01,
                            scene_name_02=scene_name_02,
                            scene_name_03=scene_name_03,
                            scene_name_04=scene_name_04,
                            scene_name_05=scene_name_05,
                            value_1=value_1,
                            value_2=value_2,
                            value_3=value_3,
                            value_4=value_4,
                            value_5=value_5,
                            brightness_global=brightness_global
                            )


""" ########## """
""" Sites User """
""" ########## """

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, login_check=False)

    return render_template('login.html', form=form)


# signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role="user")
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('signup.html', form=form)


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


# Dashboard user
@app.route('/dashboard/user/', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_user():
    user_list = User.query.all()
    return render_template('dashboard_user.html',
                            name=current_user.username,
                            user_list=user_list,
                            siteID="user" 
                            )


# Change user role
@app.route('/dashboard/user/role/<int:id>')
@login_required
@superuser_required
def promote(id):
    entry = User.query.get(id)
    entry.role = "superuser"
    db.session.commit()
    user_list = User.query.all()
    return redirect(url_for('dashboard_user'))


# Delete user
@app.route('/dashboard/user/delete/<int:id>')
@login_required
@superuser_required
def delete(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    user_list = User.query.all()
    return redirect(url_for('dashboard_user'))


""" ######### """
""" Sites LED """
""" ######### """

# LED scene 01
@app.route('/dashboard/LED/scene_01', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_01():
    scene = 1

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene  = []
        for i in range(1,10):
            rgb_scene.append(request.args.get("1 " + str(i)))
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    LED_SET_SCENE(1)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active01="active"
                            )


# LED scene 02
@app.route('/dashboard/LED/scene_02', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_02():
    scene = 2

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get("2 " + str(i)))  
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    LED_SET_SCENE(2)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active02="active"
                            )


# LED scene 03
@app.route('/dashboard/LED/scene_03', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_03():
    scene = 3

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get("3 " + str(i))) 
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    LED_SET_SCENE(3)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active03="active"
                            )


# LED scene 04
@app.route('/dashboard/LED/scene_04', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_04():
    scene = 4

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get("4 " + str(i)))      
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    LED_SET_SCENE(4)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active04="active"
                            )



# LED scene 05
@app.route('/dashboard/LED/scene_05', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_05():
    scene = 5

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get("5 " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 

    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    LED_SET_SCENE(5)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active05="active"
                            )


# Delete LED 
@app.route('/dashboard/LED/scene/delete/<int:scene>/<int:id>')
@login_required
@superuser_required
def delete_LED_scene_01(scene, id): 
    DEL_LED(scene, id)
    if scene == 1:
        return redirect(url_for('dashboard_LED_scene_01'))
    if scene == 2:
        return redirect(url_for('dashboard_LED_scene_02'))
    if scene == 3:
        return redirect(url_for('dashboard_LED_scene_03'))
    if scene == 4:
        return redirect(url_for('dashboard_LED_scene_04'))
    if scene == 5:
        return redirect(url_for('dashboard_LED_scene_05'))


# LED programs
@app.route('/dashboard/LED/programs', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_programs():

    program = ""

    if request.method == "GET": 
        # create a new program
        new_program = request.args.get("new_program") 
        if new_program is not None and new_program is not "":
            NEW_PROGRAM(new_program)

        # get the selected program
        get_Program = request.args.get("get_program") 
        if get_Program is not None:
            program = GET_PROGRAM(get_Program)

        # update programs, i = program ID
        for i in range(1,1000):
            update_Program = request.args.get(str(i))
            if update_Program is not None:
                UPDATE_PROGRAM(i, update_Program)

        # delete the selected program
        delete_Program = request.args.get("delete_program") 
        if delete_Program is not None:
            DELETE_PROGRAM(delete_Program)              

    """
    #zeilen auslesen:

    test = GET_PROGRAM("newww").content

    for line in test.splitlines():
        print("")
        print(line)
    """

    dropdown_list = GET_DROPDOWN_LIST_PROGRAMS()

    return render_template('dashboard_LED_programs.html',
                            dropdown_list=dropdown_list,
                            program=program
                            )


# LED settings
@app.route('/dashboard/LED/settings')
@login_required
@superuser_required
def dashboard_LED_settings():
    ip = GET_BRIDGE_IP()            
    LED_list = GET_LED()

    return render_template('dashboard_LED_settings.html', 
                            ip=ip,
                            LED_list=LED_list
                            )


""" ########### """
""" Sites Other """
""" ########### """

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Host files for colorpicker_local
@app.route('/get_media/<path:filename>', methods=['GET'])
def get_media(filename):
    return send_from_directory(PATH_CSS, filename)


if __name__ == '__main__':
    app.run(debug=True)
