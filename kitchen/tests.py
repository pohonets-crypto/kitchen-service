from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from kitchen.forms import DishForm, CookCreationForm, CookUpdateForm, CookSearchForm, DishSearchForm, DishTypeSearchForm
from kitchen.models import DishType, Cook, Dish


# Create your tests here.
class ModelTests(TestCase):
    def test_dish_type_str(self):
        dish_type = DishType.objects.create(
            name="test",
        )
        self.assertEqual(str(dish_type),
                         dish_type.name
                         )

    def test_cook_str(self):
        cook = Cook.objects.create(
            username="test",
            first_name="test",
            last_name="test",
            years_of_experience=5,
        )
        self.assertEqual(str(cook),
                         f"{cook.username} ({cook.first_name} {cook.last_name}), "
                f"years of experience: {cook.years_of_experience}")

    def test_dish_str(self):
        dish_type = DishType.objects.create()
        dish = Dish.objects.create(
            name="test",
            price=10,
            dish_type=dish_type,
        )
        self.assertEqual(str(dish), dish.name)


class PublicDishTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_login_required(self):
        dish_url = reverse("kitchen:dish-list")
        res = self.client.get(dish_url)
        self.assertNotEqual(res.status_code, 200)


class PrivateDishTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test123",
        )
        self.client.force_login(self.user)

    def test_retrieve_dishes(self):
        dish_url = reverse("kitchen:dish-list")
        dish_type = DishType.objects.create()
        Dish.objects.create(name="test",
                            price=7.50,
                           dish_type=dish_type)
        Dish.objects.create(name="test1",
                            price=2.75,
                           dish_type=dish_type)
        response = self.client.get(dish_url)
        self.assertEqual(response.status_code, 200)
        dishes = Dish.objects.all()
        self.assertEqual(list(response.context["dish_list"]), list(dishes))
        self.assertTemplateUsed(response, "kitchen/dish_list.html")


class PublicDishListTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_login_required(self):
        dish_type_url = reverse("kitchen:dish-type-list")
        res = self.client.get(dish_type_url)
        self.assertNotEqual(res.status_code, 200)


class PrivateDishTypeTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_retrieve_dish_types(self):
        dish_type_url = reverse("kitchen:dish-type-list")
        DishType.objects.create(name="test")
        DishType.objects.create(name="test1")
        response = self.client.get(dish_type_url)
        self.assertEqual(response.status_code, 200)
        dish_types = DishType.objects.all()
        self.assertEqual(list(response.context["dish_types"]),
                         list(dish_types))
        self.assertTemplateUsed(response,
                                "kitchen/dishtype_list.html")


class PublicCookTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_login_required(self):
        cook_url = reverse("kitchen:cook-list")
        res = self.client.get(cook_url)
        self.assertNotEqual(res.status_code, 200)


class PrivateCookTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_superuser(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_retrieve_cooks(self):
        cook_url = reverse("kitchen:cook-list")
        Cook.objects.create(username="test",
                            years_of_experience=5)
        Cook.objects.create(username="test1",
                            years_of_experience=10)
        response = self.client.get(cook_url)
        self.assertEqual(response.status_code, 200)
        cooks = Cook.objects.all()
        self.assertEqual(list(response.context["cook_list"]), list(cooks))
        self.assertTemplateUsed(response, "kitchen/cook_list.html")


class CookSearchViewTest(TestCase):
    def setUp(self):

        Cook.objects.create(username="alice",
                            years_of_experience=4)
        Cook.objects.create(username="bob",
                              years_of_experience=3)
        Cook.objects.create(username="ALIce2",
                              years_of_experience=2)
        Cook.objects.create(username="charlie",
                              years_of_experience=0)
        self.user = get_user_model().objects.create_superuser(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_search_with_empty_query_returns_all_cooks(self):
        cook_url = reverse("kitchen:cook-list")

        response = self.client.get(cook_url)
        self.assertEqual(response.status_code, 200)

        queryset = response.context["cook_list"]
        self.assertEqual(queryset.count(), 5)
        self.assertEqual(response.status_code, 200)

    def test_cook_search_by_username(self):
        cook_url = reverse("kitchen:cook-list")
        response = self.client.get(
            cook_url,
            data={"username": "alice"},
        )
        queryset = response.context["cook_list"]
        returned_usernames = {cook.username for cook in queryset}
        self.assertEqual(returned_usernames, {"alice", "ALIce2"})
        self.assertEqual(response.status_code, 200)

    def test_cook_search_without_username(self):
        cook_url = reverse("kitchen:cook-list")
        response = self.client.get(
            cook_url,
            data={"username": ""},
        )
        queryset = response.context["cook_list"]
        returned_usernames = {cook.username for cook in queryset}
        self.assertEqual(returned_usernames, {"alice",
                                              "ALIce2",
                                              "bob",
                                              "charlie",
                                              "user"})
        self.assertEqual(response.status_code, 200)


class DishSearchViewTest(TestCase):
    def setUp(self):
        dish_type = DishType.objects.create(name="test")
        Dish.objects.create(name="Varenyky",
                            price=11,
                           dish_type=dish_type)
        Dish.objects.create(name="borsch",
                            price=5,
                           dish_type=dish_type)
        Dish.objects.create(name="Tomato soup",
                            price=8.50,
                           dish_type=dish_type)
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_search_with_empty_query_returns_all_dishes(self):
        dish_url = reverse("kitchen:dish-list")
        response = self.client.get(dish_url)
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_list"]
        self.assertEqual(queryset.count(), 3)
        self.assertEqual(response.status_code, 200)

    def test_dish_search_by_name(self):
        dish_url = reverse("kitchen:dish-list")
        response = self.client.get(
            dish_url,
            data={"name": "Varenyky"},
        )
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_list"]
        returned_names = {dish.name for dish in queryset}
        self.assertEqual(returned_names, {"Varenyky"})
        self.assertEqual(response.status_code, 200)

    def test_dish_search_without_name(self):
        dish_url = reverse("kitchen:dish-list")
        response = self.client.get(
            dish_url,
            data={"name": ""},
        )
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_list"]
        returned_names = {dish.name for dish in queryset}
        self.assertEqual(returned_names, {"Varenyky",
                                           "borsch",
                                           "Tomato soup"})
        self.assertEqual(response.status_code, 200)


class DishTypeSearchTest(TestCase):
    def setUp(self):
        DishType.objects.create(name="Pasta")
        DishType.objects.create(name="soup")
        DishType.objects.create(name="sAlad")
        DishType.objects.create(name="Bread")
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_search_with_empty_query_returns_all_dish_types(self):
        dish_type_url = reverse("kitchen:dish-type-list")
        response = self.client.get(dish_type_url)
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_types"]
        self.assertEqual(queryset.count(), 4)
        self.assertEqual(response.status_code, 200)

    def test_dish_type_search_by_name(self):
        dish_type_url = reverse("kitchen:dish-type-list")
        response = self.client.get(
            dish_type_url,
            data={"name": "soup"},
        )
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_types"]
        returned_dish_types = {
            dish_type.name for dish_type in queryset
        }
        self.assertEqual(returned_dish_types, {"soup"})
        self.assertEqual(response.status_code, 200)

    def test_dish_type_search_without_name(self):
        dish_type_url = reverse("kitchen:dish-type-list")
        response = self.client.get(dish_type_url,
                                   data={"name": ""})
        self.assertEqual(response.status_code, 200)
        queryset = response.context["dish_types"]
        returned_dish_types = {
            dish_type.name for dish_type in queryset
        }
        self.assertEqual(returned_dish_types, {"Pasta",
                                               "soup",
                                               "sAlad",
                                               "Bread"})
        self.assertEqual(response.status_code, 200)


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
        )
        self.client.force_login(self.user)

    def test_index_counts(self):
        dish_type = DishType.objects.create(name="test")
        Dish.objects.create(name="Dish",
                            price=10,
                            dish_type=dish_type)
        Cook.objects.create(username="cook", years_of_experience=1)

        response = self.client.get(reverse("kitchen:index"))
        self.assertContains(response, "1")


class DishCreateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")

    def test_create_dish(self):
        url = reverse("kitchen:dish-create")
        data = {
            "name": "New Dish",
            "description": "Test description",
            "price": 10,
            "dish_type": self.dish_type.id,
            "cooks": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(Dish.objects.count(), 1)
        self.assertRedirects(response, reverse("kitchen:dish-list"))


class DishUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")
        self.dish = Dish.objects.create(
            name="Dish",
            price=10,
            dish_type=self.dish_type,
            description="Test description",
        )
        self.dish.cooks.add(self.user)

    def test_update_dish(self):
        url = reverse("kitchen:dish-update", args=[self.dish.pk])
        new_cook = Cook.objects.create(
            username="cook",
            password="testt",
            years_of_experience=1
        )

        new_data = {
            "name": "New Dish",
            "description": "Test description1",
            "price": 11,
            "dish_type": self.dish_type.id,
            "cooks": [new_cook.id],
        }
        response = self.client.post(url, new_data)

        self.assertRedirects(response, reverse("kitchen:dish-list"))
        self.assertEqual(response.status_code, 302)
        self.dish.refresh_from_db()
        self.assertEqual(self.dish.name, "New Dish")
        self.assertEqual(self.dish.description, "Test description1")
        self.assertEqual(self.dish.price, 11)
        self.assertEqual(self.dish.dish_type, self.dish_type)


class DishDeleteViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")
        self.dish = Dish.objects.create(
            name="Dish",
            price=10,
            dish_type=self.dish_type,
            description="Test description"
        )
        self.dish.cooks.add(self.user)

    def test_delete_dish(self):
        url = reverse("kitchen:dish-delete", args=[self.dish.id])

        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get,
                                "kitchen/dish_confirm_delete.html")

        response_post = self.client.post(url)

        self.assertRedirects(response_post, reverse("kitchen:dish-list"))
        self.assertEqual(Dish.objects.count(), 0)


class DishTypeCreateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)

    def test_create_dish_type(self):
        url = reverse("kitchen:dish-type-create")
        data = {
            "name": "New Dish Type",
        }
        response = self.client.post(url, data)
        self.assertEqual(DishType.objects.count(), 1)
        self.assertRedirects(response, reverse("kitchen:dish-type-list"))


class DishTypeUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")

    def test_update_dish_type(self):
        url = reverse("kitchen:dish-type-update",
                      args=[self.dish_type.pk])

        new_data = {
            "name": "New Dish Type",
        }
        response = self.client.post(url, new_data)

        self.assertRedirects(response, reverse("kitchen:dish-type-list"))
        self.assertEqual(response.status_code, 302)
        self.dish_type.refresh_from_db()
        self.assertEqual(self.dish_type.name, "New Dish Type")


class DishTypeDeleteViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")

    def test_delete_dish_type(self):
        url = reverse("kitchen:dish-type-delete",
                      args=[self.dish_type.id])

        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get,
                                "kitchen/dishtype_confirm_delete.html")

        response_post = self.client.post(url)

        self.assertRedirects(response_post, reverse("kitchen:dish-type-list"))
        self.assertEqual(DishType.objects.count(), 0)


class CookCreateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)

    def test_create_cook(self):
        url = reverse("kitchen:cook-create")
        data = {
            "username": "user1",
            "first_name": "Test",
            "last_name": "Test",
            "years_of_experience": 10,
            "password1": "strongPassword123",
            "password2": "strongPassword123",
        }
        response = self.client.post(url, data)
        self.assertEqual(Cook.objects.count(), 2)
        self.assertRedirects(response, reverse(
            "kitchen:cook-detail", args=[2]))


class CookUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)
        self.cook = Cook.objects.create(
            username="Cook",
            years_of_experience=3,
        )

    def test_update_cook(self):
        url = reverse("kitchen:cook-update",
                      args=[self.cook.pk])

        new_data = {
            "username": "updated_cook",
            "first_name": "John",
            "last_name": "Doe",
            "email": "test@example.com",
            "years_of_experience": 10,
    }

        response = self.client.post(url, new_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("kitchen:cook-list"))

        self.cook.refresh_from_db()

        self.assertEqual(self.cook.username, "updated_cook")
        self.assertEqual(self.cook.years_of_experience, 10)
        self.assertEqual(self.cook.first_name, "John")


class CookDeleteViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.cook = Cook.objects.create(
            username="Cook",
            years_of_experience=3,
        )
        self.assertEqual(Cook.objects.count(), 2)

    def test_delete_cook(self):
        url = reverse("kitchen:cook-delete",
                      args=[self.cook.id])

        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get,
                                "kitchen/cook_confirm_delete.html")

        response_post = self.client.post(url)

        self.assertRedirects(response_post, reverse("kitchen:cook-list"))
        self.assertEqual(Cook.objects.count(), 1)


class DishFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Test")
        self.cook1 = Cook.objects.create_user(
            username="c1",
            password="test123"
        )
        self.cook2 = Cook.objects.create_user(
            username="c2",
            password="test12"
        )

    def test_form_valid(self):
        form = DishForm(data={
            "name": "Dish1",
            "description": "Test description",
            "price": 10,
            "dish_type": self.dish_type.id,
            "cooks": [self.cook1.id, self.cook2.id]
        })

        self.assertTrue(form.is_valid())
        self.assertIn("cooks", form.fields)

    def test_form_invalid_without_required_fields(self):
        form = DishForm(data={})
        self.assertFalse(form.is_valid())


class CookCreationFormTest(TestCase):
    def test_form_valid(self):
        form = CookCreationForm(data={
            "username": "testcook",
            "password1": "SuperpassWord123",
            "password2": "SuperpassWord123",
            "years_of_experience": 2,
            "first_name": "Test",
            "last_name": "Form",
        })

        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form = CookCreationForm(data={
            "username": "testcook",
            "password1": "pass123",
            "password2": "test123",
        })

        self.assertFalse(form.is_valid())


class CookUpdateFormTest(TestCase):
    def setUp(self):
        self.cook = Cook.objects.create_user(
            username="user",
            password="test123",
            years_of_experience=1
        )

    def test_update_form_valid(self):
        form = CookUpdateForm(
            data={
                "username": "updated",
                "first_name": "New",
                "last_name": "Name",
                "email": "test@example.com",
                "years_of_experience": 5,
            },
            instance=self.cook
        )

        self.assertTrue(form.is_valid())


class CookSearchFormTest(TestCase):
    def test_empty_form_is_valid(self):
        form = CookSearchForm(data={"username": ""})
        self.assertTrue(form.is_valid())

    def test_form_with_value(self):
        form = CookSearchForm(data={"username": "test"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "test")


class DishSearchFormTest(TestCase):
    def test_empty_form_valid(self):
        form = DishSearchForm(data={"name": ""})
        self.assertTrue(form.is_valid())

    def test_form_with_value(self):
        form = DishSearchForm(data={"name": "Dish"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Dish")


class DishTypeSearchFormTest(TestCase):
    def test_empty_form_valid(self):
        form = DishTypeSearchForm(data={"name": ""})
        self.assertTrue(form.is_valid())

    def test_form_with_value(self):
        form = DishTypeSearchForm(data={"name": "Soup"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Soup")
