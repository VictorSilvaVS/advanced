"""
Exemplo mais complexo: Sistema de blog
Demonstra o uso de pysql_lite em um cenário mais realista com nova sintaxe de Fields
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database, Model, Field, FieldType
from datetime import datetime


# ============================================================================
# Modelos do Sistema de Blog (NOVA SINTAXE: Fields como atributos)
# ============================================================================

class Author(Model):
    """Modelo de autor"""
    _table_name = "authors"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    username = Field(FieldType.TEXT, nullable=False, unique=True)
    email = Field(FieldType.TEXT, nullable=False, unique=True)
    bio = Field(FieldType.TEXT)
    created_at = Field(FieldType.DATETIME)
    is_verified = Field(FieldType.BOOLEAN, default=False)


class BlogPost(Model):
    """Modelo de post do blog"""
    _table_name = "blog_posts"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    title = Field(FieldType.TEXT, nullable=False)
    slug = Field(FieldType.TEXT, unique=True)
    content = Field(FieldType.TEXT, nullable=False)
    author = Field(FieldType.TEXT, nullable=False)
    published_at = Field(FieldType.DATETIME)
    updated_at = Field(FieldType.DATETIME)
    is_published = Field(FieldType.BOOLEAN, default=False)
    views = Field(FieldType.INTEGER, default=0)


class Comment(Model):
    """Modelo de comentário"""
    _table_name = "comments"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    post_id = Field(FieldType.INTEGER)
    author = Field(FieldType.TEXT, nullable=False)
    email = Field(FieldType.TEXT)
    content = Field(FieldType.TEXT, nullable=False)
    created_at = Field(FieldType.DATETIME)
    is_approved = Field(FieldType.BOOLEAN, default=False)


class Tag(Model):
    """Modelo de tag"""
    _table_name = "tags"
    
    id = Field(FieldType.INTEGER, primary_key=True)
    name = Field(FieldType.TEXT, nullable=False, unique=True)
    slug = Field(FieldType.TEXT, unique=True)
    post_count = Field(FieldType.INTEGER, default=0)


# ============================================================================
# Funções do Blog
# ============================================================================

class BlogService:
    """Serviço de gerenciamento do blog"""
    
    @staticmethod
    def create_author(username: str, email: str, bio: str = "") -> Author:
        """Cria um novo autor"""
        author = Author(
            username=username,
            email=email,
            bio=bio,
            created_at=datetime.now(),
            is_verified=False
        )
        author.save()
        return author
    
    @staticmethod
    def create_post(title: str, content: str, author: str) -> BlogPost:
        """Cria um novo post"""
        # Gera slug a partir do título
        slug = title.lower().replace(" ", "-")
        
        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            author=author,
            published_at=datetime.now(),
            updated_at=datetime.now(),
            is_published=False,
            views=0
        )
        post.save()
        return post
    
    @staticmethod
    def publish_post(post_id: int) -> bool:
        """Publica um post"""
        post = BlogPost.find_by_id(post_id)
        if post:
            post.is_published = True
            post.published_at = datetime.now()
            post.save()
            return True
        return False
    
    @staticmethod
    def add_comment(post_id: int, author: str, content: str, email: str = "") -> Comment:
        """Adiciona um comentário a um post"""
        comment = Comment(
            post_id=post_id,
            author=author,
            email=email,
            content=content,
            created_at=datetime.now(),
            is_approved=False
        )
        comment.save()
        return comment
    
    @staticmethod
    def get_post_comments(post_id: int) -> list:
        """Retorna todos os comentários de um post"""
        return Comment.filter(post_id=post_id, is_approved=True)
    
    @staticmethod
    def get_author_posts(author: str):
        """Retorna todos os posts de um autor"""
        return BlogPost.filter(author=author, is_published=True)
    
    @staticmethod
    def increment_post_views(post_id: int):
        """Incrementa a contagem de visualizações"""
        post = BlogPost.find_by_id(post_id)
        if post:
            post.views += 1
            post.save()


# ============================================================================
# Exemplo de uso
# ============================================================================

def main():
    # Conectar ao banco de dados
    db = Database(":memory:")
    
    # Inicializar modelos
    Author.set_database(db)
    BlogPost.set_database(db)
    Comment.set_database(db)
    Tag.set_database(db)
    
    print("=" * 70)
    print("PYSQL_LITE - Sistema de Blog")
    print("=" * 70)
    
    # ========== Criar autores ==========
    print("\n[1] Criando autores...")
    author1 = BlogService.create_author(
        username="alice_dev",
        email="alice@blog.com",
        bio="Desenvolvedora Python apaixonada por IA"
    )
    print(f"  ✓ Autor criado: @{author1.username}")
    
    author2 = BlogService.create_author(
        username="bob_code",
        email="bob@blog.com",
        bio="Especialista em arquitetura de software"
    )
    print(f"  ✓ Autor criado: @{author2.username}")
    
    # ========== Criar posts ==========
    print("\n[2] Criando posts...")
    post1 = BlogService.create_post(
        title="Introdução a Machine Learning com Python",
        content="Neste artigo, exploraremos os fundamentos de machine learning...",
        author=author1.username
    )
    print(f"  ✓ Post criado: {post1.title}")
    
    post2 = BlogService.create_post(
        title="Arquitetura Limpa em Aplicações Python",
        content="Entender a importância da arquitetura é crucial para projetos escaláveis...",
        author=author2.username
    )
    print(f"  ✓ Post criado: {post2.title}")
    
    post3 = BlogService.create_post(
        title="Web Scraping Ético com Python",
        content="Como fazer web scraping de forma responsável e legal...",
        author=author1.username
    )
    print(f"  ✓ Post criado: {post3.title}")
    
    # ========== Publicar posts ==========
    print("\n[3] Publicando posts...")
    BlogService.publish_post(post1.id)
    print(f"  ✓ Post '{post1.title}' publicado")
    
    BlogService.publish_post(post2.id)
    print(f"  ✓ Post '{post2.title}' publicado")
    
    BlogService.publish_post(post3.id)
    print(f"  ✓ Post '{post3.title}' publicado")
    
    # ========== Incrementar visualizações ==========
    print("\n[4] Registrando visualizações...")
    for _ in range(5):
        BlogService.increment_post_views(post1.id)
    for _ in range(3):
        BlogService.increment_post_views(post2.id)
    for _ in range(2):
        BlogService.increment_post_views(post3.id)
    print(f"  ✓ Visualizações registradas")
    
    # ========== Adicionar comentários ==========
    print("\n[5] Adicionando comentários...")
    comment1 = BlogService.add_comment(
        post_id=post1.id,
        author="João",
        email="joao@example.com",
        content="Ótimo artigo! Muito útil para iniciantes."
    )
    comment1.is_approved = True
    comment1.save()
    print(f"  ✓ Comentário adicionado ao post 1")
    
    comment2 = BlogService.add_comment(
        post_id=post1.id,
        author="Maria",
        email="maria@example.com",
        content="Você poderia expandir sobre redes neurais?"
    )
    comment2.is_approved = True
    comment2.save()
    print(f"  ✓ Comentário adicionado ao post 1")
    
    comment3 = BlogService.add_comment(
        post_id=post2.id,
        author="Pedro",
        email="pedro@example.com",
        content="Excelente explicação sobre padrões de design!"
    )
    comment3.is_approved = True
    comment3.save()
    print(f"  ✓ Comentário adicionado ao post 2")
    
    # ========== Exibir estatísticas ==========
    print("\n[6] Estatísticas do Blog:")
    print(f"  • Total de autores: {Author.count()}")
    print(f"  • Total de posts: {BlogPost.count()}")
    print(f"  • Total de comentários: {Comment.count()}")
    
    # ========== Exibir posts com visualizações ==========
    print("\n[7] Posts mais visualizados:")
    all_posts = BlogPost.find_all()
    for post in sorted(all_posts, key=lambda p: p.views, reverse=True):
        print(f"  • {post.title}")
        print(f"    Autor: {post.author}")
        print(f"    Visualizações: {post.views}")
        print(f"    Comentários: {len(BlogService.get_post_comments(post.id))}")
    
    # ========== Posts de um autor ==========
    print("\n[8] Posts de Alice:")
    alice_posts = BlogService.get_author_posts(author1.username)
    for post in alice_posts:
        print(f"  • {post.title} ({post.views} views)")
    
    print("\n" + "=" * 70)
    print("Exemplo finalizado com sucesso!")
    print("=" * 70)
    
    # Fechar conexão
    db.close()


if __name__ == "__main__":
    main()
