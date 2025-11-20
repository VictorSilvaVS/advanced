"""
pysql_lite - Mini-ORM para SQLite
Camada de abstração simples para interagir com SQLite sem SQL complexo
"""

import sqlite3
import os
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
from enum import Enum

# Type variable para uso genérico
T = TypeVar('T', bound='Model')


class FieldType(Enum):
    """Tipos de campos suportados"""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    REAL = "REAL"
    BLOB = "BLOB"
    BOOLEAN = "BOOLEAN"  # Armazenado como INTEGER no SQLite, mas marcado como BOOLEAN logicamente
    DATETIME = "DATETIME"  # Armazenado como TEXT no SQLite em formato ISO


class QuerySet:
    """
    Representa um conjunto de queries que será executado no banco.
    Permite encadeamento de filtros (Query Chaining) com Lazy Loading.
    """
    
    def __init__(self, model_class: Type['Model']):
        """
        Args:
            model_class: Classe do modelo para o qual a query é construída
        """
        self.model_class = model_class
        self.filters: Dict[str, tuple] = {}  # Armazena {campo: (operador, valor)}
        self.order_fields: List[tuple] = []  # Armazena [(campo, direcção), ...]
        self._limit_value: Optional[int] = None
        self._executed = False
        self._results: List['Model'] = []
    
    def filter(self, **kwargs) -> 'QuerySet':
        """
        Adiciona um filtro ao query (AND logic)
        
        Returns:
            Self para permitir encadeamento
        """
        for key, value in kwargs.items():
            # Extrai campo e operador
            parts = key.split('__')
            field_name = parts[0]
            operator = parts[1] if len(parts) > 1 else 'eq'
            
            # Valida que o campo existe
            if field_name not in self.model_class._fields:
                raise ValueError(f"Campo '{field_name}' não existe no modelo {self.model_class.__name__}")
            
            self.filters[key] = (operator, value)
        
        return self
    
    def order_by(self, field_name: str, direction: str = 'ASC') -> 'QuerySet':
        """
        Adiciona ordenação ao query
        
        Args:
            field_name: Nome do campo para ordenar
            direction: 'ASC' ou 'DESC'
        
        Returns:
            Self para permitir encadeamento
        """
        if field_name not in self.model_class._fields:
            raise ValueError(f"Campo '{field_name}' não existe no modelo {self.model_class.__name__}")
        
        if direction.upper() not in ['ASC', 'DESC']:
            raise ValueError(f"Direção deve ser 'ASC' ou 'DESC', recebido: {direction}")
        
        self.order_fields.append((field_name, direction.upper()))
        return self
    
    def limit(self, count: int) -> 'QuerySet':
        """
        Limita o número de registros retornados
        
        Args:
            count: Número máximo de registros
        
        Returns:
            Self para permitir encadeamento
        """
        if count < 0:
            raise ValueError("LIMIT deve ser >= 0")
        
        self._limit_value = count
        return self
    
    def _execute(self) -> List['Model']:
        """
        Executa o query no banco de dados (Lazy Loading)
        Chamado automaticamente ao materializar os resultados
        """
        if self._executed:
            return self._results
        
        # Se não há filtros, retorna todos
        if not self.filters:
            results = self.model_class.find_all()
        else:
            # Reconstrói os kwargs com a sintaxe original para usar o filter() existente
            kwargs = {}
            for key, (operator, value) in self.filters.items():
                kwargs[key] = value
            results = self.model_class.filter(**kwargs)
        
        # Aplica ordenação se houver
        if self.order_fields:
            for field_name, direction in reversed(self.order_fields):
                reverse = direction == 'DESC'
                results = sorted(
                    results,
                    key=lambda x: getattr(x, field_name, None) or '',
                    reverse=reverse
                )
        
        # Aplica LIMIT se houver
        if self._limit_value is not None:
            results = results[:self._limit_value]
        
        self._results = results
        self._executed = True
        return self._results
    
    def all(self) -> List['Model']:
        """Retorna todos os resultados do query"""
        return self._execute()
    
    def first(self) -> Optional['Model']:
        """Retorna o primeiro resultado ou None"""
        results = self._execute()
        return results[0] if results else None
    
    def count(self) -> int:
        """Retorna a quantidade de resultados"""
        results = self._execute()
        return len(results)
    
    def __iter__(self):
        """Permite iteração sobre os resultados (Lazy Loading)"""
        return iter(self._execute())
    
    def __len__(self):
        """Permite usar len() no QuerySet"""
        return self.count()
    
    def __getitem__(self, index):
        """Permite indexação no QuerySet"""
        return self._execute()[index]
    
    def __repr__(self):
        """Representação em string do QuerySet"""
        filters_str = ', '.join(self.filters.keys()) if self.filters else 'sem filtros'
        return f"<QuerySet: {self.model_class.__name__} ({filters_str})>"


class ForeignKey:
    """Representa uma referência a outro modelo (chave estrangeira)"""
    
    def __init__(self, model: Type['Model'], on_delete: str = "CASCADE"):
        """
        Args:
            model: Classe do modelo referenciado
            on_delete: Ação ao deletar registro referenciado (CASCADE, SET NULL, RESTRICT)
        """
        self.model = model
        self.on_delete = on_delete
        self.target_table: Optional[str] = None
        self.target_pk: str = "id"
    
    def get_constraint_sql(self, table_name: str, column_name: str) -> str:
        """Retorna a clausula SQL para a chave estrangeira"""
        if self.target_table is None:
            # Tenta determinar a tabela alvo
            if hasattr(self.model, '_table_name'):
                self.target_table = self.model._table_name
            else:
                self.target_table = self.model.__name__.lower()
        
        return f"FOREIGN KEY ({column_name}) REFERENCES {self.target_table}({self.target_pk}) ON DELETE {self.on_delete}"


class Field:
    """Representa um campo na tabela"""
    
    def __init__(
        self,
        field_type: FieldType = FieldType.TEXT,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        unique: bool = False,
        foreign_key: Optional['ForeignKey'] = None
    ):
        self.field_type = field_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.foreign_key = foreign_key
        self.name: Optional[str] = None
    
    def get_sql_definition(self) -> str:
        """Retorna a definição SQL do campo"""
        # Mapeia tipos Python para tipos SQLite
        type_map = {
            FieldType.INTEGER: "INTEGER",
            FieldType.TEXT: "TEXT",
            FieldType.REAL: "REAL",
            FieldType.BLOB: "BLOB",
            FieldType.BOOLEAN: "INTEGER",  # SQLite não tem BOOLEAN
            FieldType.DATETIME: "TEXT",    # Armazena como ISO format
        }
        
        sql_type = type_map.get(self.field_type, self.field_type.value)
        
        parts = [self.name or "", sql_type]
        
        if self.primary_key:
            parts.append("PRIMARY KEY AUTOINCREMENT")
        
        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")
        
        if self.unique:
            parts.append("UNIQUE")
        
        if self.default is not None and not self.primary_key:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            else:
                parts.append(f"DEFAULT {self.default}")
        
        return " ".join(parts)


class Database:
    """Gerenciador de conexão com SQLite"""
    
    _instance: Optional['Database'] = None
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            db_path: Caminho do arquivo SQLite (":memory:" para banco em memória)
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
    
    @classmethod
    def get_instance(cls, db_path: str = ":memory:") -> 'Database':
        """Singleton pattern para gerenciar uma única conexão"""
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance
    
    def _connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            # Ativa suporte a chaves estrangeiras
            self.connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao conectar ao banco de dados: {e}")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa uma query no banco de dados"""
        if self.connection is None:
            raise RuntimeError("Banco de dados não conectado")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            raise RuntimeError(f"Erro ao executar query: {e}\nQuery: {query}")
    
    def commit(self):
        """Confirma transação"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Desfaz transação"""
        if self.connection:
            self.connection.rollback()
    
    def close(self):
        """Fecha conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None
            Database._instance = None
    
    def create_table(self, table_name: str, fields: Dict[str, Field]):
        """Cria uma tabela no banco de dados"""
        field_defs = []
        constraints = []
        
        for field_name, field in fields.items():
            field.name = field_name
            field_defs.append(field.get_sql_definition())
            
            # Adiciona constraint de chave estrangeira se existir
            if field.foreign_key:
                constraint_sql = field.foreign_key.get_constraint_sql(table_name, field_name)
                constraints.append(constraint_sql)
        
        # Combina definições de campos e constraints
        all_parts = field_defs + constraints
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(all_parts)})"
        
        try:
            self.execute(sql)
            self.commit()
        except RuntimeError as e:
            raise RuntimeError(f"Erro ao criar tabela {table_name}: {e}")


class QueryProperty:
    """Descriptor que permite acessar query como propriedade de classe"""
    
    def __get__(self, obj, objtype=None):
        """Retorna um QuerySet para o modelo"""
        if objtype is None:
            objtype = type(obj)
        return QuerySet(objtype)
    
    def __set_name__(self, owner, name):
        self.name = name


class RelatedManager:
    """
    Descriptor que permite acesso relacionado reverso (Inverse Lookup)
    Permite fazer: usuario.posts para acessar todos os posts do usuário
    """
    
    def __init__(self, related_model: Type['Model'], foreign_key_field: str, 
                 parent_model: Type['Model'], parent_pk_field: str):
        """
        Args:
            related_model: Classe do modelo relacionado (ex: Post)
            foreign_key_field: Nome do campo FK no modelo relacionado (ex: 'user_id')
            parent_model: Classe do modelo pai (ex: User)
            parent_pk_field: Nome do campo PK no modelo pai (ex: 'id')
        """
        self.related_model = related_model
        self.foreign_key_field = foreign_key_field
        self.parent_model = parent_model
        self.parent_pk_field = parent_pk_field
        self.parent_instance: Optional['Model'] = None
    
    def __set_name__(self, owner: Type['Model'], name: str):
        """Chamado quando o descriptor é atribuído a um atributo de classe"""
        self.name = name
    
    def __get__(self, obj: Optional['Model'], objtype: Type['Model']) -> Optional['QuerySet']:
        """
        Retorna um QuerySet para filtrar os relacionados
        
        Exemplo:
            usuario = Usuario.find_by_id(1)
            posts = usuario.posts.all()  # Retorna todos os posts do usuário
        """
        if obj is None:
            # Acesso via classe, não instância
            return None
        
        # Constrói o filtro baseado no campo FK
        parent_pk_value = getattr(obj, self.parent_pk_field, None)
        
        if parent_pk_value is None:
            # Não há instância definida, retorna queryset vazio
            return QuerySet(self.related_model).filter(**{f"{self.foreign_key_field}__eq": -1})
        
        # Retorna QuerySet filtrado pelo FK
        return self.related_model.query.filter(**{f"{self.foreign_key_field}__eq": parent_pk_value})


class Model:
    """Classe base para modelos de dados"""
    
    # Deve ser definido nas subclasses
    _table_name: str = None
    _fields: Dict[str, Field] = {}
    _database: Optional[Database] = None
    _initialized: bool = False
    
    # Descriptor para acessar query como propriedade
    query = QueryProperty()
    
    def __init__(self, **kwargs):
        """Inicializa uma instância do modelo"""
        # Inicializa o modelo se não tiver sido inicializado
        if not self.__class__._initialized:
            self.__class__._initialize_model()
        
        # Inicializa os campos com os valores fornecidos ou padrões
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            elif field.default is not None:
                setattr(self, field_name, field.default)
            else:
                setattr(self, field_name, None)
    
    @classmethod
    def _extract_fields(cls):
        """Extrai automaticamente os Fields definidos como atributos da classe"""
        extracted_fields = {}
        
        # Varre os atributos da classe procurando por Fields
        for attr_name in dir(cls):
            # Pula atributos privados, métodos herdados e métodos especiais
            if attr_name.startswith('_'):
                continue
            
            # Obtém o atributo da classe (não da instância)
            try:
                attr_value = getattr(cls, attr_name)
            except AttributeError:
                continue
            
            # Se for um Field, adiciona aos campos extraídos
            if isinstance(attr_value, Field):
                attr_value.name = attr_name
                extracted_fields[attr_name] = attr_value
                
                # Remove o Field do namespace da classe para evitar conflitos
                try:
                    delattr(cls, attr_name)
                except AttributeError:
                    pass
        
        return extracted_fields
    
    @classmethod
    def _validate_primary_key(cls):
        """Valida que exista exatamente uma chave primária"""
        pk_count = sum(1 for field in cls._fields.values() if field.primary_key)
        
        if pk_count == 0:
            # Se não houver PK, cria uma automaticamente
            id_field = Field(FieldType.INTEGER, primary_key=True)
            id_field.name = "id"
            cls._fields["id"] = id_field
        elif pk_count > 1:
            raise RuntimeError(
                f"Modelo {cls.__name__} tem mais de uma chave primária definida. "
                f"Apenas uma chave primária é permitida por modelo."
            )
    
    @classmethod
    def _get_pk_field_name(cls) -> str:
        """Retorna o nome do campo primary key"""
        for field_name, field in cls._fields.items():
            if field.primary_key:
                return field_name
        return "id"  # Fallback
    
    @classmethod
    def _initialize_model(cls, database: Optional[Database] = None):
        """Inicializa metadados do modelo e cria a tabela"""
        # Evita reinicializar
        if cls._initialized:
            return
        
        if cls._table_name is None:
            cls._table_name = cls.__name__.lower()
        
        # Garante que cls._fields seja específico dessa classe, não herdado
        if cls._fields == cls.__bases__[0]._fields if cls.__bases__ else False:
            cls._fields = {}
        
        # Extrai os Fields definidos como atributos
        extracted_fields = cls._extract_fields()
        cls._fields.update(extracted_fields)
        
        # Valida a chave primária
        cls._validate_primary_key()
        
        if database is None:
            database = Database.get_instance()
        
        cls._database = database
        
        # Cria a tabela se houver campos
        if cls._fields:
            cls._database.create_table(cls._table_name, cls._fields)
        
        # Marca o modelo como inicializado
        cls._initialized = True
    
    @classmethod
    def set_database(cls, database: Database):
        """Define o banco de dados para o modelo"""
        cls._database = database
        cls._initialized = False  # Força reinicialização com novo banco
        cls._initialize_model(database)
    
    @classmethod
    def register_related(cls, relation_name: str, related_model: Type['Model'], 
                        foreign_key_field: str):
        """
        Registra um relacionamento reverso (Inverse Lookup)
        
        Args:
            relation_name: Nome da propriedade de acesso (ex: 'posts')
            related_model: Classe do modelo relacionado (ex: Post)
            foreign_key_field: Nome do campo FK no modelo relacionado (ex: 'user_id')
        
        Exemplo:
            class User(Model):
                ...
            
            class Post(Model):
                ...
            
            # Registra o relacionamento
            User.register_related('posts', Post, 'user_id')
            
            # Agora pode fazer:
            user = User.find_by_id(1)
            posts = user.posts.all()
        """
        pk_field = cls._get_pk_field_name()
        related_manager = RelatedManager(
            related_model=related_model,
            foreign_key_field=foreign_key_field,
            parent_model=cls,
            parent_pk_field=pk_field
        )
        setattr(cls, relation_name, related_manager)
    
    def save(self) -> int:
        """
        Salva a instância no banco de dados
        
        Returns:
            ID da linha inserida/atualizada
        """
        if self._database is None:
            self._initialize_model()
        
        # Determina se é INSERT ou UPDATE
        pk_field = None
        pk_value = None
        
        for field_name, field in self._fields.items():
            if field.primary_key:
                pk_field = field_name
                pk_value = getattr(self, field_name, None)
                break
        
        # INSERT
        if pk_value is None:
            fields_to_insert = []
            values_to_insert = []
            placeholders = []
            
            for field_name, field in self._fields.items():
                if not field.primary_key:
                    value = getattr(self, field_name, None)
                    fields_to_insert.append(field_name)
                    
                    # Converte tipos especiais
                    if isinstance(value, bool):
                        values_to_insert.append(1 if value else 0)
                    elif isinstance(value, datetime):
                        values_to_insert.append(value.isoformat())
                    else:
                        values_to_insert.append(value)
                    
                    placeholders.append("?")
            
            sql = f"""
                INSERT INTO {self._table_name} ({', '.join(fields_to_insert)})
                VALUES ({', '.join(placeholders)})
            """
            
            cursor = self._database.execute(sql, tuple(values_to_insert))
            self._database.commit()
            
            # Atualiza o ID da linha inserida
            if pk_field:
                setattr(self, pk_field, cursor.lastrowid)
            
            return cursor.lastrowid
        
        # UPDATE
        else:
            set_clauses = []
            values = []
            
            for field_name, field in self._fields.items():
                if not field.primary_key:
                    value = getattr(self, field_name, None)
                    set_clauses.append(f"{field_name} = ?")
                    
                    # Converte tipos especiais
                    if isinstance(value, bool):
                        values.append(1 if value else 0)
                    elif isinstance(value, datetime):
                        values.append(value.isoformat())
                    else:
                        values.append(value)
            
            values.append(pk_value)
            
            sql = f"""
                UPDATE {self._table_name}
                SET {', '.join(set_clauses)}
                WHERE {pk_field} = ?
            """
            
            self._database.execute(sql, tuple(values))
            self._database.commit()
            
            return pk_value
    
    @classmethod
    def find_all(cls) -> List['Model']:
        """
        Retorna todas as instâncias da tabela
        
        Returns:
            Lista de instâncias do modelo
        """
        if cls._database is None:
            cls._initialize_model()
        
        sql = f"SELECT * FROM {cls._table_name}"
        cursor = cls._database.execute(sql)
        
        results = []
        for row in cursor.fetchall():
            obj = cls._from_row(row)
            results.append(obj)
        
        return results
    
    @classmethod
    def filter(cls, **kwargs) -> List['Model']:
        """
        Filtra instâncias por critérios com suporte a operadores avançados
        
        Args:
            **kwargs: Pares chave-valor para filtrar
                      Suporta operadores usando sintaxe: campo__operador=valor
                      
                      Operadores suportados:
                      - (sem operador): igualdade (campo=valor)
                      - __gt: maior que (>)
                      - __gte: maior ou igual (>=)
                      - __lt: menor que (<)
                      - __lte: menor ou igual (<=)
                      - __ne: não igual (!=)
                      - __like: LIKE pattern (SQL LIKE)
                      - __in: IN (valor1, valor2, ...)
                      - __contains: contém substring (LIKE %valor%)
                      - __startswith: começa com (LIKE valor%)
                      - __endswith: termina com (LIKE %valor)
        
        Returns:
            Lista de instâncias que correspondem aos critérios
            
        Exemplos:
            Usuario.filter(idade__gt=25)           # idade > 25
            Usuario.filter(nome__like='A%')        # nome começa com A
            Usuario.filter(status__in=['ativo', 'pendente'])
            Usuario.filter(email__contains='@gmail')
        """
        if cls._database is None:
            cls._initialize_model()
        
        if not kwargs:
            return cls.find_all()
        
        where_clauses = []
        values = []
        
        for key, value in kwargs.items():
            # Parse the key to extract field name and operator
            parts = key.split('__')
            field_name = parts[0]
            operator = parts[1] if len(parts) > 1 else 'eq'
            
            # Valida que o campo existe
            if field_name not in cls._fields:
                raise ValueError(f"Campo '{field_name}' não existe no modelo {cls.__name__}")
            
            # Constrói a cláusula WHERE baseada no operador
            if operator == 'eq':
                where_clauses.append(f"{field_name} = ?")
                if isinstance(value, bool):
                    values.append(1 if value else 0)
                elif isinstance(value, datetime):
                    values.append(value.isoformat())
                else:
                    values.append(value)
            
            elif operator == 'gt':
                where_clauses.append(f"{field_name} > ?")
                values.append(value)
            
            elif operator == 'gte':
                where_clauses.append(f"{field_name} >= ?")
                values.append(value)
            
            elif operator == 'lt':
                where_clauses.append(f"{field_name} < ?")
                values.append(value)
            
            elif operator == 'lte':
                where_clauses.append(f"{field_name} <= ?")
                values.append(value)
            
            elif operator == 'ne':
                where_clauses.append(f"{field_name} != ?")
                values.append(value)
            
            elif operator == 'like':
                where_clauses.append(f"{field_name} LIKE ?")
                values.append(value)
            
            elif operator == 'contains':
                where_clauses.append(f"{field_name} LIKE ?")
                values.append(f"%{value}%")
            
            elif operator == 'startswith':
                where_clauses.append(f"{field_name} LIKE ?")
                values.append(f"{value}%")
            
            elif operator == 'endswith':
                where_clauses.append(f"{field_name} LIKE ?")
                values.append(f"%{value}")
            
            elif operator == 'in':
                # Para operador IN, value deve ser uma lista
                if not isinstance(value, (list, tuple)):
                    raise ValueError(f"Operador '__in' requer uma lista/tupla, recebido {type(value)}")
                
                placeholders = ','.join(['?' for _ in value])
                where_clauses.append(f"{field_name} IN ({placeholders})")
                values.extend(value)
            
            else:
                raise ValueError(f"Operador '{operator}' não é suportado. Operadores válidos: "
                                 "gt, gte, lt, lte, ne, like, contains, startswith, endswith, in")
        
        sql = f"""
            SELECT * FROM {cls._table_name}
            WHERE {' AND '.join(where_clauses)}
        """
        
        cursor = cls._database.execute(sql, tuple(values))
        
        results = []
        for row in cursor.fetchall():
            obj = cls._from_row(row)
            results.append(obj)
        
        return results
    
    @classmethod
    def find_one(cls, **kwargs) -> Optional['Model']:
        """
        Retorna uma única instância que corresponde aos critérios
        
        Args:
            **kwargs: Pares chave-valor para filtrar
        
        Returns:
            Primeira instância encontrada ou None
        """
        results = cls.filter(**kwargs)
        return results[0] if results else None
    
    @classmethod
    def find_by_id(cls, pk_value: int) -> Optional['Model']:
        """
        Encontra uma instância pelo ID
        
        Args:
            pk_value: Valor da chave primária
        
        Returns:
            Instância encontrada ou None
        """
        if cls._database is None:
            cls._initialize_model()
        
        # Encontra o campo primary key
        pk_field = None
        for field_name, field in cls._fields.items():
            if field.primary_key:
                pk_field = field_name
                break
        
        if pk_field is None:
            raise RuntimeError(f"Modelo {cls.__name__} não tem chave primária definida")
        
        sql = f"SELECT * FROM {cls._table_name} WHERE {pk_field} = ?"
        cursor = cls._database.execute(sql, (pk_value,))
        row = cursor.fetchone()
        
        return cls._from_row(row) if row else None
    
    @classmethod
    def delete_by_id(cls, pk_value: int) -> bool:
        """
        Deleta uma instância pelo ID
        
        Args:
            pk_value: Valor da chave primária
        
        Returns:
            True se deletado com sucesso
        """
        if cls._database is None:
            cls._initialize_model()
        
        # Encontra o campo primary key
        pk_field = None
        for field_name, field in cls._fields.items():
            if field.primary_key:
                pk_field = field_name
                break
        
        if pk_field is None:
            raise RuntimeError(f"Modelo {cls.__name__} não tem chave primária definida")
        
        sql = f"DELETE FROM {cls._table_name} WHERE {pk_field} = ?"
        cursor = cls._database.execute(sql, (pk_value,))
        cls._database.commit()
        
        return cursor.rowcount > 0
    
    def delete(self) -> bool:
        """Deleta a instância atual do banco de dados"""
        # Encontra o valor da chave primária
        pk_value = None
        for field_name, field in self._fields.items():
            if field.primary_key:
                pk_value = getattr(self, field_name, None)
                break
        
        if pk_value is None:
            raise RuntimeError("Não é possível deletar instância sem ID")
        
        return self.__class__.delete_by_id(pk_value)
    
    @classmethod
    def count(cls) -> int:
        """Retorna a quantidade total de registros"""
        if cls._database is None:
            cls._initialize_model()
        
        sql = f"SELECT COUNT(*) as total FROM {cls._table_name}"
        cursor = cls._database.execute(sql)
        row = cursor.fetchone()
        
        return row['total'] if row else 0
    
    @classmethod
    def delete_all(cls) -> int:
        """Deleta todos os registros da tabela"""
        if cls._database is None:
            cls._initialize_model()
        
        sql = f"DELETE FROM {cls._table_name}"
        cursor = cls._database.execute(sql)
        cls._database.commit()
        
        return cursor.rowcount
    
    @classmethod
    def _from_row(cls, row: sqlite3.Row) -> 'Model':
        """Converte uma linha do banco de dados para instância do modelo"""
        data = {}
        
        for field_name, field in cls._fields.items():
            value = row[field_name]
            
            # Converte tipos especiais de volta
            if field.field_type == FieldType.BOOLEAN and value is not None:
                data[field_name] = bool(value)
            elif field.field_type == FieldType.DATETIME and value:
                try:
                    data[field_name] = datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    data[field_name] = value
            else:
                data[field_name] = value
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância para um dicionário"""
        result = {}
        for field_name in self._fields:
            value = getattr(self, field_name, None)
            if isinstance(value, datetime):
                result[field_name] = value.isoformat()
            else:
                result[field_name] = value
        
        return result
    
    def __repr__(self) -> str:
        """
        Representação em string do modelo (melhorada)
        Mostra classe, pk e resumo dos dados principais
        """
        pk_field_name = self._get_pk_field_name()
        pk_value = getattr(self, pk_field_name, None)
        
        # Se for um registro novo (sem ID), mostra como "novo"
        if pk_value is None:
            status = 'novo'
        else:
            status = pk_value
        
        # Mostra também o primeiro campo texto como resumo
        text_fields = [
            field_name for field_name, field in self._fields.items()
            if field.field_type == FieldType.TEXT and field_name != pk_field_name
        ]
        
        if text_fields:
            first_text_field = text_fields[0]
            text_value = getattr(self, first_text_field, None)
            return f"<{self.__class__.__name__} pk={status} {first_text_field}='{text_value}'>"
        else:
            return f"<{self.__class__.__name__} pk={status}>"
