import unittest

from app import app


class RouteIntegrationTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def set_user(self, role, profile_id=1):
        user_id = 1 if role == "restaurant" else 2
        name = "Saffron Table Kitchen" if role == "restaurant" else "Robin Hood Army"
        email = f"{role}@resqthali.demo"
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": user_id, "name": name, "email": email, "role": role,
                "profile_id": profile_id, "email_verified": True,
            }

    def test_all_public_pages_and_parameterized_views_render(self):
        paths = (
            "/", "/about", "/how-help", "/login", "/register",
            "/verify-email/pending/unknown-token", "/notifications", "/donor-dashboard",
            "/volunteer", "/certificates", "/certificates?volunteer_id=1",
            "/ngo-dashboard", "/ngo-dashboard?city=Delhi", "/match", "/match/101",
            "/api/match/101", "/api/check-email?email=broken",
        )
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_guest_is_redirected_from_protected_participant_areas(self):
        for path in ("/restaurant-profile", "/restaurant-dashboard", "/ngo-profile", "/ngo-control-room", "/api/ngo-control-room"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login", response.headers["Location"])
                response.close()

    def test_restaurant_pages_and_donation_form_remain_available(self):
        self.set_user("restaurant")
        for path in ("/profile", "/restaurant-profile", "/restaurant-dashboard", "/donate-to-ngo/1"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertIn(response.status_code, (200, 302))
                response.close()
        response = self.client.post("/donate-to-ngo/1", data={"item": "", "quantity": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please add the food item and quantity", response.data)
        response.close()

    def test_ngo_profile_control_room_and_json_endpoint_remain_available(self):
        self.set_user("ngo")
        response = self.client.get("/profile")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/ngo-profile"))
        response.close()
        for path in ("/ngo-profile", "/ngo-control-room", "/api/ngo-control-room"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_role_mismatch_does_not_expose_the_other_participant_profile(self):
        self.set_user("ngo")
        response = self.client.get("/restaurant-profile")
        self.assertEqual(response.status_code, 302)
        response.close()
        response = self.client.get("/ngo-profile")
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_invalid_login_and_registration_inputs_show_validation(self):
        response = self.client.post("/login", data={"email": "wrong@example.com", "password": "bad"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"could not match", response.data.lower())
        response.close()

        response = self.client.post("/register", data={"name": "Test", "email": "not-a-gmail", "password": "pass", "role": "ngo"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"valid @gmail.com", response.data)
        response.close()

    def test_missing_resources_fail_safely(self):
        for path in ("/api/match/99999", "/api/ngo-control-room"):
            response = self.client.get(path)
            expected = 404 if path.startswith("/api/match") else 302
            self.assertEqual(response.status_code, expected)
            response.close()
        response = self.client.get("/match/99999")
        self.assertEqual(response.status_code, 302)
        response.close()
        response = self.client.get("/a-route-that-does-not-exist")
        self.assertEqual(response.status_code, 404)
        response.close()


if __name__ == "__main__":
    unittest.main()
