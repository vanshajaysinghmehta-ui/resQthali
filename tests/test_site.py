import unittest
from pathlib import Path

import db
from app import app


ROOT = Path(__file__).resolve().parents[1]


class SiteRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True)

    def setUp(self):
        self.client = app.test_client()

    def test_existing_public_pages_render(self):
        paths = (
            "/", "/about", "/how-help", "/donor-dashboard", "/notifications",
            "/volunteer", "/certificates", "/ngo-dashboard", "/match", "/match/101",
        )
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_homepage_keeps_primary_features_and_background_image(self):
        response = self.client.get("/")
        body = response.get_data(as_text=True)
        for expected in (
            "Make every extra meal", "Donate food", "Volunteer for pickup",
            "Support an NGO", "Our circular impact", "id=\"particle-layer\"",
            "toggleChat()", "/static/resqthali-child.jpeg",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, body)
        response.close()

    def test_about_page_uses_its_own_background_without_changing_homepage(self):
        about = self.client.get("/about")
        self.assertIn(b"url('/static/about-hunger.jpeg')", about.data)
        about.close()

        home = self.client.get("/")
        self.assertIn(b"url('/static/resqthali-child.jpeg')", home.data)
        self.assertNotIn(b"url('/static/about-hunger.jpeg')", home.data)
        home.close()

    def test_existing_image_assets_are_served(self):
        for asset in ("resqthali-child.jpeg", "about-hunger.jpeg"):
            with self.subTest(asset=asset):
                response = self.client.get(f"/static/{asset}")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data)
                response.close()

    def test_login_and_role_specific_profile_still_work(self):
        response = self.client.post(
            "/login",
            data={"email": "restaurant@resqthali.demo", "password": "demo123"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"restaurant", response.data.lower())
        response.close()
        response = self.client.get("/restaurant-profile")
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_ngo_api_requires_login_and_returns_dashboard_data_when_logged_in(self):
        response = self.client.get("/api/ngo-control-room")
        self.assertEqual(response.status_code, 302)
        response.close()
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": 2, "name": "Robin Hood Army", "email": "ngo@resqthali.demo",
                "role": "ngo", "profile_id": 1, "email_verified": True,
            }
        response = self.client.get("/api/ngo-control-room")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["ngo"]["name"], db.ngos[0]["name"])
        response.close()

    def test_chat_location_and_match_apis(self):
        chat = self.client.post("/api/chat", json={"message": "How can an NGO request food?"})
        self.assertEqual(chat.status_code, 200)
        self.assertIn("NGOs", chat.get_json()["reply"])
        chat.close()

        location = self.client.post("/api/location", json={"lat": 28.6, "lng": 77.2})
        self.assertEqual(location.status_code, 200)
        self.assertEqual(location.get_json()["status"], "success")
        location.close()

        match = self.client.get("/api/match/101")
        self.assertEqual(match.status_code, 200)
        self.assertTrue(match.get_json()["matched_ngos"])
        match.close()
        missing_match = self.client.get("/api/match/99999")
        self.assertEqual(missing_match.status_code, 404)
        missing_match.close()

    def test_invalid_email_check_is_a_json_error_not_a_server_error(self):
        response = self.client.get("/api/check-email?email=not-an-email")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["valid"])
        response.close()

    def test_global_styles_keep_content_within_viewport_and_fix_card_rule(self):
        css_html = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn("body{overflow-x:hidden}", css_html)
        self.assertIn("rgba(255,250,246,.56)", css_html)
        self.assertIn("url('/static/resqthali-child.jpeg')", css_html)
        self.assertIn("img,video,iframe{max-width:100%}", css_html)
        self.assertIn(".feature-card,.panel,.card{border:1px solid var(--line)", css_html)
        self.assertIn("@keyframes halo-drift", css_html)
        self.assertIn("@media(max-width:360px)", css_html)
        self.assertIn(".chat-toggle{right:12px;left:auto;max-width:calc(100vw - 24px)}", css_html)
        self.assertIn(".chatbot{right:12px;left:auto;width:min(320px,calc(100vw - 24px))", css_html)


if __name__ == "__main__":
    unittest.main()
