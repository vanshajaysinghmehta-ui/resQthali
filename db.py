ngos = [
    {"id": 1, "name": "Robin Hood Army", "city": "Delhi", "state": "Delhi", "service": "Surplus food recovery & redistribution", "phone": "9984444471", "email": "robinhoodarmydelhi@gmail.com", "verified": True, "lat": 28.7041, "lng": 77.1025, "needs": [{"item": "Rice & Dal", "quantity": "50 kg", "urgency": "High"}]},
    {"id": 2, "name": "Feeding India", "city": "Mumbai", "state": "Maharashtra", "service": "Food recovery, meals & malnutrition programs", "phone": "9871178810", "email": "contact@feedingindia.org", "verified": True, "lat": 19.0760, "lng": 72.8777, "needs": [{"item": "Cooked Meals", "quantity": "200 plates", "urgency": "Critical"}]},
    {"id": 3, "name": "India FoodBanking Network", "city": "Bengaluru", "state": "Karnataka", "service": "Food banks, ration kits & packaged food", "phone": "9810845674", "email": "communications@indiafoodbanking.org", "verified": True, "lat": 12.9716, "lng": 77.5946, "needs": [{"item": "Ration Kits", "quantity": "100 kits", "urgency": "Medium"}]},
    {"id": 4, "name": "Roti Bank (AIBRT)", "city": "Lucknow", "state": "Uttar Pradesh", "service": "Food recovery & redistribution", "phone": "9455209530", "email": "allindiarotibanktrust@gmail.com", "verified": True, "lat": 26.8467, "lng": 80.9462, "needs": [{"item": "Roti & Sabzi", "quantity": "500 servings", "urgency": "High"}]},
    {"id": 5, "name": "Annamrita Foundation", "city": "Pune", "state": "Maharashtra", "service": "School meals & community nutrition", "phone": "9822001100", "email": "hello@annamrita.org", "verified": True, "lat": 18.5204, "lng": 73.8567, "needs": [{"item": "Fresh Produce", "quantity": "75 kg", "urgency": "High"}]},
    {"id": 6, "name": "Akshaya Patra Network", "city": "Hyderabad", "state": "Telangana", "service": "School meals & food distribution", "phone": "9000002200", "email": "connect@akshayapatra.org", "verified": True, "lat": 17.3850, "lng": 78.4867, "needs": [{"item": "Staple Grains", "quantity": "150 kg", "urgency": "Medium"}]},
    {"id": 7, "name": "Kolkata Food Rescue", "city": "Kolkata", "state": "West Bengal", "service": "Rescued meals & community kitchens", "phone": "9000003300", "email": "care@kolkatafoodrescue.org", "verified": True, "lat": 22.5726, "lng": 88.3639, "needs": [{"item": "Cooked Meals", "quantity": "300 plates", "urgency": "Critical"}]},
    {"id": 8, "name": "Chennai Food Bank", "city": "Chennai", "state": "Tamil Nadu", "service": "Food bank & emergency ration support", "phone": "9000004400", "email": "help@chennaifoodbank.org", "verified": True, "lat": 13.0827, "lng": 80.2707, "needs": [{"item": "Ration Kits", "quantity": "120 kits", "urgency": "High"}]},
]

restaurants = [
    {"id": 1, "name": "Saffron Table Kitchen", "city": "Delhi", "state": "Delhi", "service": "Event catering & North Indian meals", "fssai_license": "FSSAI 13326012004567", "fssai_status": "Verified", "id_status": "Verified", "contact": "operations@saffrontable.example", "verified": True, "donations": [{"item": "Vegetable Biryani", "quantity": "50 plates", "status": "Matched"}]},
    {"id": 2, "name": "Mango Leaf Restaurant", "city": "Mumbai", "state": "Maharashtra", "service": "Regional meals & corporate catering", "fssai_license": "FSSAI 11524017003218", "fssai_status": "Verified", "id_status": "Verified", "contact": "hello@mangoleaf.example", "verified": True, "donations": [{"item": "Rice & Dal", "quantity": "80 portions", "status": "Pending Pickup"}]},
    {"id": 3, "name": "Green Bowl Café", "city": "Bengaluru", "state": "Karnataka", "service": "Café meals & bakery surplus", "fssai_license": "FSSAI 11225056007891", "fssai_status": "Verified", "id_status": "Verified", "contact": "team@greenbowl.example", "verified": True, "donations": [{"item": "Fresh Idli & Sambar", "quantity": "100 plates", "status": "Pending Pickup"}]},
]

donations = [
    {"id": 101, "donor_name": "Saffron Table Kitchen", "item": "Vegetable Biryani", "quantity": "50 plates", "status": "Matched", "location_city": "Delhi", "location_lat": 28.6139, "location_lng": 77.2090, "matched_ngo_id": 1, "restaurant_id": 1},
    {"id": 102, "donor_name": "Mango Leaf Restaurant", "item": "Rice & Dal", "quantity": "80 portions", "status": "Pending Pickup", "location_city": "Mumbai", "location_lat": 19.0800, "location_lng": 72.8800, "matched_ngo_id": None, "restaurant_id": 2},
    {"id": 103, "donor_name": "Green Bowl Café", "item": "Fresh Idli & Sambar", "quantity": "100 plates", "status": "Pending Pickup", "location_city": "Bengaluru", "location_lat": 13.0600, "location_lng": 77.5900, "matched_ngo_id": None, "restaurant_id": 3},
]

volunteers = [
    {"id": 1, "name": "Vikram Singh", "city": "Delhi", "status": "Active", "deliveries_completed": 42, "hours": 68, "certificate_id": "RQ-VS-0042", "phone": "", "availability": "Weekends", "transport": "Two-wheeler", "interests": "Pickup and delivery"},
    {"id": 2, "name": "Anita Desai", "city": "Mumbai", "status": "On Route", "deliveries_completed": 18, "hours": 31, "certificate_id": "RQ-AD-0018", "phone": "", "availability": "Evenings", "transport": "Public transport", "interests": "Community outreach"},
    {"id": 3, "name": "Rohan Nair", "city": "Bengaluru", "status": "Active", "deliveries_completed": 27, "hours": 44, "certificate_id": "RQ-RN-0027", "phone": "", "availability": "Flexible", "transport": "Two-wheeler", "interests": "Pickup and delivery"},
]

volunteer_applications = []

users = [
    {"id": 1, "email": "restaurant@resqthali.demo", "password": "demo123", "name": "Saffron Table Kitchen", "role": "restaurant", "profile_id": 1, "email_verified": True},
    {"id": 2, "email": "ngo@resqthali.demo", "password": "demo123", "name": "Robin Hood Army", "role": "ngo", "profile_id": 1, "email_verified": True},
]

food_requests = [
    {"id": 1, "ngo_id": 1, "item": "Cooked vegetarian meals", "quantity": "100 portions", "urgency": "High", "status": "Open"},
    {"id": 2, "ngo_id": 2, "item": "Dry ration kits", "quantity": "50 kits", "urgency": "Medium", "status": "Open"},
]
notifications = [
    {"id": 1, "title": "New match found", "message": "Saffron Table Kitchen’s biryani has been matched with Robin Hood Army in Delhi.", "time": "Just now", "unread": True},
    {"id": 2, "title": "Verification reminder", "message": "Keep your restaurant ID and FSSAI licence details updated to receive pickups.", "time": "Today", "unread": True},
]

cities = ["Delhi", "Mumbai", "Bengaluru", "Lucknow", "Pune", "Hyderabad", "Kolkata", "Chennai", "Ahmedabad", "Jaipur", "Surat", "Nagpur", "Indore", "Bhopal", "Kochi", "Chandigarh", "Patna", "Bhubaneswar", "Guwahati", "Coimbatore", "Agra", "Amritsar", "Aurangabad", "Dehradun", "Dhanbad", "Faridabad", "Ghaziabad", "Goa", "Jabalpur", "Jamshedpur", "Kanpur", "Kota", "Ludhiana", "Madurai", "Mangaluru", "Meerut", "Mysuru", "Nashik", "Noida", "Rajkot", "Ranchi", "Srinagar", "Thiruvananthapuram", "Vadodara", "Varanasi", "Vijayawada", "Visakhapatnam"]


def get_dashboard_stats():
    return {"total_meals_saved": 15420, "active_ngos": len(ngos), "lives_impacted": 8900, "states_reached": 8, "compost_kg": 2180}

def get_active_ngos(): return ngos
def get_donation_by_id(donation_id): return next((d for d in donations if d["id"] == donation_id), None)
def get_ngo_by_id(ngo_id): return next((n for n in ngos if n["id"] == ngo_id), None)
def get_restaurant_by_id(restaurant_id): return next((r for r in restaurants if r["id"] == restaurant_id), None)
def get_volunteer_by_id(volunteer_id): return next((v for v in volunteers if v["id"] == volunteer_id), None)
def get_volunteer_application(application_id): return next((a for a in volunteer_applications if a["id"] == application_id), None)
def get_user(email, password):
    return next((u for u in users if u["email"].lower() == email.lower() and u["password"] == password), None)


def register_user(name, email, password, role, city, phone='', id_number='', fssai_license=''):
    """Create a demo participant account and its role-specific profile."""
    if any(u["email"].lower() == email.lower() for u in users):
        return None, "An account with that email already exists."
    city = city if city in cities else cities[0]
    if role == "restaurant":
        profile_id = max((r["id"] for r in restaurants), default=0) + 1
        profile = {"id": profile_id, "name": name, "city": city, "state": "India", "service": "Restaurant food rescue partner", "fssai_license": fssai_license or "Pending submission", "fssai_status": "Pending verification", "id_number": id_number or "Pending submission", "id_status": "Pending verification", "contact": phone or email, "verified": False, "donations": []}
        restaurants.append(profile)
    elif role == "ngo":
        profile_id = max((n["id"] for n in ngos), default=0) + 1
        profile = {"id": profile_id, "name": name, "city": city, "state": "India", "service": "Community food support", "phone": "Pending verification", "email": email, "verified": False, "lat": 28.6139, "lng": 77.2090, "needs": []}
        ngos.append(profile)
    elif role == "volunteer":
        profile_id = max((v["id"] for v in volunteers), default=0) + 1
        profile = {"id": profile_id, "name": name, "city": city, "status": "Application received", "deliveries_completed": 0, "hours": 0, "certificate_id": f"RQ-V-{profile_id:04d}", "phone": phone, "availability": "To be confirmed", "transport": "To be confirmed", "interests": "To be confirmed"}
        volunteers.append(profile)
        volunteer_applications.append({"id": profile_id, "volunteer_id": profile_id, "volunteer_name": name, "city": city, "status": "Pending", "ngo_id": None})
    else:
        return None, "Choose Restaurant, NGO, or Volunteer."
    user = {"id": max((u["id"] for u in users), default=0) + 1, "email": email.lower(), "password": password, "name": name, "role": role, "profile_id": profile_id}
    users.append(user)
    return user, None

def set_donation_match(donation_id, ngo_id):
    donation = get_donation_by_id(donation_id)
    if donation is None or get_ngo_by_id(ngo_id) is None: return None
    donation["matched_ngo_id"], donation["status"] = ngo_id, "Matched"
    return donation
