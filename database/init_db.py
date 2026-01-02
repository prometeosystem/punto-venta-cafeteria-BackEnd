import os
import re
from database.conexion import conectar

def column_exists(cursor, table_name: str, column_name: str) -> bool:
    """
    Verifica si una columna existe en una tabla
    """
    try:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0
    except Exception:
        return False

def index_exists(cursor, table_name: str, index_name: str) -> bool:
    """
    Verifica si un índice existe en una tabla
    """
    try:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}' 
            AND INDEX_NAME = '{index_name}'
        """)
        result = cursor.fetchone()
        return result[0] > 0
    except Exception:
        return False

def apply_migrations(cursor):
    """
    Aplica las migraciones (agrega campos faltantes) si las tablas ya existen
    Similar a spring.jpa.hibernate.ddl-auto=update
    """
    migrations_applied = 0
    
    # Migración 1: Agregar campo 'user' a usuarios
    if not column_exists(cursor, 'usuarios', 'user'):
        try:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN user VARCHAR(100) UNIQUE AFTER correo
            """)
            print("  ✓ Agregado campo 'user' a tabla usuarios")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'user': {e}")
    
    # Migración 2: Agregar campos de Loyabit a clientes
    if not column_exists(cursor, 'clientes', 'loyabit_id'):
        try:
            cursor.execute("""
                ALTER TABLE clientes 
                ADD COLUMN loyabit_id VARCHAR(255) NULL AFTER puntos
            """)
            print("  ✓ Agregado campo 'loyabit_id' a tabla clientes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'loyabit_id': {e}")
    
    if not column_exists(cursor, 'clientes', 'loyabit_sincronizado'):
        try:
            cursor.execute("""
                ALTER TABLE clientes 
                ADD COLUMN loyabit_sincronizado BOOLEAN DEFAULT FALSE AFTER loyabit_id
            """)
            print("  ✓ Agregado campo 'loyabit_sincronizado' a tabla clientes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'loyabit_sincronizado': {e}")
    
    if not index_exists(cursor, 'clientes', 'idx_loyabit_id'):
        try:
            cursor.execute("""
                ALTER TABLE clientes 
                ADD INDEX idx_loyabit_id (loyabit_id)
            """)
            print("  ✓ Agregado índice 'idx_loyabit_id' a tabla clientes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar índice 'idx_loyabit_id': {e}")
    
    # Migración 3: Agregar tiempo_preparacion a productos
    if not column_exists(cursor, 'productos', 'tiempo_preparacion'):
        try:
            cursor.execute("""
                ALTER TABLE productos 
                ADD COLUMN tiempo_preparacion INT AFTER categoria
            """)
            print("  ✓ Agregado campo 'tiempo_preparacion' a tabla productos")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'tiempo_preparacion': {e}")
    
    # Migración 4: Agregar nombre_normalizado a insumos
    if not column_exists(cursor, 'insumos', 'nombre_normalizado'):
        try:
            cursor.execute("""
                ALTER TABLE insumos 
                ADD COLUMN nombre_normalizado VARCHAR(255) AFTER nombre
            """)
            print("  ✓ Agregado campo 'nombre_normalizado' a tabla insumos")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'nombre_normalizado': {e}")
    
    if not index_exists(cursor, 'insumos', 'unique_nombre_normalizado'):
        try:
            cursor.execute("""
                ALTER TABLE insumos 
                ADD UNIQUE INDEX unique_nombre_normalizado (nombre_normalizado)
            """)
            print("  ✓ Agregado índice único 'unique_nombre_normalizado' a tabla insumos")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar índice 'unique_nombre_normalizado': {e}")
    
    # Migración 5: Agregar campos del modal de checkout a preordenes
    if not column_exists(cursor, 'preordenes', 'tipo_servicio'):
        try:
            cursor.execute("""
                ALTER TABLE preordenes 
                ADD COLUMN tipo_servicio VARCHAR(20) NULL COMMENT 'comer-aqui o para-llevar'
            """)
            print("  ✓ Agregado campo 'tipo_servicio' a tabla preordenes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'tipo_servicio': {e}")
    
    if not column_exists(cursor, 'preordenes', 'comentarios'):
        try:
            cursor.execute("""
                ALTER TABLE preordenes 
                ADD COLUMN comentarios TEXT NULL COMMENT 'Comentarios generales del pedido'
            """)
            print("  ✓ Agregado campo 'comentarios' a tabla preordenes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'comentarios': {e}")
    
    if not column_exists(cursor, 'preordenes', 'tipo_leche'):
        try:
            cursor.execute("""
                ALTER TABLE preordenes 
                ADD COLUMN tipo_leche VARCHAR(20) NULL COMMENT 'entera o deslactosada'
            """)
            print("  ✓ Agregado campo 'tipo_leche' a tabla preordenes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'tipo_leche': {e}")
    
    if not column_exists(cursor, 'preordenes', 'extra_leche'):
        try:
            cursor.execute("""
                ALTER TABLE preordenes 
                ADD COLUMN extra_leche DECIMAL(10,2) DEFAULT 0 COMMENT 'Monto extra por leche deslactosada'
            """)
            print("  ✓ Agregado campo 'extra_leche' a tabla preordenes")
            migrations_applied += 1
        except Exception as e:
            print(f"  ⚠️  Error al agregar campo 'extra_leche': {e}")
    
    return migrations_applied

def execute_sql_statements(cursor, sql_script: str):
    """
    Ejecuta múltiples statements SQL, manejando errores de forma inteligente
    """
    # Remover comentarios de una línea que empiezan con --
    sql_script = re.sub(r'--.*$', '', sql_script, flags=re.MULTILINE)
    
    # Dividir por punto y coma, pero no dentro de strings
    statements = []
    current_statement = ""
    in_string = False
    string_char = None
    
    for char in sql_script:
        if char in ("'", '"', '`') and (not current_statement or current_statement[-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        current_statement += char
        
        if not in_string and char == ';':
            stmt = current_statement.strip()
            if stmt and len(stmt) > 1:  # Ignorar solo ";"
                statements.append(stmt)
            current_statement = ""
    
    # Agregar el último statement si no termina en ;
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    executed = 0
    for statement in statements:
        statement = statement.strip()
        if not statement or statement.startswith('--'):
            continue
        
        try:
            cursor.execute(statement)
            executed += 1
        except Exception as e:
            error_msg = str(e).lower()
            # Ignorar errores de "ya existe" (tablas, índices, columnas)
            if any(keyword in error_msg for keyword in [
                'already exists', 'duplicate', 'exist', 'defined', 'duplicate key name'
            ]):
                pass  # Ignorar silenciosamente - es normal si ya existe
            else:
                # Mostrar otros errores como advertencias
                print(f"  ⚠️  Advertencia: {str(e)[:100]}")
    
    return executed

def init_database():
    """
    Inicializa la base de datos ejecutando el schema.sql
    Similar a spring.jpa.hibernate.ddl-auto=create/update en Spring Boot
    
    - Si las tablas no existen, las crea desde schema.sql
    - Si las tablas ya existen, aplica migraciones para agregar campos faltantes
    """
    try:
        conexion = conectar()
        if conexion is None:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conexion.cursor()
        
        # Verificar si TODAS las tablas principales ya existen
        tablas_requeridas = ['usuarios', 'clientes', 'productos', 'insumos', 'ventas', 
                            'detalles_venta', 'comandas', 'detalles_comanda', 
                            'recetas_insumos', 'movimientos_inventario', 
                            'visitas_clientes', 'preordenes', 'detalles_preorden']
        
        cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME IN ({','.join([f"'{t}'" for t in tablas_requeridas])})
        """)
        tablas_existentes = [row[0] for row in cursor.fetchall()]
        tablas_faltantes = [t for t in tablas_requeridas if t not in tablas_existentes]
        
        if tablas_faltantes:
            # Faltan tablas: crear/actualizar desde schema.sql
            print(f"📦 Detectadas tablas faltantes: {', '.join(tablas_faltantes)}")
            print("📦 Ejecutando schema.sql para crear/actualizar tablas...")
            
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            
            if not os.path.exists(schema_path):
                print(f"❌ No se encontró el archivo schema.sql en {schema_path}")
                cursor.close()
                conexion.close()
                return False
            
            with open(schema_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            executed = execute_sql_statements(cursor, sql_script)
            conexion.commit()
            
            print(f"✅ Schema ejecutado: {executed} statements")
            
            # Después de crear tablas, aplicar migraciones por si faltan campos
            print("🔄 Verificando migraciones adicionales...")
            migrations_applied = apply_migrations(cursor)
            conexion.commit()
            
            if migrations_applied > 0:
                print(f"✅ Migraciones aplicadas: {migrations_applied} cambios adicionales")
            else:
                print("✅ Todas las tablas y campos están actualizados")
        else:
            # Todas las tablas existen: solo aplicar migraciones de campos
            print("🔄 Todas las tablas existen: verificando campos faltantes...")
            migrations_applied = apply_migrations(cursor)
            conexion.commit()
            
            if migrations_applied > 0:
                print(f"✅ Migraciones aplicadas: {migrations_applied} cambios")
            else:
                print("✅ Base de datos ya está actualizada")
        
        cursor.close()
        conexion.close()
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return False

