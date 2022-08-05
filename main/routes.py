from main import app
#import os
from flask import render_template, url_for, flash, redirect,request
from main.forms import RegistrationForm, LoginForm
from main.models import User,Hotel,Booking
from flask_login import login_user, current_user, logout_user, login_required
from main import db, bcrypt,admin
from flask_admin.contrib.sqla import ModelView
import datetime

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, phone=form.phone.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    else:
        flash('Your account has not created!', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/book_hotel", methods=['GET', 'POST'])
def book_hotel():
    q = request.args.get('q')
    if q:
        hotels = Hotel.query.filter(Hotel.city.contains(q))
    else:
        hotels=Hotel.query.all()
    return render_template('book_hotel.html', hotels=hotels)

@app.route("/bookings", methods=['GET', 'POST'])
@login_required
def bookings():
    bookings = Booking.query.filter_by(touirst_id = current_user.id)
    hotels=Hotel.query.all()
    return render_template('bookings.html',bookings=bookings,hotels=hotels)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/hotel_info/<int:hotel_id>", methods=['GET', 'POST'])
@login_required
def hotel_info(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    bookings = Booking.query.filter_by(touirst_id = current_user.id,hotel_id=hotel_id)
    if request.method == 'POST':
        rooms = request.form['Rooms']
        arrival = datetime.datetime.strptime(request.form['Arrival'],'%Y-%m-%d')
        departure= datetime.datetime.strptime(request.form['Departure'],'%Y-%m-%d')
        if(rooms<=0):
            flash('Wrong rooms input!', 'danger')
            return redirect(url_for('book_hotel'))
        if(hotel.availability<int(rooms)):
            flash('Insufficient rooms!', 'danger')
            return redirect(url_for('book_hotel'))
        if(arrival>departure):
            flash('Wrong date input!', 'danger')
            return redirect(url_for('book_hotel'))
        for booking in bookings:
            if(bookings.arrival>=arrival and bookings.departure>=departure):
                flash('dates clashing!', 'danger')
                return redirect(url_for('book_hotel'))
            elif(bookings.arrival>=arrival and bookings.departure<=departure):
                flash('dates clashing!', 'danger')
                return redirect(url_for('book_hotel'))
            elif(bookings.arrival<=arrival and bookings.departure>=departure):
                flash('dates clashing!', 'danger')
                return redirect(url_for('book_hotel'))
            elif(bookings.arrival<=arrival and bookings.departure<=departure):
                flash('dates clashing!', 'danger')
                return redirect(url_for('book_hotel'))
            
        hotel.availability = hotel.availability - int(rooms)
        booking = Booking(touirst_id=current_user.id,hotel_id=hotel.id,arrival=arrival,departure=departure,rooms=int(rooms))
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('bookings'))
    return render_template('hotel_info.html', name=hotel.name, hotel=hotel)

@app.route("/cancel_booking/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    hotel= Hotel.query.get_or_404(booking.hotel_id)
    hotel.availability = hotel.availability+booking.rooms
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('bookings'))

@app.route("/map_view")
def map_view():
    markers =[]
    hotels=Hotel.query.all()
    for hotel in hotels:
        #st='Hotel Name:%s Rooms Available:%s'%(hotel.name,hotel.availability)
        markers.append(
        {
            'lat':hotel.latitude,
            'lon':hotel.longitude,
            'name':hotel.name,
            'availability':hotel.availability
        }
        )
        
    return render_template('map.html',markers=markers)

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def adminfunc():
    pass
class myModelView(ModelView):
    def is_accessible(self):
        return (True)
    
admin.add_view(myModelView(User,db.session))
admin.add_view(myModelView(Hotel,db.session))
admin.add_view(myModelView(Booking,db.session))