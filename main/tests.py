from django.test import TestCase, Client
from .models import Product

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

    