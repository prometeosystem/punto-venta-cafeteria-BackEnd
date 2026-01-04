import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Sin contraseña por defecto - cambiar si es necesario
            database="sistema_control_inteligente"
        )
        print("---------------Conexión exitosa-----------------")
        return conexion
    except mysql.connector.Error as error:
        print("Error al generar la conexión a la base de datos", error)
        return None

#if __name__ == "__main__":
#    crearConexion = conectar()
