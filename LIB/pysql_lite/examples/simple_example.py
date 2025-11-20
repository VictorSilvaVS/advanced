"""
Exemplo simples de uso do pysql_lite
Demonstra funcionalidades básicas: criar modelo, inserir, consultar e atualizar dados
"""

import sys
import os

# Adiciona o diretório pai ao path para importar pysql_lite
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database, Model, Field, FieldType
from datetime import datetime


# ============================================================================
# Definindo modelos (NOVA SINTAXE: Fields como atributos da classe)
# ============================================================================

class User(Model):
    """Modelo de usuário com nova sintaxe de Fields"""
    _table_name = "users"
    
    # Defina os campos como atributos da classe
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT, nullable=False, unique=True)
    age = Field(FieldType.INTEGER)
    is_active = Field(FieldType.BOOLEAN, default=True)


class Post(Model):
    """Modelo de post com nova sintaxe de Fields"""
    _table_name = "posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    title = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT)
    author_name = Field(FieldType.TEXT, nullable=False)
    created_at = Field(FieldType.DATETIME)
    views = Field(FieldType.INTEGER, default=0)


# ============================================================================
# Exemplo de uso
# ============================================================================

def main():
    # Criar/conectar ao banco de dados
    db = Database(":memory:")  # Usando banco em memória para exemplo
    
    # Inicializar modelos
    User.set_database(db)
    Post.set_database(db)
    
    print("=" * 60)
    print("PYSQL_LITE - Exemplo Simples de Uso")
    print("=" * 60)
    
    # ========== INSERT (CREATE) ==========
    print("\n[1] Inserindo usuários...")
    user1 = User(name="Alice Silva", email="alice@example.com", age=28)
    user1_id = user1.save()
    print(f"  ✓ Usuário inserido: {user1} (ID: {user1_id})")
    
    user2 = User(name="Bob Santos", email="bob@example.com", age=35, is_active=True)
    user2_id = user2.save()
    print(f"  ✓ Usuário inserido: {user2} (ID: {user2_id})")
    
    user3 = User(name="Carol Costa", email="carol@example.com", age=26, is_active=False)
    user3_id = user3.save()
    print(f"  ✓ Usuário inserido: {user3} (ID: {user3_id})")
    
    # ========== SELECT (READ) ==========
    print("\n[2] Buscando todos os usuários...")
    all_users = User.find_all()
    for user in all_users:
        print(f"  • {user.name} ({user.email}) - Age: {user.age} - Active: {user.is_active}")
    
    # ========== FILTER COM OPERADORES AVANÇADOS ==========
    print("\n[3] Filtrando com operadores avançados...")
    
    # Exemplo: Usuários com idade maior que 25
    print("  Usuários com age > 25:")
    older_users = User.filter(age__gt=25)
    for user in older_users:
        print(f"    • {user.name} ({user.age} anos)")
    
    # Exemplo: Usuários ativos (igualdade)
    print("  Usuários ativos:")
    active_users = User.filter(is_active=True)
    for user in active_users:
        print(f"    • {user.name}")
    
    # Exemplo: Usuários com email contendo exemplo
    print("  Usuários com email contendo 'example':")
    example_users = User.filter(email__contains='example')
    for user in example_users:
        print(f"    • {user.email}")
    
    # Exemplo: Usuários com nome começando com C
    print("  Usuários com nome começando com 'C':")
    c_users = User.filter(name__startswith='C')
    for user in c_users:
        print(f"    • {user.name}")
    
    # Exemplo: Usuários com idade entre 26 e 30 (combinando operadores)
    print("  Usuários com age >= 26 e age <= 30:")
    range_users = User.filter(age__gte=26, age__lte=30)
    for user in range_users:
        print(f"    • {user.name} ({user.age} anos)")
    
    # Exemplo: Usuários com IDs específicos
    print("  Usuários com ID em [1, 2]:")
    specific_users = User.filter(id__in=[1, 2])
    for user in specific_users:
        print(f"    • {user.name} (ID: {user.id})")
    
    # ========== QUERY CHAINING (QUERYSET COM ENCADEAMENTO) ==========
    print("\n[3.5] Usando QuerySet com encadeamento de filtros...")
    
    # Exemplo 1: Usuários ativos ordenados por idade descendente, limite 2
    print("  Usuários ativos, ordenados por idade DESC, limite 2:")
    active_ordered = User.query.filter(is_active=True).order_by('age', 'DESC').limit(2).all()
    for user in active_ordered:
        print(f"    • {user}")
    
    # Exemplo 2: Usuários com idade entre 25 e 35, primeiro resultado apenas
    print("  Primeiro usuário com age >= 26 e age <= 30:")
    user_range = User.query.filter(age__gte=26, age__lte=30).first()
    if user_range:
        print(f"    • {user_range}")
    
    # Exemplo 3: Contar usuários com certo critério
    print("  Contagem de usuários com age > 25:")
    count = User.query.filter(age__gt=25).count()
    print(f"    Total: {count}")
    
    # Exemplo 4: Iteração sobre QuerySet (Lazy Loading)
    print("  Iterando sobre QuerySet (Lazy Loading):")
    for user in User.query.filter(is_active=True):
        print(f"    • {user}")
    
    # ========== FIND_ONE ==========
    print("\n[4] Buscando um usuário específico...")
    user_found = User.find_one(name="Alice Silva")
    if user_found:
        print(f"  ✓ Encontrado: {user_found}")
    
    # ========== FIND_BY_ID ==========
    print("\n[5] Buscando usuário por ID...")
    user_by_id = User.find_by_id(1)
    if user_by_id:
        print(f"  ✓ ID 1: {user_by_id}")
    
    # ========== UPDATE ==========
    print("\n[6] Atualizando usuário...")
    user_to_update = User.find_by_id(1)
    user_to_update.age = 29
    user_to_update.is_active = False
    user_to_update.save()
    print(f"  ✓ Usuário atualizado: {user_to_update}")
    
    # ========== INSERT POSTS ==========
    print("\n[7] Inserindo posts...")
    post1 = Post(
        title="Introdução ao Python",
        content="Python é uma linguagem versátil...",
        author_name="Alice Silva",
        created_at=datetime.now(),
        views=150
    )
    post1.save()
    print(f"  ✓ Post inserido: {post1.title}")
    
    post2 = Post(
        title="SQLite para iniciantes",
        content="SQLite é um banco leve e rápido...",
        author_name="Bob Santos",
        created_at=datetime.now(),
        views=200
    )
    post2.save()
    print(f"  ✓ Post inserido: {post2.title}")
    
    # ========== COUNT ==========
    print("\n[8] Contando registros...")
    total_users = User.count()
    total_posts = Post.count()
    print(f"  Total de usuários: {total_users}")
    print(f"  Total de posts: {total_posts}")
    
    # ========== DELETE ==========
    print("\n[9] Deletando um registro...")
    user_delete = User.find_by_id(3)
    if user_delete:
        success = user_delete.delete()
        print(f"  ✓ Usuário deletado: {user_delete.name}")
    
    print(f"  Usuários restantes: {User.count()}")
    
    # ========== DELETE ALL ==========
    print("\n[10] Exibindo estado final...")
    remaining_users = User.find_all()
    print(f"  Usuários finais ({len(remaining_users)}):")
    for user in remaining_users:
        print(f"    • {user.name} - {user.email}")
    
    print("\n" + "=" * 60)
    print("Exemplo finalizado!")
    print("=" * 60)
    
    # Fechar conexão
    db.close()


if __name__ == "__main__":
    main()
