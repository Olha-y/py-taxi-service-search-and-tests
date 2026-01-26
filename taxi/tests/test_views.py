from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Car, Manufacturer


class PublicAccessTests(TestCase):
    def test_public_access_to_index_page(self):
        url = reverse("taxi:index")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse("login")}?next={url}"
        )

    def test_public_access_to_manufacturer_list_page(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_public_access_to_car_list_page(self):
        url = reverse("taxi:car-list")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_public_access_to_driver_list_page(self):
        url = reverse("taxi:driver-list")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)


class PrivateAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.driver_admin = get_user_model().objects.create_superuser(
            username="superuser",
            password="password",
        )
        cls.driver = get_user_model().objects.create_user(
            username="user",
            password="password1",
            license_number="FTX12345",
        )

    def setUp(self):
        self.client.force_login(self.driver)

    def test_private_access_to_index_page(self):
        url = reverse("taxi:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_access_to_manufacturer_list_page(self):
        url = reverse("taxi:manufacturer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_access_to_car_list_page(self):
        url = reverse("taxi:car-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_access_to_driver_list_page(self):
        url = reverse("taxi:driver-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_create_new_driver(self):
        url = reverse("taxi:driver-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_create_manufacturer(self):
        url = reverse("taxi:manufacturer-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_create_new_car(self):
        url = reverse("taxi:car-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_update_manufacturer(self):
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer",
            country="USA",
        )

        url = reverse(
            "taxi:manufacturer-update",
            kwargs={"pk": manufacturer.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_access_update_car(self):
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer_1",
            country="test_A",
        )
        car = Car.objects.create(
            model="test_model",
            manufacturer=manufacturer,
        )

        car.drivers.add(self.driver)

        url = reverse(
            "taxi:car-update",
            kwargs={"pk": car.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_delete_manufacturer(self):
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer",
            country="USA",
        )

        url = reverse(
            "taxi:manufacturer-delete",
            kwargs={"pk": manufacturer.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_access_delete_driver_page(self):
        """
        Logged-in driver can access
        the Delete page for delete any driver.
        """
        other_driver = get_user_model().objects.create_user(
            username="driver1",
            password="password123",
            license_number="DRT12344",
        )

        url = reverse(
            "taxi:driver-delete",
            kwargs={"pk": other_driver.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_access_delete_own_page(self):
        """
        Logged-in driver can access
        the Delete page for themselves.
        """
        url = reverse(
            "taxi:driver-delete",
            kwargs={"pk": self.driver.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_driver_access_delete_car(self):
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer_1",
            country="test_A",
        )
        car = Car.objects.create(
            model="test_model",
            manufacturer=manufacturer,
        )

        car.drivers.add(self.driver)

        url = reverse(
            "taxi:car-delete",
            kwargs={"pk": car.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_toggle_assign_to_car(self):
        manufacturer = Manufacturer.objects.create(
            name="Manufacturer_1",
            country="test_A",
        )
        car = Car.objects.create(
            model="test_model",
            manufacturer=manufacturer,
        )

        car.drivers.add(self.driver)
        url = reverse(
            "taxi:toggle-car-assign",
            kwargs={"pk": car.pk}
        )
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("taxi:car-detail", args=[car.pk])
        )
