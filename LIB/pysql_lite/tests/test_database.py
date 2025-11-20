"""
Testes unitários para pysql_lite
Valida funcionamento de Field, Database e Model
"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database, Model, Field, FieldType


# ============================================================================
# Modelos para testes
# ============================================================================

class TestUser(Model):
    """Modelo de usuário para testes"""
    _table_name = "test_users"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "email": Field(FieldType.TEXT, unique=True),
        "age": Field(FieldType.INTEGER),
        "is_active": Field(FieldType.BOOLEAN, default=True),
        "created_at": Field(FieldType.DATETIME),
    }


class TestProduct(Model):
    """Modelo de produto para testes"""
    _table_name = "test_products"
    _fields = {
        "id": Field(FieldType.INTEGER, primary_key=True),
        "name": Field(FieldType.TEXT, nullable=False),
        "price": Field(FieldType.REAL),
        "quantity": Field(FieldType.INTEGER, default=0),
    }


# ============================================================================
# Testes
# ============================================================================

class TestField(unittest.TestCase):
    """Testes para a classe Field"""
    
    def test_field_creation(self):
        """Testa criação de um campo"""
        field = Field(FieldType.TEXT, nullable=False)
        self.assertEqual(field.field_type, FieldType.TEXT)
        self.assertFalse(field.nullable)
        self.assertFalse(field.primary_key)
    
    def test_field_primary_key(self):
        """Testa campo de chave primária"""
        field = Field(FieldType.INTEGER, primary_key=True)
        self.assertTrue(field.primary_key)
    
    def test_field_with_default(self):
        """Testa campo com valor padrão"""
        field = Field(FieldType.BOOLEAN, default=True)
        self.assertEqual(field.default, True)
    
    def test_field_sql_definition(self):
        """Testa geração da definição SQL do campo"""
        field = Field(FieldType.INTEGER, primary_key=True)
        field.name = "id"
        sql = field.get_sql_definition()
        self.assertIn("PRIMARY KEY", sql)
        self.assertIn("AUTOINCREMENT", sql)


class TestDatabase(unittest.TestCase):
    """Testes para a classe Database"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        Database._instance = None
        self.db = Database(":memory:")
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_database_connection(self):
        """Testa conexão com banco de dados"""
        self.assertIsNotNone(self.db.connection)
    
    def test_database_singleton(self):
        """Testa padrão singleton"""
        db1 = Database.get_instance(":memory:")
        db2 = Database.get_instance(":memory:")
        self.assertIs(db1, db2)
    
    def test_execute_query(self):
        """Testa execução de query"""
        cursor = self.db.execute("SELECT 1 as test")
        row = cursor.fetchone()
        self.assertEqual(row['test'], 1)


class TestModel(unittest.TestCase):
    """Testes para a classe Model"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        Database._instance = None
        self.db = Database(":memory:")
        TestUser.set_database(self.db)
        TestProduct.set_database(self.db)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_model_creation(self):
        """Testa criação de instância do modelo"""
        user = TestUser(name="Alice", email="alice@example.com", age=28)
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.email, "alice@example.com")
        self.assertEqual(user.age, 28)
        self.assertTrue(user.is_active)  # valor padrão
    
    def test_model_save_insert(self):
        """Testa inserção de registro"""
        user = TestUser(name="Bob", email="bob@example.com", age=30)
        user_id = user.save()
        
        self.assertIsNotNone(user_id)
        self.assertEqual(user.id, user_id)
    
    def test_model_save_update(self):
        """Testa atualização de registro"""
        user = TestUser(name="Carol", email="carol@example.com", age=25)
        user_id = user.save()
        
        # Atualizar
        user.age = 26
        user.save()
        
        # Verificar
        updated_user = TestUser.find_by_id(user_id)
        self.assertEqual(updated_user.age, 26)
    
    def test_find_all(self):
        """Testa busca de todos os registros"""
        TestUser(name="User1", email="user1@example.com").save()
        TestUser(name="User2", email="user2@example.com").save()
        TestUser(name="User3", email="user3@example.com").save()
        
        users = TestUser.find_all()
        self.assertEqual(len(users), 3)
    
    def test_find_by_id(self):
        """Testa busca por ID"""
        user = TestUser(name="Diana", email="diana@example.com", age=24)
        user_id = user.save()
        
        found_user = TestUser.find_by_id(user_id)
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.name, "Diana")
    
    def test_find_one(self):
        """Testa busca de um registro específico"""
        TestUser(name="Eva", email="eva@example.com", age=27).save()
        
        found_user = TestUser.find_one(name="Eva")
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.email, "eva@example.com")
    
    def test_filter(self):
        """Testa filtro de registros"""
        TestUser(name="User1", email="user1@example.com", is_active=True).save()
        TestUser(name="User2", email="user2@example.com", is_active=False).save()
        TestUser(name="User3", email="user3@example.com", is_active=True).save()
        
        active_users = TestUser.filter(is_active=True)
        self.assertEqual(len(active_users), 2)
    
    def test_count(self):
        """Testa contagem de registros"""
        TestUser(name="User1", email="user1@example.com").save()
        TestUser(name="User2", email="user2@example.com").save()
        
        count = TestUser.count()
        self.assertEqual(count, 2)
    
    def test_delete_by_id(self):
        """Testa deleção por ID"""
        user = TestUser(name="Frank", email="frank@example.com")
        user_id = user.save()
        
        success = TestUser.delete_by_id(user_id)
        self.assertTrue(success)
        
        found_user = TestUser.find_by_id(user_id)
        self.assertIsNone(found_user)
    
    def test_delete_instance(self):
        """Testa deleção de instância"""
        user = TestUser(name="Grace", email="grace@example.com")
        user.save()
        
        success = user.delete()
        self.assertTrue(success)
        
        found_user = TestUser.find_one(name="Grace")
        self.assertIsNone(found_user)
    
    def test_delete_all(self):
        """Testa deleção de todos os registros"""
        TestUser(name="User1", email="user1@example.com").save()
        TestUser(name="User2", email="user2@example.com").save()
        TestUser(name="User3", email="user3@example.com").save()
        
        deleted = TestUser.delete_all()
        self.assertEqual(deleted, 3)
        
        count = TestUser.count()
        self.assertEqual(count, 0)
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        user = TestUser(name="Henry", email="henry@example.com", age=32)
        user.save()
        
        user_dict = user.to_dict()
        self.assertIn("name", user_dict)
        self.assertIn("email", user_dict)
        self.assertEqual(user_dict["name"], "Henry")
    
    def test_boolean_field(self):
        """Testa campo booleano"""
        user1 = TestUser(name="User1", email="user1@example.com", is_active=True)
        user2 = TestUser(name="User2", email="user2@example.com", is_active=False)
        
        user1.save()
        user2.save()
        
        found_user1 = TestUser.find_by_id(user1.id)
        found_user2 = TestUser.find_by_id(user2.id)
        
        self.assertTrue(found_user1.is_active)
        self.assertFalse(found_user2.is_active)
    
    def test_datetime_field(self):
        """Testa campo de data/hora"""
        now = datetime.now()
        user = TestUser(
            name="User",
            email="user@example.com",
            created_at=now
        )
        user.save()
        
        found_user = TestUser.find_by_id(user.id)
        self.assertIsNotNone(found_user.created_at)
        # Compara apenas até segundos (SQLite trunca microssegundos)
        self.assertEqual(
            found_user.created_at.replace(microsecond=0),
            now.replace(microsecond=0)
        )
    
    def test_real_field(self):
        """Testa campo de números reais"""
        product1 = TestProduct(name="Product1", price=19.99)
        product2 = TestProduct(name="Product2", price=29.50)
        
        product1.save()
        product2.save()
        
        found_product = TestProduct.find_by_id(product1.id)
        self.assertAlmostEqual(found_product.price, 19.99, places=2)
    
    def test_default_values(self):
        """Testa valores padrão"""
        user = TestUser(name="User", email="user@example.com")
        self.assertTrue(user.is_active)  # padrão True
        
        product = TestProduct(name="Product", price=10.0)
        self.assertEqual(product.quantity, 0)  # padrão 0


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        Database._instance = None
        self.db = Database(":memory:")
        TestUser.set_database(self.db)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_workflow_create_read_update_delete(self):
        """Testa fluxo completo: criar, ler, atualizar, deletar"""
        # CREATE
        user = TestUser(name="Integration Test", email="test@example.com", age=30)
        user_id = user.save()
        self.assertIsNotNone(user_id)
        
        # READ
        found_user = TestUser.find_by_id(user_id)
        self.assertEqual(found_user.name, "Integration Test")
        
        # UPDATE
        found_user.age = 31
        found_user.save()
        
        updated_user = TestUser.find_by_id(user_id)
        self.assertEqual(updated_user.age, 31)
        
        # DELETE
        success = updated_user.delete()
        self.assertTrue(success)
        
        final_user = TestUser.find_by_id(user_id)
        self.assertIsNone(final_user)


class TestQuerySet(unittest.TestCase):
    """Testes para a classe QuerySet com Query Chaining"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        from database import QuerySet
        self.db = Database(":memory:")
        TestUser.set_database(self.db)
        
        # Insere dados de teste
        TestUser(name="Alice", email="alice@example.com", age=25, is_active=True).save()
        TestUser(name="Bob", email="bob@example.com", age=30, is_active=False).save()
        TestUser(name="Carol", email="carol@example.com", age=35, is_active=True).save()
        TestUser(name="David", email="david@example.com", age=28, is_active=True).save()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_queryset_all(self):
        """Testa obtenção de todos os registros via QuerySet"""
        results = TestUser.query.all()
        self.assertEqual(len(results), 4)
    
    def test_queryset_filter(self):
        """Testa filtro com QuerySet"""
        results = TestUser.query.filter(is_active=True).all()
        self.assertEqual(len(results), 3)
    
    def test_queryset_order_by(self):
        """Testa ordenação com QuerySet"""
        results = TestUser.query.order_by('age', 'ASC').all()
        ages = [u.age for u in results]
        self.assertEqual(ages, [25, 28, 30, 35])
    
    def test_queryset_order_by_desc(self):
        """Testa ordenação descendente com QuerySet"""
        results = TestUser.query.order_by('age', 'DESC').all()
        ages = [u.age for u in results]
        self.assertEqual(ages, [35, 30, 28, 25])
    
    def test_queryset_limit(self):
        """Testa limite de registros com QuerySet"""
        results = TestUser.query.limit(2).all()
        self.assertEqual(len(results), 2)
    
    def test_queryset_first(self):
        """Testa obtenção do primeiro registro"""
        first = TestUser.query.order_by('age', 'ASC').first()
        self.assertEqual(first.name, "Alice")
    
    def test_queryset_count(self):
        """Testa contagem de registros"""
        count = TestUser.query.filter(is_active=True).count()
        self.assertEqual(count, 3)
    
    def test_queryset_chaining(self):
        """Testa encadeamento completo de operações"""
        results = TestUser.query.filter(
            age__gt=25
        ).filter(
            is_active=True
        ).order_by(
            'age', 'ASC'
        ).limit(2).all()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].name, "David")
        self.assertEqual(results[1].name, "Carol")
    
    def test_queryset_iteration(self):
        """Testa iteração sobre QuerySet"""
        qs = TestUser.query.filter(is_active=True)
        count = 0
        for user in qs:
            count += 1
        self.assertEqual(count, 3)
    
    def test_queryset_len(self):
        """Testa uso de len() em QuerySet"""
        qs = TestUser.query.filter(is_active=True)
        self.assertEqual(len(qs), 3)
    
    def test_queryset_getitem(self):
        """Testa indexação em QuerySet"""
        qs = TestUser.query.order_by('age', 'ASC')
        self.assertEqual(qs[0].name, "Alice")
        self.assertEqual(qs[1].name, "David")


class TestModelRepresentation(unittest.TestCase):
    """Testes para __repr__ melhorado"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.db = Database(":memory:")
        TestUser.set_database(self.db)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.db.close()
        Database._instance = None
    
    def test_repr_new_instance(self):
        """Testa __repr__ para instância nova (sem ID)"""
        user = TestUser(name="Test User", email="test@example.com")
        repr_str = repr(user)
        self.assertIn("TestUser", repr_str)
        self.assertIn("novo", repr_str)
    
    def test_repr_saved_instance(self):
        """Testa __repr__ para instância salva (com ID)"""
        user = TestUser(name="Test User", email="test@example.com")
        user.save()
        repr_str = repr(user)
        self.assertIn("TestUser", repr_str)
        self.assertIn("pk=1", repr_str)
        self.assertIn("Test User", repr_str)


# ============================================================================
# Executar testes
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
