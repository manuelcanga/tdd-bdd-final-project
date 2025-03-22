# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Check that it matches the original product
        db_product = Product.find(product.id)
        self.assertEqual(db_product.name, product.name)
        self.assertEqual(db_product.description, product.description)
        self.assertEqual(Decimal(db_product.price), product.price)
        self.assertEqual(db_product.available, product.available)
        self.assertEqual(db_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()
        logging.info(product.serialize())
        product.description = "new description"
        before_update_id = product.id
        product.update()
        self.assertIsNotNone(product.id)
        self.assertEqual(product.id, before_update_id)
        self.assertEqual(product.description, "new description")
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        db_product = products[0]
        self.assertEqual(db_product.id, before_update_id)
        self.assertEqual(db_product.name, product.name)
        self.assertEqual(db_product.description, "new description")
        self.assertEqual(Decimal(db_product.price), product.price)
        self.assertEqual(db_product.available, product.available)
        self.assertEqual(db_product.category, product.category)

    def test_update_with_empty_id(self):
        """It should throw a exception when
        a product is updated with empty id"""

        product = ProductFactory()
        logging.info(product.serialize())
        product.id = None
        product.create()
        logging.info(product.serialize())
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Product in database before removing
        products = Product.all()
        self.assertEqual(len(products), 1)

        db_product = Product.find(product.id)
        db_product.delete()

        # Product isnt in database after removing
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should List all Products"""
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(0, 5):
            product = ProductFactory()
            product.id = None
            product.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should find a product by name"""

        product_batch = ProductFactory.create_batch(5)
        for product in product_batch:
            product.create()

        name_to_find = product_batch[0].name

        # count name in batch
        name_times_in_batch = 0
        for i in range(0, 5):
            if product_batch[i].name == name_to_find:
                name_times_in_batch += 1

        # count name in db
        products_from_db = Product.find_by_name(name_to_find)
        self.assertEqual(name_times_in_batch, products_from_db.count())

        # check name in results
        for product_from_db in products_from_db:
            self.assertEqual(name_to_find, product_from_db.name)

    def test_find_a_product_by_availability(self):
        """It should find a product by availability"""

        product_batch = ProductFactory.create_batch(10)
        for product in product_batch:
            product.create()

        available_to_find = product_batch[0].available

        # count availability in batch
        availability_times_in_batch = 0
        for i in range(0, 10):
            if product_batch[i].available == available_to_find:
                availability_times_in_batch += 1

        # count availability in db
        products_from_db = Product.find_by_availability(available_to_find)
        self.assertEqual(availability_times_in_batch, products_from_db.count())

        # check availability in results
        for product_from_db in products_from_db:
            self.assertEqual(available_to_find, product_from_db.available)

    def test_find_a_product_by_category(self):
        """It should find a product by category"""

        product_batch = ProductFactory.create_batch(10)
        for product in product_batch:
            product.create()

        category_to_find = product_batch[0].category

        # count category in batch
        category_times_in_batch = 0
        for i in range(0, 10):
            if product_batch[i].category == category_to_find:
                category_times_in_batch += 1

        # count category in db
        products_from_db = Product.find_by_category(category_to_find)
        self.assertEqual(category_times_in_batch, products_from_db.count())

        # check category in results
        for product_from_db in products_from_db:
            self.assertEqual(category_to_find, product_from_db.category)

    def test_find_a_product_by_price(self):
        """It should find a product by price"""

        product_batch = ProductFactory.create_batch(10)
        for product in product_batch:
            product.create()

        price_to_find = product_batch[0].price

        # count price in batch
        price_times_in_batch = 0
        for i in range(0, 10):
            if product_batch[i].price == price_to_find:
                price_times_in_batch += 1

        # count price in db
        products_from_db = Product.find_by_price(str(price_to_find))
        self.assertEqual(price_times_in_batch, products_from_db.count())

        # check price in results
        for product_from_db in products_from_db:
            self.assertEqual(price_to_find, product_from_db.price)

    def test_deserialize_with_no_valid_available_value(self):
        """It should throw exception in deserialize
        with no valid available value"""

        product = ProductFactory()
        product.create()

        # Not valid available
        dict_to_test = product.serialize()
        dict_to_test["available"] = "fail!"
        self.assertRaises(DataValidationError, product.deserialize, dict_to_test)

    def test_deserialize_without_an_attribute(self):
        """It should throw exception in deserialize
        without an attribute"""

        product = ProductFactory()
        product.create()

        # Without an attribute
        dict_to_test = {}
        self.assertRaises(DataValidationError, product.deserialize, dict_to_test)

    def test_deserialize_with_wrong_attribute(self):
        """It should throw exception in deserialize with wrong attribute"""

        product = ProductFactory()
        product.create()

        # With a wrong attribute
        dict_to_test = product.serialize()
        dict_to_test["category"] = "TDD/BDD"
        self.assertRaises(DataValidationError, product.deserialize, dict_to_test)

    def test_deserialize_with_wrong_category(self):
        """It should throw exception in deserialize with wrong attribute"""

        product = ProductFactory()
        product.create()

        # With a wrong attribute
        dict_to_test = product.serialize()
        dict_to_test["category"] = 15
        self.assertRaises(DataValidationError, product.deserialize, dict_to_test)
