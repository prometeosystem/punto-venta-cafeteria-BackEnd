from repository.producto_repository import (
    crear_producto, ver_todos_productos, ver_producto_by_id,
    editar_producto, eliminar_producto, obtener_imagen_producto
)
from repository.receta_repository import crear_receta, eliminar_todas_recetas_producto
from repository.inventario_repository import crear_insumo
from schemas.producto_schema import ProductoCreate, ProductoUpdate
from schemas.comanda_schema import RecetaInsumoCreate
from schemas.inventario_schema import InsumoCreate
from fastapi import UploadFile
from typing import Optional

def _procesar_recetas(id_producto: int, recetas):
    """Función auxiliar para procesar recetas (crear insumos nuevos si es necesario y crear recetas)"""
    from schemas.producto_schema import RecetaInsumoEnProducto
    
    recetas_creadas = []
    errores = []
    insumos_creados = []
    
    # Convertir diccionarios a objetos RecetaInsumoEnProducto si es necesario
    recetas_objetos = []
    for i, receta in enumerate(recetas):
        print(f"[DEBUG] Procesando receta {i+1}: tipo={type(receta)}, valor={receta}")
        if isinstance(receta, dict):
            # Convertir diccionario a objeto
            try:
                print(f"[DEBUG]   Convirtiendo diccionario a RecetaInsumoEnProducto...")
                receta_obj = RecetaInsumoEnProducto(**receta)
                recetas_objetos.append(receta_obj)
                print(f"[DEBUG]   ✅ Receta convertida: id_insumo={receta_obj.id_insumo}, cantidad={receta_obj.cantidad_necesaria}, unidad={receta_obj.unidad_medida}")
            except Exception as e:
                error_msg = f"Error al procesar receta {i+1}: {str(e)}"
                print(f"[DEBUG]   ❌ {error_msg}")
                errores.append(error_msg)
                continue
        else:
            print(f"[DEBUG]   Receta ya es objeto, agregando directamente")
            recetas_objetos.append(receta)
    
    for receta in recetas_objetos:
        id_insumo = None
        
        # Si se proporciona un insumo nuevo, crearlo primero
        # Solo con datos básicos - valores por defecto para inventario
        if receta.insumo_nuevo:
            from decimal import Decimal
            # El insumo se crea sin unidad de medida (se usa una genérica por defecto)
            insumo_data = InsumoCreate(
                nombre=receta.insumo_nuevo.nombre,
                descripcion=receta.insumo_nuevo.descripcion,
                unidad_medida="unidades",  # Valor por defecto genérico
                cantidad_actual=Decimal('0'),  # Valor por defecto
                cantidad_minima=Decimal('0'),   # Valor por defecto
                precio_compra=Decimal('0'),    # Valor por defecto
                activo=True
            )
            resultado_insumo = crear_insumo(insumo_data)
            
            if "error" in resultado_insumo:
                errores.append(f"Error al crear insumo '{receta.insumo_nuevo.nombre}': {resultado_insumo['error']}")
                continue
            
            id_insumo = resultado_insumo["id_insumo"]
            insumos_creados.append({
                "id_insumo": id_insumo,
                "nombre": receta.insumo_nuevo.nombre
            })
        else:
            # Usar el insumo existente
            id_insumo = receta.id_insumo
        
        # Crear la receta (relación producto-insumo)
        # La unidad_medida va en la receta, no en el insumo
        print(f"[DEBUG] Creando receta: producto={id_producto}, insumo={id_insumo}, cantidad={receta.cantidad_necesaria}, unidad={receta.unidad_medida}")
        receta_data = RecetaInsumoCreate(
            id_producto=id_producto,
            id_insumo=id_insumo,
            cantidad_necesaria=receta.cantidad_necesaria,
            unidad_medida=receta.unidad_medida
        )
        resultado_receta = crear_receta(receta_data)
        
        if "error" in resultado_receta:
            error_msg = f"Error al crear receta para insumo ID {id_insumo}: {resultado_receta['error']}"
            print(f"[DEBUG] ❌ {error_msg}")
            errores.append(error_msg)
        else:
            print(f"[DEBUG] ✅ Receta creada exitosamente: ID {resultado_receta['id_receta']}")
            recetas_creadas.append({
                "id_receta": resultado_receta["id_receta"],
                "id_insumo": id_insumo,
                "cantidad_necesaria": float(receta.cantidad_necesaria)
            })
    
    return {
        "recetas_creadas": recetas_creadas,
        "insumos_creados": insumos_creados,
        "errores": errores
    }

def crear_producto_service(producto: ProductoCreate, imagen: Optional[UploadFile] = None):
    # Procesar imagen si existe
    imagen_bytes = None
    tipo_imagen = None
    
    if imagen:
        # Validar tipo de archivo
        contenido_tipo = imagen.content_type
        if contenido_tipo not in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']:
            return {"error": "Formato de imagen no permitido. Use: JPEG, PNG o WebP"}
        
        # Leer bytes de la imagen
        try:
            imagen_bytes = imagen.file.read()
            # Validar tamaño (max 5MB)
            if len(imagen_bytes) > 5 * 1024 * 1024:
                return {"error": "La imagen es demasiado grande. Máximo 5MB"}
            
            # Determinar tipo de imagen
            if contenido_tipo in ['image/jpeg', 'image/jpg']:
                tipo_imagen = 'image/jpeg'
            elif contenido_tipo == 'image/png':
                tipo_imagen = 'image/png'
            elif contenido_tipo == 'image/webp':
                tipo_imagen = 'image/webp'
        except Exception as e:
            return {"error": f"Error al leer la imagen: {str(e)}"}
    
    # Crear el producto (sin recetas)
    producto_sin_recetas = ProductoCreate(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria=producto.categoria,
        activo=producto.activo,
        recetas=None
    )
    
    resultado_producto = crear_producto(producto_sin_recetas, imagen_bytes, tipo_imagen)
    
    # Si hay error al crear el producto, retornar el error
    if "error" in resultado_producto:
        return resultado_producto
    
    id_producto = resultado_producto["id_producto"]
    
    # Si hay recetas (insumos) para relacionar
    if producto.recetas:
        resultado_recetas = _procesar_recetas(id_producto, producto.recetas)
        
        # Agregar información de recetas al resultado
        resultado_producto["recetas_creadas"] = len(resultado_recetas["recetas_creadas"])
        resultado_producto["insumos_creados"] = len(resultado_recetas["insumos_creados"])
        resultado_producto["recetas"] = resultado_recetas["recetas_creadas"]
        resultado_producto["insumos_nuevos"] = resultado_recetas["insumos_creados"]
        
        if resultado_recetas["errores"]:
            resultado_producto["errores_recetas"] = resultado_recetas["errores"]
            resultado_producto["advertencia"] = "Producto creado pero algunos insumos/recetas tuvieron errores"
    
    return resultado_producto

def ver_todos_productos_service():
    return ver_todos_productos()

def ver_producto_by_id_service(id_producto: int):
    """Obtiene un producto por ID e incluye sus recetas"""
    producto = ver_producto_by_id(id_producto)
    
    # Si hay error, retornarlo
    if "error" in producto:
        return producto
    
    # Obtener recetas del producto
    from repository.receta_repository import ver_recetas_por_producto
    recetas = ver_recetas_por_producto(id_producto)
    
    # Agregar recetas al producto
    if isinstance(recetas, list):
        producto["recetas"] = recetas
    else:
        producto["recetas"] = []
    
    return producto

def editar_producto_service(id_producto: int, producto: ProductoUpdate, imagen: Optional[UploadFile] = None, eliminar_imagen: bool = False):
    # Procesar imagen si existe
    imagen_bytes = None
    tipo_imagen = None
    
    if imagen:
        # Validar tipo de archivo
        contenido_tipo = imagen.content_type
        if contenido_tipo not in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']:
            return {"error": "Formato de imagen no permitido. Use: JPEG, PNG o WebP"}
        
        # Leer bytes de la imagen
        try:
            imagen_bytes = imagen.file.read()
            # Validar tamaño (max 5MB)
            if len(imagen_bytes) > 5 * 1024 * 1024:
                return {"error": "La imagen es demasiado grande. Máximo 5MB"}
            
            # Determinar tipo de imagen
            if contenido_tipo in ['image/jpeg', 'image/jpg']:
                tipo_imagen = 'image/jpeg'
            elif contenido_tipo == 'image/png':
                tipo_imagen = 'image/png'
            elif contenido_tipo == 'image/webp':
                tipo_imagen = 'image/webp'
        except Exception as e:
            return {"error": f"Error al leer la imagen: {str(e)}"}
    
    # Si se proporcionan recetas, primero eliminar las existentes y luego crear las nuevas
    if producto.recetas is not None:
        # Debug: verificar qué recetas se recibieron
        print(f"[DEBUG SERVICE] Editar producto {id_producto}: Recibidas {len(producto.recetas)} recetas")
        for i, receta in enumerate(producto.recetas):
            print(f"[DEBUG SERVICE] Receta {i+1}: {receta}")
        
        # Eliminar todas las recetas existentes del producto
        resultado_eliminacion = eliminar_todas_recetas_producto(id_producto)
        print(f"[DEBUG SERVICE] Recetas eliminadas: {resultado_eliminacion}")
    else:
        print(f"[DEBUG SERVICE] ⚠️ producto.recetas es None - no se tocarán las recetas existentes")
    
    # Actualizar el producto (sin recetas en el update)
    producto_sin_recetas = ProductoUpdate(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria=producto.categoria,
        activo=producto.activo,
        recetas=None
    )
    
    resultado_producto = editar_producto(id_producto, producto_sin_recetas, imagen_bytes, tipo_imagen, eliminar_imagen)
    
    # Si hay error al actualizar el producto, retornar el error
    if "error" in resultado_producto:
        return resultado_producto
    
    # Si se proporcionaron recetas, procesarlas
    if producto.recetas is not None:
        if len(producto.recetas) > 0:
            print(f"[DEBUG] Procesando {len(producto.recetas)} recetas...")
            resultado_recetas = _procesar_recetas(id_producto, producto.recetas)
            
            print(f"[DEBUG] Resultado procesamiento:")
            print(f"[DEBUG]   - Recetas creadas: {len(resultado_recetas['recetas_creadas'])}")
            print(f"[DEBUG]   - Insumos creados: {len(resultado_recetas['insumos_creados'])}")
            print(f"[DEBUG]   - Errores: {len(resultado_recetas['errores'])}")
            if resultado_recetas['errores']:
                print(f"[DEBUG]   - Detalle errores: {resultado_recetas['errores']}")
            
            # Agregar información de recetas al resultado
            resultado_producto["recetas_actualizadas"] = len(resultado_recetas["recetas_creadas"])
            resultado_producto["insumos_creados"] = len(resultado_recetas["insumos_creados"])
            resultado_producto["recetas"] = resultado_recetas["recetas_creadas"]
            resultado_producto["insumos_nuevos"] = resultado_recetas["insumos_creados"]
            
            # ⚠️ IMPORTANTE: Si no se crearon recetas, verificar por qué
            if len(resultado_recetas["recetas_creadas"]) == 0:
                if resultado_recetas["errores"]:
                    resultado_producto["error"] = "No se pudieron crear las recetas. Verifique los errores."
                    resultado_producto["errores"] = resultado_recetas["errores"]
                    print(f"[DEBUG] ❌ ERROR: No se crearon recetas. Errores: {resultado_recetas['errores']}")
                    return resultado_producto
                else:
                    resultado_producto["advertencia"] = "No se crearon recetas. Verifique los logs del servidor."
                    print(f"[DEBUG] ⚠️ ADVERTENCIA: No se crearon recetas pero no hay errores registrados")
            elif resultado_recetas["errores"]:
                resultado_producto["errores_recetas"] = resultado_recetas["errores"]
                resultado_producto["advertencia"] = "Producto actualizado pero algunos insumos/recetas tuvieron errores"
        else:
            # Si se envía una lista vacía, solo se eliminaron las recetas
            print(f"[DEBUG] Lista de recetas vacía - solo se eliminaron recetas existentes")
            resultado_producto["recetas_actualizadas"] = 0
            resultado_producto["mensaje"] = "Producto actualizado y todas las recetas eliminadas"
    
    return resultado_producto

def eliminar_producto_service(id_producto: int):
    return eliminar_producto(id_producto)

def obtener_imagen_producto_service(id_producto: int):
    """Obtiene la imagen de un producto desde la base de datos"""
    return obtener_imagen_producto(id_producto)

