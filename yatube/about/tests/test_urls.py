from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_use_correct_templates(self):
        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exist_at_desired_locations(self):
        url_code_status_names = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, code_status in url_code_status_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code_status)
