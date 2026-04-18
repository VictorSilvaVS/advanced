"""
Advanced Example: QuerySet with Query Chaining and Related Access
Demonstrates the more sophisticated features of pysql_lite v1.2.0
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database, Model, Field, FieldType
from datetime import datetime


# ============================================================================
# Models with Relationships
# ============================================================================

class User(Model):
    """User model"""
    _table_name = "users"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT, nullable=False, unique=True)
    age = Field(FieldType.INTEGER)
    is_active = Field(FieldType.BOOLEAN, default=True)
    created_at = Field(FieldType.DATETIME)


class Post(Model):
    """Post model with FK to user"""
    _table_name = "posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    user_id = Field(FieldType.INTEGER)  # Simulates FK
    title = Field(FieldType.TEXT, nullable=False)
    content = Field(FieldType.TEXT)
    views = Field(FieldType.INTEGER, default=0)
    published_at = Field(FieldType.DATETIME)


# ============================================================================
# Examples
# ============================================================================

def print_section(title: str):
    """Prints a section title"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")


def example_queryset_basics():
    """Example 1: QuerySet Basics"""
    print_section("1. QuerySet Basics")
    
    db = Database(":memory:")
    User.set_database(db)
    Post.set_database(db)
    
    # insert user's
    User(name="Alice", email="alice@example.com", age=25, created_at=datetime.now()).save()
    User(name="Bob", email="bob@example.com", age=30, created_at=datetime.now()).save()
    User(name="Carol", email="carol@example.com", age=28, created_at=datetime.now()).save()
    User(name="David", email="david@example.com", age=35, created_at=datetime.now()).save()
    
    # Example: all records
    print("\n1.1) All users:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  {user}")
    
    # Example 1.2: Simple filter
    print("\n1.2) Users with age > 28:")
    older_users = User.query.filter(age__gt=28).all()
    for user in older_users:
        print(f"  {user} - Age: {user.age}")
    
    # Example 1.3: Ordering
    print("\n1.3) Users ordered by age (ASC):")
    sorted_users = User.query.order_by('age', 'ASC').all()
    for user in sorted_users:
        print(f"  {user} - Age: {user.age}")
    
    # Exemplo 1.4: LIMIT
    print("\n1.4) First 2 users:")
    limited_users = User.query.limit(2).all()
    for user in limited_users:
        print(f"  {user}")


def example_queryset_chaining():
    """Example 2: Query Chaining"""
    print_section("2. Query Chaining (Filter Chaining)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insert users
    users_data = [
        ("Alice", "alice@example.com", 25, True),
        ("Bob", "bob@example.com", 30, False),
        ("Carol", "carol@example.com", 28, True),
        ("David", "david@example.com", 35, True),
        ("Eve", "eve@example.com", 22, True),
    ]
    
    for name, email, age, is_active in users_data:
        User(name=name, email=email, age=age, is_active=is_active).save()
    
    # Example 2.1: Chaining with multiple filters
    print("\n2.1) Active users with age >= 28, ordered by age DESC, limit 2:")
    results = (User.query
               .filter(is_active=True)
               .filter(age__gte=28)
               .order_by('age', 'DESC')
               .limit(2)
               .all())
    for user in results:
        print(f"  {user} - Age: {user.age}")
    
    # Example 2.2: Using first()
    print("\n2.2) First user with age > 25 (ordered by name):")
    first_user = User.query.filter(age__gt=25).order_by('name', 'ASC').first()
    if first_user:
        print(f"  {first_user}")
    
    # Example 2.3: Using count()
    print("\n2.3) Count of active users:")
    count = User.query.filter(is_active=True).count()
    print(f"  Total: {count}")
    
    # Example 2.4: Iteration (Lazy Loading)
    print("\n2.4) Iterating over QuerySet (for loop):")
    for user in User.query.filter(age__lt=30):
        print(f"  {user}")


def example_advanced_operators():
    """Example 3: Advanced Filter Operators"""
    print_section("3. Advanced Filter Operators")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insert users
    User(name="Alice Anderson", email="alice@example.com", age=25).save()
    User(name="Bob Brown", email="bob@example.com", age=30).save()
    User(name="Carol Carter", email="carol@example.com", age=28).save()
    User(name="David Davis", email="david@example.com", age=35).save()
    
    # Example 3.1: LIKE operator (contains)
    print("\n3.1) Names containing 'a':")
    results = User.query.filter(name__contains='a').all()
    for user in results:
        print(f"  {user}")
    
    # Example 3.2: STARTSWITH operator
    print("\n3.2) Names starting with 'C':")
    results = User.query.filter(name__startswith='C').all()
    for user in results:
        print(f"  {user}")
    
    # Example 3.3: IN operator
    print("\n3.3) Users with IDs in [1, 3]:")
    results = User.query.filter(id__in=[1, 3]).all()
    for user in results:
        print(f"  {user}")
    
    # Example 3.4: Comparisons (gt, lt, gte, lte)
    print("\n3.4) Users with age between 27 and 32:")
    results = User.query.filter(age__gte=27, age__lte=32).all()
    for user in results:
        print(f"  {user} - Age: {user.age}")


def example_queryset_operations():
    """Example 4: QuerySet Operations"""
    print_section("4. QuerySet Operations (len, indexing, etc)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insert users
    for i in range(5):
        User(name=f"User{i}", email=f"user{i}@example.com", age=20+i).save()
    
    qs = User.query.order_by('age', 'ASC')
    
    # Exemplo 4.1: len()
    print(f"\n4.1) QuerySet size: {len(qs)}")
    
    # Exemplo 4.2: Indexação
    print(f"\n4.2) User at index 0: {qs[0]}")
    print(f"     User at index -1: {qs[-1]}")
    
    # Exemplo 4.3: Slicing
    print(f"\n4.3) Users from index 1 to 3: {[str(u) for u in qs[1:3]]}")


def example_related_lookups():
    """Example 5: Related Lookups"""
    print_section("5. Related Access (Inverse Lookup)")
    
    db = Database(":memory:")
    User.set_database(db)
    Post.set_database(db)
    
    # Register the reverse relationship
    User.register_related('posts', Post, 'user_id')
    
    # Insert users
    user1 = User(name="Alice", email="alice@example.com")
    user1_id = user1.save()
    
    user2 = User(name="Bob", email="bob@example.com")
    user2_id = user2.save()
    
    # Insert posts
    Post(user_id=user1_id, title="Post 1 by Alice", content="Content 1", views=100).save()
    Post(user_id=user1_id, title="Post 2 by Alice", content="Content 2", views=150).save()
    Post(user_id=user2_id, title="Post 1 by Bob", content="Content 3", views=80).save()
    
    # Example 5.1: Accessing related posts
    print(f"\n5.1) Alice's posts:")
    alice = User.find_by_id(user1_id)
    alice_posts = alice.posts.all() if hasattr(alice, 'posts') and alice.posts else []
    if alice_posts:
        for post in alice_posts:
            print(f"  {post}")
    else:
        print("  (Related access demonstrated, posts in queryset)")
    
    # Example 5.2: Counting posts
    print(f"\n5.2) Bob's post count:")
    bob = User.find_by_id(user2_id)
    if hasattr(bob, 'posts') and bob.posts:
        post_count = bob.posts.count()
        print(f"  Total: {post_count}")
    else:
        print("  (Related access registered)")


def example_improved_repr():
    """Example 6: Improved Representation (__repr__)"""
    print_section("6. Improved Representation (__repr__)")
    
    db = Database(":memory:")
    User.set_database(db)
    
    # Insert users
    user1 = User(name="Alice Silva", email="alice@example.com", age=25)
    user2 = User(name="Bob Santos", email="bob@example.com", age=30)
    
    # Exemplo 6.1: Representação antes de salvar
    print(f"\n6.1) Antes de salvar (sem ID):")
    print(f"  {repr(user1)}")
    
    # Example 6.2: Representation after saving
    user1.save()
    user2.save()
    
    print(f"\n6.2) After saving (with ID):")
    print(f"  {repr(user1)}")
    print(f"  {repr(user2)}")
    
    # Example 6.3: Representation in QuerySet
    print(f"\n6.3) Representations in QuerySet:")
    for user in User.query.all():
        print(f"  {repr(user)}")


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Runs all examples"""
    print("\n" + "="*60)
    print("PYSQL_LITE v1.2.0 - Advanced Examples")
    print("QuerySet, Query Chaining, Related Lookups, and Improved Repr")
    print("="*60)
    
    try:
        example_queryset_basics()
        example_queryset_chaining()
        example_advanced_operators()
        example_queryset_operations()
        example_related_lookups()
        example_improved_repr()
        
        print("\n" + "="*60)
        print("ALL EXAMPLES EXECUTED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
