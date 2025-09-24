from django.test import TestCase, Client
from .models import Product
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

# Create your tests here.
class mainTest(TestCase):
    def test_main_url_is_exist(self):
            response = Client().get('')
            self.assertEqual(response.status_code, 200)

    def test_main_using_main_template(self):
            response = Client().get('')
            self.assertTemplateUsed(response, 'main.html')

    def test_nonexistent_page(self):
            response = Client().get('/burhan_always_exists/')
            self.assertEqual(response.status_code, 404)

    def test_product_creation(self):
            product = Product.objects.create(
                name="Sepatu Flash",
                price=500000,
                description="Sepatu nyaman untuk olahraga harian",
                category="other",
                is_featured=True,
                stock=10,
                color="Merah"
            ) 
            self.assertEqual(product.name, "Sepatu Flash")
            self.assertEqual(product.price, 500000)
            self.assertEqual(product.category, "other")
            self.assertTrue(product.is_featured)
            self.assertEqual(product.stock, 10)
           
    def test_product_default_values(self):
            product = Product.objects.create(
                name="Kaos Olgar Pinkeu",
                price=150000,
                description="Kaos nyaman sehari-hari"
            )

            self.assertEqual(product.category, "other")      
            self.assertEqual(product.stock, 0)              
            self.assertFalse(product.is_featured)   

    def test_is_out_of_stock(self):
            product_1 = Product.objects.create(
                name = "Kaos Olgar Pinkeu",
                price=150000,
                description="Kaos nyaman sehari-hari",
                color = "Merah muda",
                stock = 1
            )
            self.assertFalse(product_1.is_out_of_stock)

            product_0 = Product.objects.create(
                name = "Kaos Olgar Pinkeu",
                price=150000,
                description="Kaos nyaman sehari-hari",
                color = "Merah muda",
                stock = 0
            )
            self.assertTrue(product_0.is_out_of_stock)

    def test_reduce_stock_simple(self):
            product = Product.objects.create(
                name="Kaos",
                price=100000,
                description="Kaos nyaman untuk olahraga",
                stock=5
            ) 
            product.reduce_stock(1)
            self.assertEqual(product.stock, 4)

class LucyLocketShopFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create single browser instance for all tests
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close browser after all tests complete
        cls.browser.quit()

    def setUp(self):
        # Create user for testing
        self.test_user = User.objects.create_user(
            username='testadmin',
            password='testpassword'
        )

    def tearDown(self):
        # Clean up browser state between tests
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        # Navigate to blank page to reset state
        self.browser.get("about:blank")

    def login_user(self):
        """Helper method to login user"""
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

    def test_login_page(self):
        # Test login functionality
        self.login_user()

        # Check if login is successful
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Welcome to Lucy Locket Shop!")

        logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertTrue(logout_link.is_displayed())

    def test_register_page(self):
        # Test register functionality
        self.browser.get(f"{self.live_server_url}/register/")

        # Check if register page opens
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        # Fill register form
        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        # Check redirect to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_product(self):
        # Test create product functionality (requires login)
        self.login_user()

        # Go to create product page
        add_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Add Product")
        add_button.click()

        # Fill form
        name_input = self.browser.find_element(By.NAME, "name")
        price_input = self.browser.find_element(By.NAME, "price")
        description_input = self.browser.find_element(By.NAME, "description")
        category_select = self.browser.find_element(By.NAME, "category")
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")
        stock_input = self.browser.find_element(By.NAME, "stock")
        color_input = self.browser.find_element(By.NAME, "color")

        name_input.send_keys("Test Product Name")
        price_input.send_keys("15000000")
        description_input.send_keys("Test product content for selenium testing")

        # Set category (pakai value yang valid → contoh: "training")
        select = Select(category_select)
        select.select_by_value("training")

        thumbnail_input.send_keys("https://example.com/image.jpg")
        is_featured_checkbox.click()
        stock_input.send_keys("10")
        color_input.send_keys("Red")

        # Submit form
        name_input.submit()

        # Check if returned to main page and product list appears
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Product List"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Product List")

        # Check if product name appears on page
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Test Product Name")))
        product_name = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Test Product Name")
        self.assertTrue(product_name.is_displayed())

    def test_product_detail(self):
        # Test product detail page

        self.login_user()

        # Create product for testing
        product = Product.objects.create(
                name="Detail Test Product",
                price=150000,
                description="Content for detail product testing",
                category="training",
                stock=5,
                color="Red",
                user=self.test_user
        )

        # Open product detail page
        self.browser.get(f"{self.live_server_url}/product/{product.id}/")

        # Check if detail page opens correctly
        self.assertIn("Detail Test Product", self.browser.page_source)
        self.assertIn("Content for detail product testing", self.browser.page_source)
        self.assertIn("Training", self.browser.page_source)  # get_category_display
        self.assertIn("Stock: 5", self.browser.page_source)
        self.assertIn("Rp 150,000", self.browser.page_source)


    def test_logout(self):
        # Test logout functionality
        self.login_user()

        # Click logout button - text is inside button, not link
        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        # Check if redirected to login page
        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_product_main_page(self):
    # Test filter functionality on main product page

        Product.objects.create(
                name="My Test Product",
                price=100000,
                description="My product content",
                category="ball",
                stock=10,
                color="Blue",
                user=self.test_user
        )
        Product.objects.create(
                name="Other User Product",
                price=200000,
                description="Other product content",
                category="shoes",
                stock=3,
                color="Black",
                user=self.test_user
        )

        self.login_user()

        wait = WebDriverWait(self.browser, 10)

        # Test filter "All Articles" (ganti ke All Products kalau label template sudah beda)
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Articles")))
        all_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "All Articles")
        all_button.click()
        self.assertIn("My Test Product", self.browser.page_source)
        self.assertIn("Other User Product", self.browser.page_source)

        # Test filter "My Articles" (ganti ke My Products kalau label template sudah beda)
        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Articles")
        my_button.click()
        self.assertIn("My Test Product", self.browser.page_source)

