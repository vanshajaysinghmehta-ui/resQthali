import math
import re
import urllib.parse
import urllib.request
import os
import secrets
import smtplib
import ssl
import time
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote_plus
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import db
from db import ngos, restaurants, donations, volunteers, cities, notifications, food_requests, get_dashboard_stats

app = Flask(__name__)
app.secret_key = "resQthali_secret_key"
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
CONTACT_PHONE = os.getenv("RESQTHALI_CONTACT_PHONE", "+91 98765 43210")
CONTACT_EMAIL = os.getenv("RESQTHALI_CONTACT_EMAIL", "contact@resqthali.org")
UPLOAD_DIR = Path(app.root_path) / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_UPLOADS = {"jpg", "jpeg", "png", "webp", "pdf"}
VERIFICATION_TTL_SECONDS = 24 * 60 * 60
verification_tokens = {}


def save_upload(file, prefix):
    """Save a small verification/profile asset and return its public URL."""
    if not file or not file.filename:
        return None
    suffix = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if suffix not in ALLOWED_UPLOADS:
        return None
    safe_name = secure_filename(file.filename)
    destination = UPLOAD_DIR / f"{prefix}_{safe_name}"
    file.save(destination)
    return url_for('static', filename=f"uploads/{destination.name}")


def gmail_check(email):
    """Validate address shape and ask Google's public DNS whether Gmail accepts mail.

    This cannot prove that a private mailbox exists; only a verification email can do that.
    """
    email = (email or '').strip().lower()
    valid_shape = bool(re.fullmatch(r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@gmail\.com", email))
    if not valid_shape:
        return {"valid": False, "message": "Enter a valid @gmail.com address."}
    try:
        query = urllib.parse.urlencode({"name": "gmail.com", "type": "MX"})
        with urllib.request.urlopen(f"https://dns.google/resolve?{query}", timeout=4) as response:
            payload = response.read().decode('utf-8')
        reachable = '"Status": 0' in payload and 'gmail-smtp-in' in payload
    except Exception:
        reachable = False
    if reachable:
        return {"valid": True, "service_reachable": True, "message": "Gmail’s mail service is reachable. We still need to send a verification email to confirm this exact inbox."}
    # A DNS timeout should not block a correctly formed registration. The exact
    # mailbox still requires an email verification step in a production setup.
    return {"valid": True, "service_reachable": False, "message": "This is a valid Gmail address format. Live mailbox verification is still pending."}


def smtp_is_configured():
    return all(os.getenv(key) for key in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM"))


def send_verification_email(user, request_root):
    """Send a signed, expiring verification link using configured SMTP credentials."""
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {"user_id": user["id"], "expires": time.time() + VERIFICATION_TTL_SECONDS}
    base_url = os.getenv('APP_BASE_URL', request_root).rstrip('/')
    verify_url = base_url + url_for('verify_email', token=token)
    if not smtp_is_configured():
        return False, token, "SMTP is not configured. Add SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM to send real email."
    message = EmailMessage()
    message["Subject"] = "Verify your resQthali email"
    message["From"] = os.getenv("SMTP_FROM")
    message["To"] = user["email"]
    message.set_content(f"Hello {user['name']},\n\nVerify your resQthali account by opening this link:\n{verify_url}\n\nThis link expires in 24 hours. If you did not register, ignore this message.")
    try:
        host, port = os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587"))
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls(context=context)
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.send_message(message)
        return True, token, "Verification email sent. Check your inbox and spam folder."
    except (OSError, smtplib.SMTPException, ValueError) as error:
        app.logger.warning("SMTP verification email failed: %s", error)
        return False, token, "We could not send the verification email right now. Check your SMTP settings and try again."


def haversine_distance(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return round(radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def google_maps_directions_url(origin_lat, origin_lng, dest_lat, dest_lng):
    return ("https://www.google.com/maps/dir/?api=1"
            f"&origin={quote_plus(f'{origin_lat},{origin_lng}')}&destination={quote_plus(f'{dest_lat},{dest_lng}')}&travelmode=driving")


def rank_ngos_for_donation(donation):
    ranked = []
    for partner in db.get_active_ngos():
        if None in (donation.get("location_lat"), donation.get("location_lng"), partner.get("lat"), partner.get("lng")):
            continue
        distance = haversine_distance(donation["location_lat"], donation["location_lng"], partner["lat"], partner["lng"])
        entry = dict(partner)
        entry["distance_km"] = distance
        entry["est_time_mins"] = max(round((distance / 30) * 60), 5)
        entry["route_url"] = google_maps_directions_url(donation["location_lat"], donation["location_lng"], partner["lat"], partner["lng"])
        ranked.append(entry)
    return sorted(ranked, key=lambda item: item["distance_km"])


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user"):
                flash("Please log in to access your profile.", "info")
                return redirect(url_for("login", next=request.path))
            if role and session["user"].get("role") != role:
                flash("That profile area is for verified participants of that role.", "danger")
                return redirect(url_for("profile"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.context_processor
def shared_context():
    return {"current_user": session.get("user"), "site_notifications": notifications, "contact_phone": CONTACT_PHONE, "contact_email": CONTACT_EMAIL}


@app.route('/')
def index(): return render_template('base.html', stats=get_dashboard_stats(), cities=cities)

@app.route('/about')
def about(): return render_template('about.html', stats=get_dashboard_stats(), cities=cities)

@app.route('/how-help')
def how_help(): return render_template('how_help.html', stats=get_dashboard_stats())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.get_user(request.form.get('email', ''), request.form.get('password', ''))
        if not user:
            flash("We could not match those details. Try one of the demo accounts below.", "danger")
        else:
            session['user'] = {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"], "profile_id": user["profile_id"], "email_verified": user.get("email_verified", False)}
            flash(f"Welcome back, {user['name']}.", "success")
            return redirect(request.args.get('next') or url_for('profile'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        city = request.form.get('city', '')
        phone = request.form.get('phone', '').strip()
        id_number = request.form.get('id_number', '').strip()
        fssai_license = request.form.get('fssai_license', '').strip()
        email_check = gmail_check(email)
        missing_restaurant_details = role == 'restaurant' and not all((phone, id_number, fssai_license))
        missing_volunteer_details = role == 'volunteer' and not phone
        if not name or not password or not email_check['valid'] or missing_restaurant_details or missing_volunteer_details:
            message = email_check['message'] if not email_check['valid'] else ('Restaurant contact, ID, and FSSAI licence numbers are required.' if missing_restaurant_details else ('A contact number is required for volunteer applications.' if missing_volunteer_details else 'Please complete every required field.'))
            flash(message, 'danger')
        else:
            user, error = db.register_user(name, email, password, role, city, phone, id_number, fssai_license)
            if error:
                flash(error, 'danger')
            else:
                user["email_verified"] = False
                session['user'] = {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"], "profile_id": user["profile_id"]}
                sent, token, message = send_verification_email(user, request.url_root)
                session['user']['email_verified'] = False
                flash('Account created. ' + message, 'success' if sent else 'info')
                return redirect(url_for('verify_email_pending', token=token))
    return render_template('register.html', cities=cities, selected_role=request.args.get('role', 'restaurant'))


@app.route('/verify-email/pending/<token>')
def verify_email_pending(token):
    record = verification_tokens.get(token)
    return render_template('verify_email.html', token=token, sent=smtp_is_configured(), valid=bool(record and record['expires'] > time.time()))


@app.route('/verify-email/<token>')
def verify_email(token):
    record = verification_tokens.get(token)
    if not record or record['expires'] < time.time():
        flash('That verification link is missing or expired. Please register again or request a new link.', 'danger')
        return redirect(url_for('login'))
    user = next((candidate for candidate in db.users if candidate['id'] == record['user_id']), None)
    if not user:
        flash('We could not find that account.', 'danger')
        return redirect(url_for('login'))
    user['email_verified'] = True
    verification_tokens.pop(token, None)
    if session.get('user', {}).get('id') == user['id']:
        session['user']['email_verified'] = True
    flash('Email verified successfully. You can now complete your participant profile.', 'success')
    return redirect(url_for('profile'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    destination = {'restaurant': 'restaurant_profile', 'ngo': 'ngo_profile', 'volunteer': 'volunteer_profile'}.get(user['role'], 'volunteer_profile')
    return redirect(url_for(destination))


@app.route('/restaurant-profile', methods=['GET', 'POST'])
@login_required('restaurant')
def restaurant_profile():
    user = session['user']
    restaurant = db.get_restaurant_by_id(user['profile_id'])
    if request.method == 'POST':
        profile_url = save_upload(request.files.get('profile_photo'), f"restaurant_{restaurant['id']}_profile")
        id_url = save_upload(request.files.get('id_photo'), f"restaurant_{restaurant['id']}_id")
        fssai_url = save_upload(request.files.get('fssai_photo'), f"restaurant_{restaurant['id']}_fssai")
        if profile_url: restaurant['profile_photo'] = profile_url
        if id_url: restaurant['id_photo'] = id_url
        if fssai_url: restaurant['fssai_photo'] = fssai_url
        if id_url and fssai_url:
            restaurant['verified'] = True
            restaurant['id_status'] = 'Verified'
            restaurant['fssai_status'] = 'Verified'
        else:
            restaurant['id_status'] = 'Submitted for review'
            restaurant['fssai_status'] = 'Submitted for review'
        flash("Your profile and verification files were saved for review.", "success")
    return render_template('restaurant_profile.html', restaurant=restaurant)


@app.route('/ngo-profile', methods=['GET', 'POST'])
@login_required('ngo')
def ngo_profile():
    user = session['user']
    partner = db.get_ngo_by_id(user['profile_id'])
    if request.method == 'POST':
        profile_url = save_upload(request.files.get('profile_photo'), f"ngo_{partner['id']}_profile")
        id_url = save_upload(request.files.get('id_photo'), f"ngo_{partner['id']}_id")
        if profile_url: partner['profile_photo'] = profile_url
        if id_url: partner['id_photo'] = id_url
        item = request.form.get('item', '').strip()
        quantity = request.form.get('quantity', '').strip()
        urgency = request.form.get('urgency', 'Medium')
        if item and quantity:
            food_requests.append({"id": len(food_requests) + 1, "ngo_id": partner['id'], "item": item, "quantity": quantity, "urgency": urgency, "status": "Open"})
            flash("Your food request is now visible to verified restaurant partners.", "success")
            return redirect(url_for('ngo_profile'))
        flash("Please add an item and quantity.", "danger")
    requests_for_ngo = [r for r in food_requests if r['ngo_id'] == partner['id']]
    applications = [a for a in db.volunteer_applications if a['status'] == 'Pending' and (a.get('ngo_id') in (None, partner['id']))]
    review_notice = session.pop('ngo_review_notice', None)
    return render_template('ngo_profile.html', partner=partner, food_requests=requests_for_ngo, volunteer_applications=applications, ngo_review_notice=review_notice)


@app.route('/ngo-profile/volunteer/<int:application_id>/<action>', methods=['POST'])
@login_required('ngo')
def review_volunteer(application_id, action):
    if action not in ('accept', 'reject'):
        return jsonify({'error': 'Invalid volunteer action.'}), 400
    application = db.get_volunteer_application(application_id)
    ngo_id = session['user']['profile_id']
    if not application or application['status'] != 'Pending':
        flash('That volunteer application is no longer available.', 'danger')
        return redirect(url_for('ngo_profile'))
    if application.get('ngo_id') not in (None, ngo_id):
        flash('That volunteer application is assigned to another NGO.', 'danger')
        return redirect(url_for('ngo_profile'))
    application['ngo_id'] = ngo_id
    application['status'] = 'Accepted' if action == 'accept' else 'Rejected'
    volunteer = db.get_volunteer_by_id(application['volunteer_id'])
    if volunteer:
        volunteer['status'] = 'Accepted by NGO' if action == 'accept' else 'Application declined'
    message = '✓ Volunteer accepted. They can now coordinate with your NGO.' if action == 'accept' else '✕ Volunteer application rejected.'
    category = 'success' if action == 'accept' else 'danger'
    session['ngo_review_notice'] = {'message': message, 'category': category}
    return redirect(url_for('ngo_profile'))


@app.route('/ngo-control-room')
@login_required('ngo')
def ngo_control_room():
    partner = db.get_ngo_by_id(session['user']['profile_id'])
    return render_template('ngo_control_room.html', partner=partner)


def ngo_dashboard_payload(ngo_id):
    partner = db.get_ngo_by_id(ngo_id)
    incoming = []
    for donation in donations:
        match_status = 'Matched to another NGO'
        if donation.get('matched_ngo_id') == ngo_id:
            match_status = 'Matched to this NGO'
        elif donation.get('matched_ngo_id') is None:
            match_status = 'Awaiting NGO match'
        incoming.append({
            'id': donation['id'], 'item': donation['item'], 'quantity': donation['quantity'],
            'restaurant': donation['donor_name'], 'city': donation.get('location_city', 'India'),
            'status': donation['status'], 'match_status': match_status,
            'updated': 'Live feed'
        })
    requests_for_ngo = [{
        'id': item['id'], 'item': item['item'], 'quantity': item['quantity'],
        'urgency': item['urgency'], 'status': item['status']
    } for item in food_requests if item['ngo_id'] == ngo_id]
    return {'ngo': {'id': partner['id'], 'name': partner['name'], 'city': partner['city']}, 'incoming': incoming, 'requests': requests_for_ngo, 'unread_notifications': sum(1 for n in notifications if n.get('unread'))}


@app.route('/api/ngo-control-room')
@login_required('ngo')
def api_ngo_control_room():
    return jsonify(ngo_dashboard_payload(session['user']['profile_id']))


@app.route('/notifications')
def notification_page(): return render_template('notifications.html', notifications=notifications)


@app.route('/donor-dashboard')
def donor():
    return render_template('donor.html', restaurants=restaurants, donations=donations)


@app.route('/restaurant-dashboard', methods=['GET', 'POST'])
@login_required('restaurant')
def restaurant_dashboard():
    return redirect(url_for('restaurant_profile'))


@app.route('/submit-food', methods=['POST'])
@login_required('restaurant')
def submit_food():
    restaurant = db.get_restaurant_by_id(session['user']['profile_id'])
    if not session['user'].get('email_verified', False):
        flash("Please verify your email before submitting food.", "info")
        return redirect(url_for('verify_email_pending', token=''))
    if not restaurant.get('verified'):
        flash("Only verified restaurants can submit food for pickup.", "danger")
        return redirect(url_for('restaurant_profile'))
    item, quantity = request.form.get('item', '').strip(), request.form.get('quantity', '').strip()
    if item and quantity:
        donation_id = max(d['id'] for d in donations) + 1
        donations.append({"id": donation_id, "donor_name": restaurant['name'], "item": item, "quantity": quantity, "status": "Pending Pickup", "location_city": restaurant['city'], "location_lat": 28.6139, "location_lng": 77.2090, "matched_ngo_id": None, "restaurant_id": restaurant['id']})
        notifications.insert(0, {"id": len(notifications) + 1, "title": "Food submission received", "message": f"{restaurant['name']} submitted {item} for NGO matchmaking.", "time": "Just now", "unread": True})
        flash("Food submitted. We’ll notify you when a partner NGO is matched.", "success")
    else: flash("Please add the food item and quantity.", "danger")
    return redirect(url_for('restaurant_profile'))


@app.route('/volunteer')
def volunteer(): return render_template('volunteer.html', volunteers=volunteers, cities=cities)

@app.route('/volunteer-profile', methods=['GET', 'POST'])
@login_required('volunteer')
def volunteer_profile():
    volunteer = db.get_volunteer_by_id(session['user']['profile_id'])
    if request.method == 'POST':
        volunteer['phone'] = request.form.get('phone', '').strip() or volunteer.get('phone', '')
        volunteer['availability'] = request.form.get('availability', '').strip() or volunteer.get('availability', '')
        volunteer['transport'] = request.form.get('transport', '').strip() or volunteer.get('transport', '')
        volunteer['interests'] = request.form.get('interests', '').strip() or volunteer.get('interests', '')
        flash('Your volunteer details have been saved. We’ll be in touch about nearby opportunities.', 'success')
        return redirect(url_for('volunteer_profile'))
    return render_template('volunteer_profile.html', volunteer=volunteer)


@app.route('/api/volunteer-profile', methods=['POST'])
@login_required('volunteer')
def api_volunteer_profile():
    volunteer = db.get_volunteer_by_id(session['user']['profile_id'])
    data = request.get_json(silent=True) or request.form
    if not volunteer:
        return jsonify({'ok': False, 'message': 'Volunteer profile not found.'}), 404
    phone = (data.get('phone') or '').strip()
    availability = (data.get('availability') or '').strip()
    transport = (data.get('transport') or '').strip()
    interests = (data.get('interests') or '').strip()
    if not phone:
        return jsonify({'ok': False, 'message': 'Contact number is required.'}), 400
    if len(phone) < 7 or len(phone) > 20:
        return jsonify({'ok': False, 'message': 'Enter a valid contact number.'}), 400
    volunteer['phone'] = phone
    volunteer['availability'] = availability or volunteer.get('availability', '')
    volunteer['transport'] = transport or volunteer.get('transport', '')
    volunteer['interests'] = interests or volunteer.get('interests', '')
    return jsonify({'ok': True, 'message': 'Volunteer profile saved.'})

@app.route('/certificates')
def certificates():
    volunteer_id = request.args.get('volunteer_id', type=int)
    certificate = db.get_volunteer_by_id(volunteer_id) if volunteer_id else None
    name = request.args.get('name', '').strip()
    role = request.args.get('role', 'Food Rescue Contributor')
    contribution = request.args.get('contribution', 'for helping rescue surplus food and strengthen local communities')
    return render_template('certificates.html', certificate=certificate, name=name, role=role, contribution=contribution)

@app.route('/ngo-dashboard')
def ngo():
    selected_city = request.args.get('city', '').strip()
    visible_ngos = [n for n in ngos if not selected_city or n['city'] == selected_city]
    return render_template('ngo.html', ngos=visible_ngos, cities=cities, selected_city=selected_city)

@app.route('/donate-to-ngo/<int:ngo_id>', methods=['GET', 'POST'])
def donate_to_ngo(ngo_id):
    partner = db.get_ngo_by_id(ngo_id)
    if not partner:
        flash('That NGO partner could not be found.', 'danger')
        return redirect(url_for('ngo'))
    if not session.get('user'):
        return redirect(url_for('login', next=url_for('donate_to_ngo', ngo_id=ngo_id)))
    if session['user'].get('role') != 'restaurant':
        flash('Only restaurant partners can donate food.', 'info')
        return redirect(url_for('profile'))
    restaurant = db.get_restaurant_by_id(session['user']['profile_id'])
    if request.method == 'POST':
        if not session['user'].get('email_verified', False):
            flash('Please verify your email before donating food.', 'info')
            return redirect(url_for('verify_email_pending', token=''))
        if not restaurant.get('verified'):
            flash('Complete your ID and FSSAI verification before donating food.', 'danger')
            return redirect(url_for('restaurant_profile'))
        item = request.form.get('item', '').strip()
        quantity = request.form.get('quantity', '').strip()
        if not item or not quantity:
            flash('Please add the food item and quantity.', 'danger')
        else:
            donation_id = max(d['id'] for d in donations) + 1
            donations.append({'id': donation_id, 'donor_name': restaurant['name'], 'item': item, 'quantity': quantity,
                              'status': 'Matched', 'location_city': restaurant['city'], 'location_lat': 28.6139,
                              'location_lng': 77.2090, 'matched_ngo_id': partner['id'], 'restaurant_id': restaurant['id']})
            notifications.insert(0, {'id': len(notifications) + 1, 'title': 'Donation sent to NGO',
                                     'message': f"{restaurant['name']} offered {item} to {partner['name']}.",
                                     'time': 'Just now', 'unread': True})
            flash(f'Donation sent to {partner["name"]}. We’ll coordinate the pickup with you.', 'success')
            return redirect(url_for('ngo'))
    return render_template('donate_to_ngo.html', partner=partner, restaurant=restaurant)

@app.route('/match')
def match():
    pending = [dict(d) for d in donations if d['status'] != 'Completed']
    for donation in pending: donation['top_matches'] = rank_ngos_for_donation(donation)[:2]
    return render_template('match.html', matches=pending, volunteers=volunteers)

@app.route('/match/<int:donation_id>')
def match_donation(donation_id):
    donation = db.get_donation_by_id(donation_id)
    if not donation:
        flash("Donation request not found.", "danger")
        return redirect(url_for('match'))
    return render_template('match_detail.html', donation=donation, ngos=rank_ngos_for_donation(donation))

@app.route('/api/match/<int:donation_id>')
def api_match_donation(donation_id):
    donation = db.get_donation_by_id(donation_id)
    if not donation: return jsonify({"error": "Donation not found"}), 404
    return jsonify({"donation": donation, "matched_ngos": rank_ngos_for_donation(donation)})

@app.route('/confirm_match')
def confirm_match():
    donation_id, ngo_id = request.args.get('donation_id', type=int), request.args.get('ngo_id', type=int)
    donation = db.set_donation_match(donation_id, ngo_id) if donation_id and ngo_id else None
    if not donation:
        flash("Could not assign that pickup. Please try again.", "danger")
        return redirect(url_for('match'))
    ngo_obj = db.get_ngo_by_id(ngo_id)
    notifications.insert(0, {"id": len(notifications) + 1, "title": "Pickup matched", "message": f"{donation['item']} is matched with {ngo_obj['name']}.", "time": "Just now", "unread": True})
    flash(f"Pickup assigned to {ngo_obj['name']} for {donation['item']}.", "success")
    return redirect(url_for('match'))

@app.route('/api/location', methods=['POST'])
def update_location():
    data = request.get_json(silent=True) or {}
    return jsonify({"status": "success", "message": "Location received. Choose a city or create a pickup request.", "lat": data.get("lat"), "lng": data.get("lng")})


@app.route('/api/check-email')
def check_email():
    return jsonify(gmail_check(request.args.get('email', '')))

@app.route('/api/chat', methods=['POST'])
def chat():
    data, msg = request.get_json(silent=True) or {}, ''
    msg = data.get('message', '').lower()
    reply = "I’m the resQthali assistant. Ask me about restaurant verification, NGO requests, login, or pickup routes."
    if 'individual' in msg: reply = "To keep food safety clear, resQthali accepts food submissions only from verified restaurants with identity and FSSAI details."
    elif 'fssai' in msg or 'verify' in msg: reply = "Restaurants must submit identity details and an FSSAI licence for review before food can be listed."
    elif 'request' in msg or 'ngo' in msg: reply = "Verified NGOs can log in to their profile and publish an item, quantity, and urgency for restaurant partners."
    elif 'notification' in msg or 'match' in msg: reply = "Notifications appear in the bell panel when food is submitted or matched with an NGO."
    return jsonify({"reply": reply})

if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)
