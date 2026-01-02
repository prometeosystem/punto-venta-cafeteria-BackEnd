from repository.producto_repository import (
    crear_producto, ver_todos_productos, ver_producto_by_id,
    editar_producto, eliminar_producto
)
from repository.receta_repository import crear_receta, eliminar_todas_recetas_producto
from repository.inventario_repository import crear_insumo
from schemas.producto_schema import ProductoCreate, ProductoUpdate
from schemas.comanda_schema import RecetaInsumoCreate
from schemas.inventario_schema import InsumoCreate

def _procesar_recetas(id_producto: int, recetas):
    """Función auxiliar para procesar recetas (crear insumos nuevos si es necesario y crear recetas)"""
    recetas_creadas = []
    errores = []
    insumos_creados = []
    
    for receta in recetas:
        id_insumo = None
        
        # Si se proporciona un insumo nuevo, crearlo primero
        if receta.insumo_nuevo:
            insumo_data = InsumoCreate(
                nombre=receta.insumo_nuevo.nombre,
                descripcion=receta.insumo_nuevo.descripcion,
                unidad_medida=receta.insumo_nuevo.unidad_medida,
                cantidad_actual=receta.insumo_nuevo.cantidad_actual,
                cantidad_minima=receta.insumo_nuevo.cantidad_minima,
                precio_compra=receta.insumo_nuevo.precio_compra,
                activo=receta.insumo_nuevo.activo
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
        receta_data = RecetaInsumoCreate(
            id_producto=id_producto,
            id_insumo=id_insumo,
            cantidad_necesaria=receta.cantidad_necesaria
        )
        resultado_receta = crear_receta(receta_data)
        
        if "error" in resultado_receta:
            errores.append(f"Error al crear receta para insumo ID {id_insumo}: {resultado_receta['error']}")
        else:
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

def crear_producto_service(producto: ProductoCreate):
    # Primero crear el producto (sin recetas)
    producto_sin_recetas = ProductoCreate(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria=producto.categoria,
        activo=producto.activo,
        recetas=None
    )
    
    resultado_producto = crear_producto(producto_sin_recetas)
    
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
    return ver_producto_by_id(id_producto)

def editar_producto_service(id_producto: int, producto: ProductoUpdate):
    # Si se proporcionan recetas, primero eliminar las existentes y luego crear las nuevas
    if producto.recetas is not None:
        # Eliminar todas las recetas existentes del producto
        eliminar_todas_recetas_producto(id_producto)
    
    # Actualizar el producto (sin recetas en el update)
    producto_sin_recetas = ProductoUpdate(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        categoria=producto.categoria,
        activo=producto.activo,
        recetas=None
    )
    
    resultado_producto = editar_producto(id_producto, producto_sin_recetas)
    
    # Si hay error al actualizar el producto, retornar el error
    if "error" in resultado_producto:
        return resultado_producto
    
    # Si se proporcionaron recetas, procesarlas
    if producto.recetas is not None:
        if len(producto.recetas) > 0:
            resultado_recetas = _procesar_recetas(id_producto, producto.recetas)
            
            # Agregar información de recetas al resultado
            resultado_producto["recetas_actualizadas"] = len(resultado_recetas["recetas_creadas"])
            resultado_producto["insumos_creados"] = len(resultado_recetas["insumos_creados"])
            resultado_producto["recetas"] = resultado_recetas["recetas_creadas"]
            resultado_producto["insumos_nuevos"] = resultado_recetas["insumos_creados"]
            
            if resultado_recetas["errores"]:
                resultado_producto["errores_recetas"] = resultado_recetas["errores"]
                resultado_producto["advertencia"] = "Producto actualizado pero algunos insumos/recetas tuvieron errores"
        else:
            # Si se envía una lista vacía, solo se eliminaron las recetas
            resultado_producto["recetas_actualizadas"] = 0
            resultado_producto["mensaje"] = "Producto actualizado y todas las recetas eliminadas"
    
    return resultado_producto

def eliminar_producto_service(id_producto: int):
    return eliminar_producto(id_producto)

