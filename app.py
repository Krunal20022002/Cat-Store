from flask import Flask, render_template, request, flash, redirect, url_for, session
import re
import os
import secrets
from datetime import datetime, timedelta
from database import init_db, add_user, get_user_by_email, verify_password, set_reset_token, verify_reset_token, update_password, get_all_users, add_contact, get_all_contacts

app = Flask(__name__)
app.secret_key = 'cat_store_secret_key'  # Required for flash messages

# Initialize database
init_db()

# Images directory helper
IMAGE_DIR = os.path.join(app.root_path, 'static', 'images')

def list_images():
    """Return a sorted list of image filenames in static/images."""
    allowed = {'.jpg', '.jpeg', '.png', '.svg', '.webp'}
    imgs = []
    try:
        for f in os.listdir(IMAGE_DIR):
            _, ext = os.path.splitext(f.lower())
            if ext in allowed:
                imgs.append(f)
    except Exception:
        return []
    imgs.sort()
    return imgs

def find_hero_image(images):
    """Return filename for hero image if user uploaded one named 'hero' (any extension)."""
    for f in images:
        base = os.path.splitext(f)[0].lower()
        if base == 'hero':
            return f
    return None

def pick_category_images(images):
    """Try to pick representative images for categories: cats, food, toys/accessories.
    Returns dict with keys 'cats','food','toys'. Falls back to any image or SVG placeholders."""
    cats = None
    food = None
    toys = None

    # Prefer exact filenames uploaded by the user (e.g., 'cat.jpg', 'food.jpg', 'toys and accessories.jpg')
    lowered = [f.lower() for f in images]
    for f in images:
        base = os.path.splitext(f)[0].lower()
        if not cats and base == 'cat':
            cats = f
        if not food and base == 'food':
            food = f
        if not toys and base in ('toys and accessories', 'toys and accessory', 'toys', 'accessories', 'toy'):
            toys = f

    # If exact names weren't provided, fall back to keyword matching
    if not (cats and food and toys):
        for f in lowered:
            if not cats and any(k in f for k in ('cat', 'kitten', 'feline')):
                cats = f
            if not food and any(k in f for k in ('food', 'kibble', 'salmon', 'tuna')):
                food = f
            if not toys and any(k in f for k in ('toy', 'ball', 'wand', 'mouse', 'scratch', 'accessor')):
                toys = f

    # fallback picks
    if not cats and images:
        cats = images[0]
    if not food and len(images) > 1:
        food = images[1]
    if not toys and len(images) > 2:
        toys = images[2]

    # final fallback to svg placeholders if still None
    if not cats:
        cats = 'cat1.svg'
    if not food:
        food = 'cat2.svg'
    if not toys:
        toys = 'cat3.svg'

    return {'cats': cats, 'food': food, 'toys': toys}

# Route for home page
@app.route('/')
def home():
    images = list_images()
    categories = pick_category_images(images)
    hero = find_hero_image(images)
    return render_template('home.html', categories=categories, hero_image=hero)

# Route for shop page
@app.route('/shop')
def shop():
    images = list_images()
    # pick first 4 images (or fall back to svg placeholders)
    product_images = images[:4]
    return render_template('shop.html', product_images=product_images)

# Route for gallery page
@app.route('/gallery')
def gallery():
    images = list_images()
    return render_template('gallery.html', gallery_images=images)

# Route for about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # Basic validation
        if not full_name or not email or not message:
            flash('Please fill in name, email and message', 'error')
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email.strip()):
            flash('Please provide a valid email address', 'error')
        else:
            # store in database
            ok = add_contact(full_name.strip(), email.strip(), phone.strip() if phone else '', message.strip())
            if ok:
                flash('Thanks — your message has been received!', 'success')
                return redirect(url_for('contact'))
            else:
                flash('Failed to save your message. Please try again later.', 'error')

    return render_template('contact.html')

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([full_name, email, mobile, password, confirm_password]):
            flash('All fields are required', 'error')
        else:
            # name validation: letters, spaces, hyphen and apostrophe allowed, min 2 chars
            if not re.match(r"^[A-Za-z\s\-']{2,}$", full_name.strip()):
                flash('Please enter a valid name (letters and spaces only, min 2 chars)', 'error')
            # email validation
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email.strip()):
                flash('Invalid email format', 'error')
            else:
                # phone: strip non-digits then check length
                digits = re.sub(r'\D', '', mobile)
                if len(digits) != 10:
                    flash('Mobile number must contain 10 digits', 'error')
                # password checks
                elif password != confirm_password:
                    flash('Passwords do not match', 'error')
                else:
                    pw = password
                    pw_errors = []
                    if len(pw) < 8:
                        pw_errors.append('at least 8 characters')
                    if not re.search(r'[A-Z]', pw):
                        pw_errors.append('an uppercase letter')
                    if not re.search(r'[a-z]', pw):
                        pw_errors.append('a lowercase letter')
                    if not re.search(r'\d', pw):
                        pw_errors.append('a number')
                    if not re.search(r'[^A-Za-z0-9]', pw):
                        pw_errors.append('a special character')

                    if pw_errors:
                        flash('Password must contain ' + ', '.join(pw_errors), 'error')
                    else:
                        if add_user(full_name, email, mobile, password):
                            flash('Registration successful!', 'success')
                            return redirect(url_for('login'))
                        else:
                            flash('Email already registered', 'error')

    return render_template('register.html')


# Route for login page (demo mode — no database)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required', 'error')
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Invalid email format', 'error')
        else:
            user = get_user_by_email(email)
            if user and verify_password(user[4], password):  # index 4 is password_hash
                session['user_id'] = user[0]  # Store user ID in session
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    token = request.args.get('token')
    
    if token:
        # Show reset password form if token is provided
        return render_template('forgot_password.html', token=token)
    
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email', 'error')
        else:
            user = get_user_by_email(email)
            if user:
                # Generate reset token
                token = secrets.token_urlsafe(32)
                expiry = datetime.now() + timedelta(hours=24)
                set_reset_token(email, token, expiry)
                
                # In a real application, you would send this link via email
                reset_link = url_for('forgot_password', token=token, _external=True)
                flash(f'Password reset link (for demo): {reset_link}', 'success')
            else:
                # Don't reveal if email exists or not
                flash('If your email is registered, you will receive a reset link', 'info')
        
    return render_template('forgot_password.html', token=None)

@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    if not token:
        return redirect(url_for('login'))
    
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('forgot_password'))
    
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not password or not confirm_password:
        flash('Please enter both passwords', 'error')
    elif password != confirm_password:
        flash('Passwords do not match', 'error')
    else:
        update_password(email, password)
        flash('Password has been reset successfully', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html', token=token)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/users')
def users():
    """Display all registered users (admin view)."""
    all_users = get_all_users()
    return render_template('users.html', users=all_users)


@app.route('/contacts')
def contacts():
    """Display all contact form submissions."""
    all_contacts = get_all_contacts()
    return render_template('contacts.html', contacts=all_contacts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
