from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from taxi.models import Manufacturer, Car, Driver


class ManufacturerListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        Manufacturer.objects.create(name="Toyota", country="Japan")
        Manufacturer.objects.create(name="Ford", country="USA")

    def test_manufacturer_list_view_status_code(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_manufacturer_list_view_uses_correct_template(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    def test_manufacturer_list_view_context(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url)
        self.assertIn("manufacturer_list", response.context)
        self.assertIn("search_form_manufacturer", response.context)
        self.assertEqual(len(response.context["manufacturer_list"]), 2)

    def test_manufacturer_list_view_search(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url, {"name": "Toy"})
        self.assertEqual(len(response.context["manufacturer_list"]), 1)
        self.assertEqual(
            response.context["manufacturer_list"][0].name, "Toyota"
        )

    def test_toggle_assign_to_car_view(self):
        driver = get_user_model().objects.create_user(
            username="driver", password="pass123", license_number="ABC12345"
        )
        self.client.login(username="driver", password="pass123")
        manufacturer = Manufacturer.objects.create(
            name="TestManuf", country="Country"
        )
        car = Car.objects.create(model="ModelX", manufacturer=manufacturer)

        url = reverse("taxi:toggle-car-assign", args=[car.pk])
        response = self.client.get(url)

        driver.refresh_from_db()
        self.assertIn(car, driver.cars.all())
        self.assertEqual(response.status_code, 302)  # редірект

        # Другий раз викликаємо, щоб зняти призначення
        response = self.client.get(url)
        driver.refresh_from_db()
        self.assertNotIn(car, driver.cars.all())
