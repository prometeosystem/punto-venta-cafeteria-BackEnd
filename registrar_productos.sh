#!/bin/bash

# Script para registrar productos en la base de datos
# IMPORTANTE: Primero necesitas hacer login y obtener el token
# Reemplaza TOKEN_AQUI con el token obtenido del login

# Variables
BASE_URL="http://localhost:8000"
# TOKEN="TU_TOKEN_AQUI"  # Descomenta y reemplaza después de hacer login

# Función para crear producto
crear_producto() {
    local nombre="$1"
    local descripcion="$2"
    local precio="$3"
    local categoria="$4"
    
    curl -X POST "${BASE_URL}/api/productos/crear_producto" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${TOKEN}" \
        -d "{
            \"nombre\": \"${nombre}\",
            \"descripcion\": \"${descripcion}\",
            \"precio\": ${precio},
            \"categoria\": \"${categoria}\",
            \"activo\": true
        }"
    echo ""
    echo "---"
}

# ============================================
# PASO 1: Hacer login primero
# ============================================
# Ejecuta este comando primero para obtener el token:
# curl -X POST "http://localhost:8000/api/login" \
#     -H "Content-Type: application/json" \
#     -d '{"correo": "tu_correo@ejemplo.com", "contrasena": "tu_contraseña"}'
#
# Copia el "access_token" de la respuesta y reemplaza TOKEN_AQUI arriba
# ============================================

# Verificar que el token esté configurado
if [ -z "$TOKEN" ]; then
    echo "ERROR: Debes configurar la variable TOKEN primero"
    echo "1. Ejecuta el comando de login mostrado arriba"
    echo "2. Copia el access_token de la respuesta"
    echo "3. Edita este script y reemplaza TOKEN_AQUI con tu token"
    exit 1
fi

echo "Registrando productos..."
echo ""

# ============================================
# BEBIDAS CALIENTES
# ============================================
echo "Registrando Bebidas Calientes..."

# Americano
crear_producto "Americano M" "Pa' empezar el día." "40.00" "Bebidas Calientes"
crear_producto "Americano G" "Pa' empezar el día." "45.00" "Bebidas Calientes"

# Capuchino
crear_producto "Capuchino M" "Expresso sencillo con leche espumada." "55.00" "Bebidas Calientes"
crear_producto "Capuchino G" "Expresso sencillo con leche espumada." "60.00" "Bebidas Calientes"

# Energy Latte
crear_producto "Energy Latte M" "Expresso doble con leche cremosa." "60.00" "Bebidas Calientes"
crear_producto "Energy Latte G" "Expresso doble con leche cremosa." "65.00" "Bebidas Calientes"

# Coco Yuki Latte
crear_producto "Coco Yuki Latte M" "Expresso doble con toque sabor coco y leche cremosa." "65.00" "Bebidas Calientes"
crear_producto "Coco Yuki Latte G" "Expresso doble con toque sabor coco y leche cremosa." "69.00" "Bebidas Calientes"

# Chai ó Matcha
crear_producto "Chai ó Matcha M" "Tés con leche cremosa." "60.00" "Bebidas Calientes"
crear_producto "Chai ó Matcha G" "Tés con leche cremosa." "65.00" "Bebidas Calientes"

# Chai Sucio
crear_producto "Chai Sucio M" "Té especiado con expresso café y leche cremosa." "65.00" "Bebidas Calientes"
crear_producto "Chai Sucio G" "Té especiado con expresso café y leche cremosa." "70.00" "Bebidas Calientes"

# Muka Rush
crear_producto "Muka Rush M" "Expresso con chocolate y leche cremosa." "65.00" "Bebidas Calientes"
crear_producto "Muka Rush G" "Expresso con chocolate y leche cremosa." "70.00" "Bebidas Calientes"

# Chocolate Dark Finish
crear_producto "Chocolate Dark Finish M" "Chocolate de tu elección con leche cremosa." "65.00" "Bebidas Calientes"
crear_producto "Chocolate Dark Finish G" "Chocolate de tu elección con leche cremosa." "70.00" "Bebidas Calientes"

# Caramel | Irlandés
crear_producto "Caramel | Irlandés M" "Expresso acompañado del sabor a elección y leche cremosa." "65.00" "Bebidas Calientes"
crear_producto "Caramel | Irlandés G" "Expresso acompañado del sabor a elección y leche cremosa." "70.00" "Bebidas Calientes"

# ============================================
# BEBIDAS FRÍAS
# ============================================
echo "Registrando Bebidas Frías..."

# Affogato
crear_producto "Affogato" "Bola de helado acompañada de expresso doble." "65.00" "Bebidas Frías"

# Iced americano
crear_producto "Iced Americano M" "Elige tu americano helado o frapeado." "50.00" "Bebidas Frías"
crear_producto "Iced Americano G" "Elige tu americano helado o frapeado." "55.00" "Bebidas Frías"

# Iced Latte
crear_producto "Iced Latte M" "Elige tu latte helado o frapeado." "55.00" "Bebidas Frías"
crear_producto "Iced Latte G" "Elige tu latte helado o frapeado." "60.00" "Bebidas Frías"

# Expresso Honey
crear_producto "Expresso Honey M" "Expresso doble + miel + agua tónica" "55.00" "Bebidas Frías"
crear_producto "Expresso Honey G" "Expresso doble + miel + agua tónica" "60.00" "Bebidas Frías"

# Expresso Tonic
crear_producto "Expresso Tonic M" "Expresso doble + agua tónica" "50.00" "Bebidas Frías"
crear_producto "Expresso Tonic G" "Expresso doble + agua tónica" "55.00" "Bebidas Frías"

# Orange Coffee
crear_producto "Orange Coffee M" "Expresso doble + jugo de naranja + agua tónica" "65.00" "Bebidas Frías"
crear_producto "Orange Coffee G" "Expresso doble + jugo de naranja + agua tónica" "70.00" "Bebidas Frías"

# Coco Yuki Latte (frío)
crear_producto "Coco Yuki Latte Frío M" "Elígelo helado o frapeado" "70.00" "Bebidas Frías"
crear_producto "Coco Yuki Latte Frío G" "Elígelo helado o frapeado" "75.00" "Bebidas Frías"

# Chai ó Matcha (frío)
crear_producto "Chai ó Matcha Frío M" "Elígelo helado o frapeado" "70.00" "Bebidas Frías"
crear_producto "Chai ó Matcha Frío G" "Elígelo helado o frapeado" "75.00" "Bebidas Frías"

# Moka Rush (frío)
crear_producto "Moka Rush Frío M" "Expresso con chocolate helado o frapeado" "65.00" "Bebidas Frías"
crear_producto "Moka Rush Frío G" "Expresso con chocolate helado o frapeado" "70.00" "Bebidas Frías"

# Chocolate Dark Finish (frío)
crear_producto "Chocolate Dark Finish Frío M" "Chocolate de tu gusto helado o frapeado" "60.00" "Bebidas Frías"
crear_producto "Chocolate Dark Finish Frío G" "Chocolate de tu gusto helado o frapeado" "65.00" "Bebidas Frías"

# Caramel | Irlandés | Pistache | Taro
crear_producto "Caramel | Irlandés | Pistache | Taro M" "Elígelo helado o frapeado" "70.00" "Bebidas Frías"
crear_producto "Caramel | Irlandés | Pistache | Taro G" "Elígelo helado o frapeado" "75.00" "Bebidas Frías"

# Smoothie de Mango ó Fresa
crear_producto "Smoothie de Mango ó Fresa M" "Frappé base agua ó leche de tu fruta favorita" "70.00" "Bebidas Frías"
crear_producto "Smoothie de Mango ó Fresa G" "Frappé base agua ó leche de tu fruta favorita" "75.00" "Bebidas Frías"

# ============================================
# BEBIDAS FITNESS - ENTRENAMIENTO
# ============================================
echo "Registrando Bebidas Fitness - Entrenamiento..."

# Sprint shot
crear_producto "Sprint shot" "Un expresso doble de energía para activar tu entrenamiento." "40.00" "Bebidas Fitness"

# Peak point macchiato
crear_producto "Peak point macchiato" "Expresso doble con un toque de espuma de leche, un boost suave pero decidido." "45.00" "Bebidas Fitness"

# Flat White Run
crear_producto "Flat White Run" "Expresso doble con leche cremosa, ideal para enfoque sostenido." "55.00" "Bebidas Fitness"

# Long Run Americano
crear_producto "Long Run Americano" "Ligero y limpio para resistencia prolongada." "50.00" "Bebidas Fitness"

# Energy Latte (fitness)
crear_producto "Energy Latte Fitness" "Clásico expresso doble con leche para recuperar energía." "65.00" "Bebidas Fitness"

# ============================================
# BEBIDAS FITNESS - CON PROTEÍNA/CREATINA
# ============================================
echo "Registrando Bebidas Fitness - Con Proteína/Creatina..."

# Recovery Dúo Fruit
crear_producto "Recovery Dúo Fruit" "Bebida base leche + plátano + fresas + scoop" "65.00" "Bebidas Fitness"

# Power Boost Latte
crear_producto "Power Boost Latte" "Bebida base leche + café + scoop" "65.00" "Bebidas Fitness"

# Muscle Peanut
crear_producto "Muscle Peanut" "Bebida base leche + crema de cacahuate + plátano + scoop" "70.00" "Bebidas Fitness"

# Mango Marathon
crear_producto "Mango Marathon" "Bebida base leche + mango + miel + yogurt griego + scoop" "75.00" "Bebidas Fitness"

# Speed Up Red
crear_producto "Speed Up Red" "Bebida base yogurt griego + frutos rojos + avena + scoop" "78.00" "Bebidas Fitness"

# Zona Pro Matcha
crear_producto "Zona Pro Matcha" "Bebida base leche + matcha + miel + fresas + scoop" "80.00" "Bebidas Fitness"

# Core Blue
crear_producto "Core Blue" "Bebida base leche + moras + plátano + espirulina azul + scoop" "80.00" "Bebidas Fitness"

# Antioxidant Fruit
crear_producto "Antioxidant Fruit" "Agua de coco + espirulina azul + fresas + avena + scoop" "85.00" "Bebidas Fitness"

# Runner Brew
crear_producto "Runner Brew" "Bebida base yogurt griego + mango + miel + matcha + scoop" "88.00" "Bebidas Fitness"

# ============================================
# MENÚ DULCE
# ============================================
echo "Registrando Menú Dulce..."

# Yogur Bloom
crear_producto "Yogur Bloom" "Yogurt griego + granola + miel + fruta de temporada" "98.00" "Menú Dulce"

# Pan de temporada
crear_producto "Pan de temporada" "Pregunta por disponibilidad del pan recién horneado" "75.00" "Menú Dulce"

# Chocobanana Sando
crear_producto "Chocobanana Sando" "Chocolate y plátano" "67.00" "Menú Dulce"

# Fruit Sando
crear_producto "Fruit Sando" "Fresas, durazno y kiwi" "89.00" "Menú Dulce"

# Ichigo Sando
crear_producto "Ichigo Sando" "Fresas frescas" "92.00" "Menú Dulce"

# ============================================
# MENÚ SALADO
# ============================================
echo "Registrando Menú Salado..."

# Classic Sando
crear_producto "Classic Sando" "Jamón, queso y tocino dulce crujiente" "89.00" "Menú Salado"

# Tamago Sando
crear_producto "Tamago Sando" "Ensalada de huevo" "60.00" "Menú Salado"

# Mila Sando
crear_producto "Mila Sando" "Milanesa de res" "145.00" "Menú Salado"

# ============================================
# ENSALADAS
# ============================================
echo "Registrando Ensaladas..."

# Huevito Bowl
crear_producto "Huevito Bowl" "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, huevo duro y aderezo a elección" "125.00" "Ensaladas"

# Tuna fit
crear_producto "Tuna fit" "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, atún y aderezo a elección" "135.00" "Ensaladas"

# Mlla Green
crear_producto "Mlla Green" "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, milanesa de res, empanizado de la casa" "145.00" "Ensaladas"

# ============================================
# OTROS PLATILLOS
# ============================================
echo "Registrando Otros Platillos..."

# Molletes
crear_producto "Molletes" "Pan de la casa, frijoles, queso manchego, pico de gallo, chorizo o huevo" "0.00" "Otros"

# Chilaquiles
crear_producto "Chilaquiles" "Totopos, crema, queso, salsa de la casa, huevo ó pollo, acompañados de frijoles refritos" "0.00" "Otros"

echo ""
echo "¡Productos registrados exitosamente!"

