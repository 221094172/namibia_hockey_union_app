from flask import render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy import or_
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
import config
from models import User, Team, Player, Event, Notification
from forms import (
    RegistrationForm, LoginForm, TeamRegistrationForm, 
    PlayerRegistrationForm, EventRegistrationForm, 
    TeamEventRegistrationForm, NotificationForm, SearchForm,
    AdminRegistrationForm
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from utils import save_optimized_image, delete_image

# Define upload directories
UPLOAD_FOLDERS = {
    'logos': os.path.join('static', 'uploads', 'logos'),
    'players': os.path.join('static', 'uploads', 'players'),
    'profiles': os.path.join('static', 'uploads', 'profiles')
}

# Create upload directories if they don't exist
def create_upload_dirs():
    # Create base uploads directory
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    
    # Create each directory if it doesn't exist
    for directory in UPLOAD_FOLDERS.values():
        os.makedirs(directory, exist_ok=True)

# Ensure upload directories exist
create_upload_dirs()

@app.route('/')
def index():
    # Get current datetime
    now = datetime.utcnow()
    
    # Get upcoming events (limit to 5)
    upcoming_events = Event.query.filter(Event.start_date > now).order_by(Event.start_date).limit(5).all()
    
    # Get recent notifications (limit to 5)
    recent_notifications = Notification.query.filter_by(is_global=True).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('index.html', upcoming_events=upcoming_events, recent_notifications=recent_notifications, now=now)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Get current datetime
    now = datetime.utcnow()
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, now=now)

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Get current datetime
    now = datetime.utcnow()
    
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        # Verify admin credentials
        if form.email.data != config.ADMIN_EMAIL or form.admin_code.data != config.ADMIN_SECRET_CODE:
            flash('Invalid admin credentials. Please check your email and admin code.', 'danger')
            return render_template('admin_register.html', form=form, now=now)
        
        # Create admin user
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
        
        flash('Admin account has been created! You can now log in with admin privileges.', 'success')
        return redirect(url_for('login'))
    
    return render_template('admin_register.html', form=form, now=now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Get current datetime
    now = datetime.utcnow()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form, now=now)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current datetime
    now = datetime.utcnow()
    
    # Get teams managed by current user
    user_teams = Team.query.filter_by(manager_id=current_user.id).all()
    
    # Get all players in user's teams
    players = []
    for team in user_teams:
        players.extend(team.players)
    
    # Remove duplicates
    players = list(set(players))
    
    # Get events related to user's teams
    events = []
    for team in user_teams:
        events.extend(team.events)
    
    # Remove duplicates
    events = list(set(events))
    
    # Get notifications for user's teams or global notifications
    notifications = Notification.query.filter(
        (Notification.is_global == True) | 
        (Notification.target_team_id.in_([team.id for team in user_teams]))
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                          teams=user_teams, 
                          players=players, 
                          events=events,
                          notifications=notifications,
                          now=now)

@app.route('/teams/register', methods=['GET', 'POST'])
@login_required
def register_team():
    # Get current datetime
    now = datetime.utcnow()
    
    form = TeamRegistrationForm()
    if form.validate_on_submit():
        logo_url = None
        if form.logo.data:
            # Save and optimize the logo image
            logo_url = save_optimized_image(
                form.logo.data, 
                UPLOAD_FOLDERS['logos'], 
                image_type='logo'
            )
        
        team = Team()
        team.name = form.name.data
        team.division = form.division.data
        team.founded_year = form.founded_year.data
        team.logo_url = logo_url
        team.manager_id = current_user.id
        db.session.add(team)
        db.session.commit()
        flash('Team has been registered successfully!', 'success')
        return redirect(url_for('team_list'))
    
    return render_template('team_registration.html', form=form, now=now)

@app.route('/teams')
@login_required
def team_list():
    # Get current datetime
    now = datetime.utcnow()
    
    teams = Team.query.filter_by(manager_id=current_user.id).all()
    return render_template('team_list.html', teams=teams, now=now)

@app.route('/teams/<int:team_id>')
@login_required
def team_details(team_id):
    # Get current datetime
    now = datetime.utcnow()
    
    team = Team.query.get_or_404(team_id)
    
    # Check if current user is the team manager or admin
    if team.manager_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this team.', 'danger')
        return redirect(url_for('team_list'))
    
    return render_template('team_details.html', team=team, now=now)

@app.route('/teams/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    # Get current datetime
    now = datetime.utcnow()
    
    team = Team.query.get_or_404(team_id)
    
    # Check if current user is the team manager or admin
    if team.manager_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this team.', 'danger')
        return redirect(url_for('team_list'))
    
    form = TeamRegistrationForm()
    
    if request.method == 'GET':
        # Populate form with existing data
        form.name.data = team.name
        form.division.data = team.division
        form.founded_year.data = team.founded_year
    
    if form.validate_on_submit():
        # Update team information
        team.name = form.name.data
        team.division = form.division.data
        team.founded_year = form.founded_year.data
        
        # Update logo if new one is provided
        if form.logo.data:
            # Save and optimize the new logo
            new_logo_url = save_optimized_image(
                form.logo.data, 
                UPLOAD_FOLDERS['logos'], 
                image_type='logo'
            )
            
            if new_logo_url:
                # Delete old logo file if it exists
                if team.logo_url:
                    delete_image(team.logo_url)
                
                # Update the team's logo URL
                team.logo_url = new_logo_url
        
        db.session.commit()
        flash('Team information has been updated successfully!', 'success')
        return redirect(url_for('team_details', team_id=team.id))
    
    return render_template('edit_team.html', form=form, team=team, now=now)

@app.route('/players/register', methods=['GET', 'POST'])
@login_required
def register_player():
    # Get current datetime
    now = datetime.utcnow()
    
    form = PlayerRegistrationForm()
    
    # Populate team_id dropdown with teams managed by current user
    form.team_id.choices = [(team.id, team.name) for team in Team.query.filter_by(manager_id=current_user.id).all()]
    
    if form.validate_on_submit():
        photo_url = None
        if form.photo.data:
            # Save and optimize the player photo
            photo_url = save_optimized_image(
                form.photo.data, 
                UPLOAD_FOLDERS['players'], 
                image_type='player'
            )
        
        player = Player()
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.date_of_birth = form.date_of_birth.data
        player.position = form.position.data
        player.jersey_number = form.jersey_number.data
        player.email = form.email.data
        player.phone = form.phone.data
        player.photo_url = photo_url
        
        team = Team.query.get(form.team_id.data)
        if team and team.manager_id == current_user.id:
            player.teams.append(team)
            db.session.add(player)
            db.session.commit()
            flash('Player has been registered successfully!', 'success')
            return redirect(url_for('player_list'))
        else:
            flash('Invalid team selected.', 'danger')
    
    return render_template('player_registration.html', form=form, now=now)

@app.route('/players')
@login_required
def player_list():
    # Get current datetime
    now = datetime.utcnow()
    
    # Get all players from teams managed by current user
    managed_teams = Team.query.filter_by(manager_id=current_user.id).all()
    players = []
    
    for team in managed_teams:
        for player in team.players:
            if player not in players:
                players.append(player)
    
    return render_template('player_list.html', players=players, teams=managed_teams, now=now)
    
@app.route('/players/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    # Get current datetime
    now = datetime.utcnow()
    
    player = Player.query.get_or_404(player_id)
    
    # Verify player belongs to a team managed by current user
    user_teams = Team.query.filter_by(manager_id=current_user.id).all()
    player_team_ids = [team.id for team in player.teams]
    is_manager = any(team.id in player_team_ids for team in user_teams)
    
    if not is_manager and not current_user.is_admin:
        flash('You do not have permission to edit this player.', 'danger')
        return redirect(url_for('player_list'))
    
    form = PlayerRegistrationForm()
    
    # Populate team_id dropdown with teams managed by current user
    form.team_id.choices = [(team.id, team.name) for team in Team.query.filter_by(manager_id=current_user.id).all()]
    
    if request.method == 'GET':
        # Pre-populate form with existing data
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
        form.date_of_birth.data = player.date_of_birth
        form.position.data = player.position
        form.jersey_number.data = player.jersey_number
        form.email.data = player.email
        form.phone.data = player.phone
        # Can't pre-populate file field, just show existing photo
        if player.teams:
            form.team_id.data = player.teams[0].id  # Pre-select the first team
    
    if form.validate_on_submit():
        # Update player details
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.date_of_birth = form.date_of_birth.data
        player.position = form.position.data
        player.jersey_number = form.jersey_number.data
        player.email = form.email.data
        player.phone = form.phone.data
        
        # Update photo if new one is provided
        if form.photo.data:
            # Save and optimize the player photo
            new_photo_url = save_optimized_image(
                form.photo.data, 
                UPLOAD_FOLDERS['players'], 
                image_type='player'
            )
            
            if new_photo_url:
                # Delete old photo file if it exists
                if player.photo_url:
                    delete_image(player.photo_url)
                
                # Update the player's photo URL
                player.photo_url = new_photo_url
        
        # Handle team assignment
        selected_team = Team.query.get(form.team_id.data)
        if selected_team and selected_team.manager_id == current_user.id:
            # Check if player is already on this team
            if selected_team not in player.teams:
                player.teams.append(selected_team)
        
        db.session.commit()
        flash('Player information has been updated successfully!', 'success')
        
        # Redirect to a sensible location - team details if coming from there
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/teams/'):
            return redirect(next_page)
        return redirect(url_for('player_list'))
    
    return render_template('edit_player.html', form=form, player=player, now=now)

@app.route('/events/register', methods=['GET', 'POST'])
@login_required
def register_event():
    # Get current datetime
    now = datetime.utcnow()
    
    # Only admin users can create events
    if not current_user.is_admin:
        flash('You do not have permission to create events.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = EventRegistrationForm()
    
    if form.validate_on_submit():
        event = Event()
        event.name = form.name.data
        event.description = form.description.data
        event.location = form.location.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.registration_deadline = form.registration_deadline.data
        event.created_by = current_user.id
        db.session.add(event)
        db.session.commit()
        flash('Event has been created successfully!', 'success')
        return redirect(url_for('event_list'))
    
    return render_template('event_registration.html', form=form, now=now)

@app.route('/events')
def event_list():
    # Get current datetime
    now = datetime.utcnow()
    
    events = Event.query.order_by(Event.start_date).all()
    return render_template('event_list.html', events=events, now=now)

@app.route('/events/<int:event_id>')
def event_details(event_id):
    # Get current datetime
    now = datetime.utcnow()
    
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event, now=now)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Get current datetime
    now = datetime.utcnow()
    
    form = SearchForm()
    results = {
        'teams': [],
        'players': [],
        'events': []
    }
    
    if form.validate_on_submit() or request.args.get('query'):
        # Get search query from form or URL parameter
        query = form.query.data if form.validate_on_submit() else request.args.get('query')
        category = form.category.data if form.validate_on_submit() else request.args.get('category', 'all')
        
        # Format query for SQL LIKE
        search_query = f"%{query}%"
        
        # Search teams
        if category in ['all', 'teams']:
            teams = Team.query.filter(
                or_(
                    Team.name.ilike(search_query),
                    Team.division.ilike(search_query)
                )
            ).all()
            results['teams'] = teams
        
        # Search players
        if category in ['all', 'players']:
            players = Player.query.filter(
                or_(
                    Player.first_name.ilike(search_query),
                    Player.last_name.ilike(search_query),
                    Player.position.ilike(search_query)
                )
            ).all()
            results['players'] = players
        
        # Search events
        if category in ['all', 'events']:
            events = Event.query.filter(
                or_(
                    Event.name.ilike(search_query),
                    Event.description.ilike(search_query),
                    Event.location.ilike(search_query)
                )
            ).all()
            results['events'] = events
    
    return render_template('search.html', form=form, results=results, now=now)

@app.route('/events/register_team', methods=['GET', 'POST'])
@login_required
def register_team_for_event():
    # Get current datetime
    now = datetime.utcnow()
    
    form = TeamEventRegistrationForm()
    
    # Populate team_id dropdown with teams managed by current user
    form.team_id.choices = [(team.id, team.name) for team in Team.query.filter_by(manager_id=current_user.id).all()]
    
    # Populate event_id dropdown with upcoming events
    form.event_id.choices = [(event.id, event.name) for event in 
                            Event.query.filter(Event.registration_deadline > now).all()]
    
    if form.validate_on_submit():
        team = Team.query.get(form.team_id.data)
        event = Event.query.get(form.event_id.data)
        
        if team and event and team.manager_id == current_user.id:
            if event not in team.events:
                team.events.append(event)
                db.session.commit()
                flash(f'Team {team.name} has been registered for {event.name}!', 'success')
            else:
                flash('Team is already registered for this event.', 'warning')
        else:
            flash('Invalid team or event selected.', 'danger')
        
        return redirect(url_for('event_list'))
    
    return render_template('team_event_registration.html', form=form, now=now)

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    # Get current datetime
    now = datetime.utcnow()
    
    form = NotificationForm()
    
    # Populate target_team_id dropdown for admin users
    if current_user.is_admin:
        # Use type conversion to ensure all ids are same type (integers)
        form.target_team_id.choices = [(int(0), 'All Teams')] + [(int(team.id), team.name) for team in Team.query.all()]
    else:
        form.target_team_id.choices = [(int(team.id), team.name) for team in Team.query.filter_by(manager_id=current_user.id).all()]
    
    if form.validate_on_submit():
        notification = Notification()
        notification.title = form.title.data
        notification.content = form.content.data
        notification.created_by = current_user.id
        notification.is_global = form.is_global.data
        
        if not form.is_global.data and form.target_team_id.data:
            team = Team.query.get(form.target_team_id.data)
            if team and (team.manager_id == current_user.id or current_user.is_admin):
                notification.target_team_id = team.id
            else:
                flash('Invalid team selected.', 'danger')
                return render_template('notifications.html', form=form, now=now)
        
        db.session.add(notification)
        db.session.commit()
        flash('Notification has been sent!', 'success')
        return redirect(url_for('notifications'))
    
    # Get notifications visible to current user
    if current_user.is_admin:
        all_notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    else:
        managed_teams = Team.query.filter_by(manager_id=current_user.id).all()
        team_ids = [team.id for team in managed_teams]
        
        all_notifications = Notification.query.filter(
            (Notification.is_global == True) | 
            (Notification.target_team_id.in_(team_ids)) |
            (Notification.created_by == current_user.id)
        ).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications.html', form=form, notifications=all_notifications, now=now)
    
@app.route('/admin/users')
@login_required
def admin_users():
    # Get current datetime
    now = datetime.utcnow()
    
    # Only admin users can access this page
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all users
    users = User.query.all()
    
    # Calculate admin count
    admin_count = User.query.filter_by(is_admin=True).count()
    
    # Calculate manager count (users who manage at least one team)
    manager_count = db.session.query(db.func.count(db.distinct(Team.manager_id))).scalar()
    
    # Calculate new users this month
    current_month_start = datetime(now.year, now.month, 1)
    new_users_count = User.query.filter(User.created_at >= current_month_start).count()
    
    return render_template(
        'admin/user_management.html', 
        users=users, 
        admin_count=admin_count,
        manager_count=manager_count,
        new_users_count=new_users_count,
        now=now
    )
    
@app.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_user_details(user_id):
    # Get current datetime
    now = datetime.utcnow()
    
    # Only admin users can access this page
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Get user's teams
    teams = Team.query.filter_by(manager_id=user.id).all()
    
    # For simplicity, we're not implementing form editing in this example
    # This would typically include a form to modify user details
    
    return render_template(
        'admin/user_details.html',
        user=user,
        teams=teams,
        now=now
    )
