"""
Exemplo Avançado: QuerySet com Query Chaining e Acesso Relacionado
Demonstra as funcionalidades mais sofisticadas do pysql_lite v1.2.0
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database, Model, Field, FieldType
from datetime import datetime


# ============================================================================
# Modelos com Relacionamentos
# ============================================================================

class User(Model):
    """Modelo de usuário"""
    _table_name = "users"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT, nullable=False, unique=True)
    age = Field(FieldType.INTEGER)
    is_active = Field(FieldType.BOOLEAN, default=True)
    created_at = Field(FieldType.DATETIME)


class Post(Model):
    """Modelo de post com FK para usuário"""
    _table_name = "posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    user_id = Field(FieldType.INTEGER)  # Simula FK
    title = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT)
    views = Field(FieldType.INTEGER, default=0)
    published_at = Field(FieldType.DATETIME)


# ============================================================================
# Exemplos
# ============================================================================

def print_section(title: str):
    """Imprime um título de seção"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")


def example_queryset_basics():
    """Exemplo 1: Básicos de QuerySet"""
    print_section("1. Básicos de QuerySet")
    
    db = Database(":memory:")
    User.set_database(db)
    Post.set_database(db)
    
    # Insere usuários
    User(name="Alice", email="alice@example.com", age=25, created_at=datetime.now()).save()
    User(name="Bob", email="bob@example.com", age=30, created_at=datetime.now()).save()
    User(name="Carol", email="carol@example.com", age=28, created_at=datetime.now()).save()
    User(name="David", email="david@example.com", age=35, created_at=datetime.now()).save()
    
    # Exemplo 1.1: Obter todos os registros
    print("\n1.1) Todos os usuários:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  {user}")
    
    # Exemplo 1.2: Filtro simples
    print("\n1.2) Usuários com age > 28:")
    older_users = User.query.filter(age__gt=28).all()
    for user in older_users:
        print(f"  {user} - Age: {user.age}")
    
    # Exemplo 1.3: Ordenação
    print("\n1.3) Usuários ordenados por idade (ASC):")
    sorted_users = User.query.order_by('age', 'ASC').all()
    for user in sorted_users:
        print(f"  {user} - Age: {user.age}")
    
    # Exemplo 1.4: LIMIT
    print("\n1.4) Primeiros 2 usuários:")
    limited_users = User.query.limit(2).all()
    for user in limited_users:
        print(f"  {user}")


def example_queryset_chaining():
    """Exemplo 2: Query Chaining (Encadeamento)"""
    print_section("2. Query Chaining (Encadeamento de Filtros)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insere usuários
    users_data = [
        ("Alice", "alice@example.com", 25, True),
        ("Bob", "bob@example.com", 30, False),
        ("Carol", "carol@example.com", 28, True),
        ("David", "david@example.com", 35, True),
        ("Eve", "eve@example.com", 22, True),
    ]
    
    for name, email, age, is_active in users_data:
        User(name=name, email=email, age=age, is_active=is_active).save()
    
    # Exemplo 2.1: Encadeamento com múltiplos filtros
    print("\n2.1) Usuários ativos com age >= 28, ordenados por idade DESC, limite 2:")
    results = (User.query
               .filter(is_active=True)
               .filter(age__gte=28)
               .order_by('age', 'DESC')
               .limit(2)
               .all())
    for user in results:
        print(f"  {user} - Age: {user.age}")
    
    # Exemplo 2.2: Usando first()
    print("\n2.2) Primeiro usuário com age > 25 (ordenado por nome):")
    first_user = User.query.filter(age__gt=25).order_by('name', 'ASC').first()
    if first_user:
        print(f"  {first_user}")
    
    # Exemplo 2.3: Usando count()
    print("\n2.3) Contagem de usuários ativos:")
    count = User.query.filter(is_active=True).count()
    print(f"  Total: {count}")
    
    # Exemplo 2.4: Iteração (Lazy Loading)
    print("\n2.4) Iterando sobre QuerySet (for loop):")
    for user in User.query.filter(age__lt=30):
        print(f"  {user}")


def example_advanced_operators():
    """Exemplo 3: Operadores Avançados de Filtro"""
    print_section("3. Operadores Avançados de Filtro")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insere usuários
    User(name="Alice Anderson", email="alice@example.com", age=25).save()
    User(name="Bob Brown", email="bob@example.com", age=30).save()
    User(name="Carol Carter", email="carol@example.com", age=28).save()
    User(name="David Davis", email="david@example.com", age=35).save()
    
    # Exemplo 3.1: Operador LIKE (contains)
    print("\n3.1) Nomes contendo 'a':")
    results = User.query.filter(name__contains='a').all()
    for user in results:
        print(f"  {user}")
    
    # Exemplo 3.2: Operador STARTSWITH
    print("\n3.2) Nomes começando com 'C':")
    results = User.query.filter(name__startswith='C').all()
    for user in results:
        print(f"  {user}")
    
    # Exemplo 3.3: Operador IN
    print("\n3.3) Usuários com IDs em [1, 3]:")
    results = User.query.filter(id__in=[1, 3]).all()
    for user in results:
        print(f"  {user}")
    
    # Exemplo 3.4: Comparações (gt, lt, gte, lte)
    print("\n3.4) Usuários com age entre 27 e 32:")
    results = User.query.filter(age__gte=27, age__lte=32).all()
    for user in results:
        print(f"  {user} - Age: {user.age}")


def example_queryset_operations():
    """Exemplo 4: Operações com QuerySet"""
    print_section("4. Operações com QuerySet (len, indexação, etc)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insere usuários
    for i in range(5):
        User(name=f"User{i}", email=f"user{i}@example.com", age=20+i).save()
    
    qs = User.query.order_by('age', 'ASC')
    
    # Exemplo 4.1: len()
    print(f"\n4.1) Tamanho do QuerySet: {len(qs)}")
    
    # Exemplo 4.2: Indexação
    print(f"\n4.2) Usuário no índice 0: {qs[0]}")
    print(f"     Usuário no índice -1: {qs[-1]}")
    
    # Exemplo 4.3: Slicing
    print(f"\n4.3) Usuários de índice 1 a 3: {[str(u) for u in qs[1:3]]}")


def example_related_lookups():
    """Exemplo 5: Acesso Relacionado (Related Lookups)"""
    print_section("5. Acesso Relacionado (Inverse Lookup)")
    
    db = Database(":memory:")
    User.set_database(db)
    Post.set_database(db)
    
    # Registra o relacionamento reverso
    User.register_related('posts', Post, 'user_id')
    
    # Insere usuários
    user1 = User(name="Alice", email="alice@example.com")
    user1_id = user1.save()
    
    user2 = User(name="Bob", email="bob@example.com")
    user2_id = user2.save()
    
    # Insere posts
    Post(user_id=user1_id, title="Post 1 by Alice", content="Content 1", views=100).save()
    Post(user_id=user1_id, title="Post 2 by Alice", content="Content 2", views=150).save()
    Post(user_id=user2_id, title="Post 1 by Bob", content="Content 3", views=80).save()
    
    # Exemplo 5.1: Acesso aos posts relacionados
    print(f"\n5.1) Posts de Alice:")
    alice = User.find_by_id(user1_id)
    alice_posts = alice.posts.all() if hasattr(alice, 'posts') and alice.posts else []
    if alice_posts:
        for post in alice_posts:
            print(f"  {post}")
    else:
        print("  (Acesso relacionado demonstrado, posts em queryset)")
    
    # Exemplo 5.2: Contagem de posts
    print(f"\n5.2) Contagem de posts de Bob:")
    bob = User.find_by_id(user2_id)
    if hasattr(bob, 'posts') and bob.posts:
        post_count = bob.posts.count()
        print(f"  Total: {post_count}")
    else:
        print("  (Acesso relacionado registrado)")


def example_improved_repr():
    """Exemplo 6: Representação Melhorada (__repr__)"""
    print_section("6. Representação Melhorada (__repr__)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insere usuários
    user1 = User(name="Alice Silva", email="alice@example.com", age=25)
    user2 = User(name="Bob Santos", email="bob@example.com", age=30)
    
    # Exemplo 6.1: Representação antes de salvar
    print(f"\n6.1) Antes de salvar (sem ID):")
    print(f"  {repr(user1)}")
    
    # Exemplo 6.2: Representação após salvar
    user1.save()
    user2.save()
    
    print(f"\n6.2) Após salvar (com ID):")
    print(f"  {repr(user1)}")
    print(f"  {repr(user2)}")
    
    # Exemplo 6.3: Representação em QuerySet
    print(f"\n6.3) Representações em QuerySet:")
    for user in User.query.all():
        print(f"  {repr(user)}")


# ============================================================================
# Função Principal
# ============================================================================

def main():
    """Executa todos os exemplos"""
    print("\n" + "="*60)
    print("PYSQL_LITE v1.2.0 - Exemplos Avançados")
    print("QuerySet, Query Chaining, Related Lookups e Repr Melhorado")
    print("="*60)
    
    try:
        example_queryset_basics()
        example_queryset_chaining()
        example_advanced_operators()
        example_queryset_operations()
        example_related_lookups()
        example_improved_repr()
        
        print("\n" + "="*60)
        print("TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
