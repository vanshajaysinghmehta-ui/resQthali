# resQthali 🍛🌱

### Food rescue, responsible compost, stronger communities.

**resQthali** is a food-rescue platform designed to connect restaurants with NGOs and volunteers so that safe surplus food can reach people who need it instead of being wasted.

The platform also promotes responsible handling of food that is no longer suitable for serving by connecting the food-rescue process with a circular composting approach.

---

## 🌍 Problem

Large amounts of edible food can become surplus at restaurants while communities and organizations continue to face food insecurity.

At the same time, food that is no longer safe to serve is often treated simply as waste.

resQthali aims to create a structured system where:

* Safe surplus food can be redirected to communities.
* Restaurants can submit available surplus food.
* NGOs can participate in receiving food.
* Volunteers can support last-mile transportation.
* Food that cannot be served can be handled responsibly through composting.
* Different participants can access features based on their roles.

---

## 💡 Solution

resQthali provides a web-based platform connecting the different participants in the food-rescue cycle.

### Basic flow

```text
Restaurant
    ↓
Surplus food submission
    ↓
Backend processing
    ↓
Available NGOs
    ↓
Distance calculation
    ↓
NGO ranking
    ↓
Suggested pickup route
    ↓
Google Maps directions
```

The platform uses geographical distance between locations to help identify nearby NGOs.

---

## ✨ Key Features

### 🍽️ Restaurant Food Donation

Restaurants can submit information about surplus food through the platform.

The backend processes the donation and identifies available NGO options.

### 🤝 NGO Network

The platform contains NGO information and allows NGO users to interact with the food-rescue workflow.

### 🚲 Volunteer Support

Volunteers can participate in the last-mile transportation of rescued food.

### 📍 Distance-Based NGO Matching

The backend calculates geographical distance between a food donation and available NGOs.

The NGOs are then ranked according to distance.

### 🗺️ Google Maps Directions

After the backend determines suitable NGO destinations, it generates Google Maps driving-direction links.

**Important:** The backend performs the NGO distance ranking. Google Maps is used for navigation/directions rather than deciding which NGO is closest.

### 📧 Email Verification

The application includes email verification using secure verification tokens and SMTP email delivery.

Verification tokens have a limited validity period.

### 🔐 Role-Based Access

Different users can have different roles, including:

* Restaurant
* NGO
* Volunteer
* Donor

Protected routes use authentication and role checks.

### 💬 resQthali Assistant

The website includes a chatbot-style assistant for common questions about:

* Restaurant verification
* NGO requests
* Routes
* Food waste
* Vermicomposting

The current assistant is **rule-based**, using predefined backend logic rather than a large language model.

### 📊 Impact Information

The platform displays impact-oriented information such as:

* Meals saved
* Compost generated
* Partner NGOs

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Jinja templates

## Backend

* Python
* Flask

## Routing & Location

* Google Maps directions
* Haversine distance calculation

## Email

* SMTP
* Secure verification tokens

## Deployment

* GitHub
* Render
* Gunicorn

---

# 📁 Project Structure

```text
resqthali/
│
├── app.py
│   └── Main Flask application
│
├── db.py
│   └── Data layer and application data
│
├── requirements.txt
│   └── Python dependencies
│
├── .env.example
│   └── Example environment configuration
│
├── SMTP_SETUP.md
│   └── Email/SMTP configuration documentation
│
├── README_UPGRADE.md
│   └── Upgrade-related documentation
│
├── templates/
│   ├── base.html
│   ├── about.html
│   ├── how_help.html
│   ├── login.html
│   ├── register.html
│   ├── donor.html
│   ├── restaurant_profile.html
│   ├── ngo_profile.html
│   ├── ngo_control_room.html
│   ├── restaurant dashboards
│   ├── volunteer.html
│   ├── certificates.html
│   └── other application pages
│
├── static/
│   ├── about-hunger.jpeg
│   ├── resqthali-child.jpeg
│   └── uploads/
│
└── tests/
    ├── test_routes.py
    └── test_site.py
```

---

# ⚙️ How the Backend Works

The main backend is contained in `app.py`.

Flask routes connect URLs to Python functions.

For example:

```text
Browser
   ↓
GET /login
   ↓
Flask route
   ↓
login.html
   ↓
Browser
```

For an action such as food submission:

```text
Restaurant
   ↓
POST /submit-food
   ↓
Flask
   ↓
Validate user/session
   ↓
Create donation
   ↓
Find available NGOs
   ↓
Calculate distances
   ↓
Rank NGOs
   ↓
Generate route links
   ↓
Return result
```

---

# 📍 NGO Matching Algorithm

resQthali currently uses geographical distance to rank NGOs.

The backend uses the **Haversine formula** to calculate the approximate great-circle distance between two latitude/longitude coordinates.

Conceptually:

```text
Donation location
       ↓
Get NGO coordinates
       ↓
Calculate distance for each NGO
       ↓
Sort NGOs by distance
       ↓
Display suggested NGOs
```

The application also estimates travel time using an assumed average speed.

The current prototype does **not** use live traffic information for this estimate.

---

# 🗺️ Google Maps Integration

Once suitable NGO destinations are identified, resQthali generates Google Maps directions URLs.

The basic process is:

```text
Backend
   ↓
Origin + NGO destination
   ↓
Google Maps directions URL
   ↓
User opens route
```

Google Maps therefore handles the actual navigation interface while the resQthali backend handles the initial NGO ranking.

---

# 🔐 Authentication & Verification

The application includes:

* User registration
* Login/logout
* Sessions
* Role-based route protection
* Email verification
* Organization verification functionality

Verification tokens are generated using secure random token generation and are given a limited expiry period.

---

# 📤 File Uploads

The application supports selected upload types for documents and images.

Allowed extensions include:

```text
.jpg
.jpeg
.png
.webp
.pdf
```

Uploaded filenames are processed using `secure_filename()`.

The application also has an upload-size limit of approximately **8 MB**.

---

# 💬 Chatbot Architecture

The resQthali assistant communicates with the backend through:

```text
/api/chat
```

The frontend sends a request using JavaScript.

The Flask backend processes the message and returns JSON.

```text
Chat interface
      ↓
JavaScript fetch()
      ↓
/api/chat
      ↓
Flask
      ↓
Rule-based response
      ↓
JSON
      ↓
Chat interface
```

The current implementation is intentionally lightweight and does not require an external AI model.

---

# 🔌 API Endpoints

The application contains API routes for functionality such as:

```text
/api/chat
/api/location
/api/check-email
/api/match/<donation_id>
/api/ngo-control-room
```

These endpoints allow JavaScript components and frontend pages to communicate with the Flask backend.

---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/vanshajaysinghmehta-ui/resQthali.git
cd resQthali
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy the example environment file and configure the required values.

```text
.env.example
```

For email functionality, SMTP configuration may be required.

## 5. Run the application

```bash
python app.py
```

The development server will normally be available at:

```text
http://127.0.0.1:5000
```

---

# ☁️ Deployment

The project can be deployed using Render.

The deployment process is:

```text
GitHub repository
       ↓
Render
       ↓
Install requirements
       ↓
Gunicorn
       ↓
Flask application
```

The production start command is:

```bash
gunicorn app:app
```

Here:

* The first `app` refers to `app.py`.
* The second `app` refers to the Flask application object inside `app.py`.

---

# 🧪 Testing

The project includes automated test files:

```text
tests/test_routes.py
tests/test_site.py
```

These tests can be used to check important routes and website behaviour.

---

# ⚠️ Current Prototype Limitations

resQthali is currently a prototype/demo application.

Some components should be upgraded before production deployment.

### 1. Persistent Database

The current data layer uses in-memory application data.

A production version should use persistent storage such as PostgreSQL.

### 2. Password Security

Production authentication should use secure password hashing and stronger credential management.

### 3. Secret Management

Sensitive configuration such as Flask secret keys and SMTP credentials should be stored securely through environment variables.

### 4. Verification Token Storage

Verification tokens are currently held in memory.

A production system should store them persistently.

### 5. Location Data

The current food-submission flow uses prototype location data rather than fully dynamic restaurant GPS coordinates.

### 6. Travel-Time Estimation

The current system uses an approximate average-speed calculation rather than live traffic data.

### 7. Production File Storage

Uploaded files should eventually be stored using dedicated persistent/object storage rather than relying only on the application filesystem.

---

# 🔮 Future Improvements

Potential future improvements include:

* PostgreSQL or another persistent database
* Secure password hashing
* Persistent verification-token storage
* Dynamic restaurant GPS/location capture
* Live traffic-aware routing
* More advanced NGO matching
* Persistent cloud file storage
* Stronger restaurant/NGO verification
* Expanded analytics and impact dashboards
* Notifications for new food-rescue opportunities
* Improved volunteer coordination
* More advanced AI assistance if required

---

# 🎯 Project Goal

resQthali aims to make food rescue more structured by connecting:

```text
Restaurants
     +
 NGOs
     +
Volunteers
     ↓
Food Rescue
     ↓
Community Impact
     ↓
Responsible Food Waste Management
```

The broader goal is to help turn surplus food into a resource rather than simply treating it as waste.

---

# 👥 Project

**resQthali**

> Every meal matters.

Built as a food-rescue platform prototype focused on connecting surplus food with communities while encouraging responsible food-waste management.
