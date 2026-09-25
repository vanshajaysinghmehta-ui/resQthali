import unittest

import db
from app import app


class VolunteerFeatureTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def login_as(self, role, profile_id=1):
        user = {"id": 2, "name": "Robin Hood Army", "email": "ngo@resqthali.demo", "role": role, "profile_id": profile_id, "email_verified": True}
        with self.client.session_transaction() as session:
            session["user"] = user

    def test_volunteer_application_is_created_and_ngo_can_review_it(self):
        email = "volunteer-feature-test@gmail.com"
        response = self.client.post("/register", data={"name": "Feature Volunteer", "email": email, "password": "demo123", "role": "volunteer", "city": "Jaipur", "phone": "+919999999999"})
        self.assertEqual(response.status_code, 302)
        application = next(item for item in db.volunteer_applications if item["volunteer_name"] == "Feature Volunteer")
        self.login_as("ngo", 1)
        response = self.client.get("/ngo-profile")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Feature Volunteer", response.data)
        response = self.client.post(f"/ngo-profile/volunteer/{application['id']}/accept")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(application["status"], "Accepted")

    def test_only_volunteer_can_use_fast_profile_save_api(self):
        with self.client.session_transaction() as session:
            session["user"] = {"id": 3, "name": "Vikram Singh", "email": "volunteer@test", "role": "volunteer", "profile_id": 1, "email_verified": True}
        response = self.client.post("/api/volunteer-profile", json={"phone": "+911234567890", "availability": "Weekends", "transport": "Bike", "interests": "Pickup"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["ok"])
        self.login_as("ngo", 1)
        response = self.client.post("/api/volunteer-profile", json={"phone": "+911234567890"})
        self.assertEqual(response.status_code, 302)

    def test_invalid_fast_save_does_not_partially_mutate_profile(self):
        self.login_as("volunteer", 1)
        volunteer = db.get_volunteer_by_id(1)
        original = dict(volunteer)
        response = self.client.post("/api/volunteer-profile", json={"phone": "12", "availability": "Changed"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(volunteer, original)

    def test_review_notice_is_scoped_to_ngo_profile_and_ownership_is_enforced(self):
        db.volunteer_applications.append({"id": 9001, "volunteer_id": 1, "volunteer_name": "Ownership Test", "city": "Delhi", "status": "Pending", "ngo_id": 2})
        self.login_as("ngo", 1)
        response = self.client.post("/ngo-profile/volunteer/9001/accept")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.get_volunteer_application(9001)["status"], "Pending")
        response = self.client.get("/ngo-profile")
        self.assertNotIn(b"Volunteer accepted", response.data)

    def test_city_list_and_contact_details_are_visible(self):
        response = self.client.get("/volunteer")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Visakhapatnam", response.data)
        self.assertIn(b"+91 98765 43210", response.data)
        self.assertIn(b"contact@resqthali.org", response.data)


if __name__ == "__main__":
    unittest.main()
