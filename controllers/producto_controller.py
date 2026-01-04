from fastapi import APIRouter, Depends, File, UploadFile, Form, Response
from schemas.producto_schema import ProductoCreate, ProductoUpdate
from services.producto_service import (
    crear_producto_service,
    ver_todos_productos_service,
    ver_producto_by_id_service,
    editar_producto_service,
    eliminar_producto_service,
    obtener_imagen_producto_service
)
from utils.auth import require_role, get_current_user
from typing import Optional
from decimal import Decimal
import json

router = APIRouter()

@router.post("/crear_producto")
async def crear_producto(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: str = Form(...),
    categoria: str = Form(...),
    activo: bool = Form(True),
    recetas: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Crear un nuevo producto con opción de imagen"""
    # Parsear recetas si vienen
    recetas_list = None
    if recetas:
        try:
            recetas_parsed = json.loads(recetas)
            # Convertir diccionarios a objetos RecetaInsumoEnProducto
            from schemas.producto_schema import RecetaInsumoEnProducto
            recetas_objetos = []
            for receta_dict in recetas_parsed:
                try:
                    receta_obj = RecetaInsumoEnProducto(**receta_dict)
                    recetas_objetos.append(receta_obj)
                except Exception as e:
                    return {"error": f"Error en formato de receta: {str(e)}"}
            recetas_list = recetas_objetos
        except json.JSONDecodeError:
            return {"error": "Formato de recetas inválido (JSON mal formado)"}
        except Exception as e:
            return {"error": f"Error al procesar recetas: {str(e)}"}
    
    producto_data = ProductoCreate(
        nombre=nombre,
        descripcion=descripcion,
        precio=Decimal(precio),
        categoria=categoria,
        activo=activo,
        recetas=recetas_list
    )
    
    return await crear_producto_service(producto_data, imagen)

@router.get("/ver_productos", summary="Listar productos (PÚBLICO)")
async def listar_productos():
    """
    **ENDPOINT PÚBLICO** - Listar todos los productos activos.
    
    No requiere autenticación. Usado por la página web para mostrar el menú.
    """
    return ver_todos_productos_service()

@router.get("/ver_producto/{id_producto}")
async def ver_producto_by_id(
    id_producto: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver un producto específico"""
    return ver_producto_by_id_service(id_producto)

@router.put("/editar_producto/{id_producto}")
async def editar_producto(
    id_producto: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    activo: Optional[bool] = Form(None),
    recetas: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    eliminar_imagen: bool = Form(False),
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Editar un producto con opción de actualizar imagen"""
    # Construir objeto de actualización
    update_data = {}
    if nombre is not None:
        update_data["nombre"] = nombre
    if descripcion is not None:
        update_data["descripcion"] = descripcion
    if precio is not None:
        update_data["precio"] = Decimal(precio)
    if categoria is not None:
        update_data["categoria"] = categoria
    if activo is not None:
        # Convertir activo a boolean si viene como string o número
        if isinstance(activo, str):
            update_data["activo"] = activo.lower() in ['true', '1', 'yes', 'on']
        elif isinstance(activo, (int, float)):
            update_data["activo"] = bool(activo)
        else:
            update_data["activo"] = bool(activo)
    
    # Parsear recetas
    # IMPORTANTE: Si recetas es None, NO se tocan las recetas existentes
    # Solo se actualizan si se envía explícitamente (array vacío o con elementos)
    if recetas is not None:
        try:
            print(f"[DEBUG CONTROLLER] Recetas recibidas (tipo: {type(recetas)}, valor: {recetas})")
            if recetas and recetas.strip():  # Verificar que no esté vacío
                recetas_parsed = json.loads(recetas)
                print(f"[DEBUG CONTROLLER] Recetas parseadas: {recetas_parsed}")
                # Convertir diccionarios a objetos RecetaInsumoEnProducto
                from schemas.producto_schema import RecetaInsumoEnProducto
                recetas_objetos = []
                for i, receta_dict in enumerate(recetas_parsed):
                    try:
                        print(f"[DEBUG CONTROLLER] Procesando receta {i+1}: {receta_dict}")
                        # Convertir cantidad_necesaria a Decimal si viene como float o string
                        if 'cantidad_necesaria' in receta_dict:
                            if isinstance(receta_dict['cantidad_necesaria'], (int, float)):
                                receta_dict['cantidad_necesaria'] = Decimal(str(receta_dict['cantidad_necesaria']))
                            elif isinstance(receta_dict['cantidad_necesaria'], str):
                                receta_dict['cantidad_necesaria'] = Decimal(receta_dict['cantidad_necesaria'])
                        receta_obj = RecetaInsumoEnProducto(**receta_dict)
                        recetas_objetos.append(receta_obj)
                        print(f"[DEBUG CONTROLLER] ✅ Receta {i+1} convertida correctamente")
                    except Exception as e:
                        import traceback
                        error_msg = f"Error en formato de receta {i+1}: {str(e)}"
                        print(f"[DEBUG CONTROLLER] ❌ {error_msg}")
                        print(f"[DEBUG CONTROLLER] Traceback: {traceback.format_exc()}")
                        return {"error": error_msg}
                update_data["recetas"] = recetas_objetos
                print(f"[DEBUG CONTROLLER] Total recetas procesadas: {len(recetas_objetos)}")
            else:
                # String vacío o "[]" - se eliminarán todas las recetas
                print(f"[DEBUG CONTROLLER] Recetas vacías - se eliminarán todas")
                update_data["recetas"] = []
        except json.JSONDecodeError as e:
            error_msg = f"Formato de recetas inválido (JSON mal formado): {str(e)}"
            print(f"[DEBUG CONTROLLER] ❌ {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error al procesar recetas: {str(e)}"
            print(f"[DEBUG CONTROLLER] ❌ {error_msg}")
            return {"error": error_msg}
    # Si recetas es None, no se agrega al update_data, por lo que no se tocan las recetas existentes
    
    producto_update = ProductoUpdate(**update_data)
    
    return await editar_producto_service(id_producto, producto_update, imagen, eliminar_imagen)

@router.delete("/eliminar_producto/{id_producto}")
async def eliminar_producto(
    id_producto: int,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Eliminar (desactivar) un producto"""
    return eliminar_producto_service(id_producto)

@router.get("/imagen/{id_producto}")
async def obtener_imagen_producto(
    id_producto: int
):
    """
    Obtener la imagen de un producto desde la base de datos.
    Endpoint público para servir imágenes.
    """
    resultado = obtener_imagen_producto_service(id_producto)
    
    if "error" in resultado:
        return Response(
            status_code=404,
            content="Imagen no encontrada"
        )
    
    return Response(
        content=resultado["imagen"],
        media_type=resultado["tipo_imagen"]
    )

