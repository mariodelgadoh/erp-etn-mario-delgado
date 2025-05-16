# Sistema ERP para Empresa de Autobuses
# Este sistema incluye módulos para diferentes departamentos:
# - Admin: Acceso completo a todo el sistema
# - RH: Gestión de personal (contratación, despido, pagos)
# - Finanzas: Control presupuestario (100 millones de pesos)
# - Inventario: Control de autobuses y equipos
# - Compras: Gestión de adquisiciones (autobuses, computadoras, etc.)
# - Proveedores: Gestión de proveedores (Volvo, Mercedes Benz, HP, Dell)
# - Ventas: Sistema de venta de boletos
# - Logística: Gestión de rutas y horarios

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import hashlib
import random
import string
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from tkcalendar import DateEntry
from PIL import Image, ImageTk


# Clase principal del sistema
class SistemaERP:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema ERP -  Enlaces Terestres Nacionales")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Crear la base de datos y tablas
        self.crear_base_datos()
        
        # Crear usuarios predefinidos para administradores y jefes
        self.crear_usuarios_predefinidos()
        
        # Iniciar con la pantalla de login
        self.mostrar_login()
    
    def crear_base_datos(self):
        # Conectar a la base de datos (se crea si no existe)
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL,
            departamento TEXT NOT NULL
        )
        ''')
        
        # Tabla de empleados
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            edad INTEGER NOT NULL,
            puesto TEXT NOT NULL,
            fecha_contratacion TEXT NOT NULL,
            salario REAL NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
        ''')
        
        # Tabla de finanzas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS finanzas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            concepto TEXT NOT NULL,
            ingreso REAL DEFAULT 0,
            egreso REAL DEFAULT 0,
            saldo_actual REAL NOT NULL
        )
        ''')
        
        # Tabla de inventario de autobuses
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS autobuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            año INTEGER NOT NULL,
            capacidad INTEGER NOT NULL DEFAULT 24,
            estado TEXT NOT NULL
        )
        ''')
        
        # Tabla de inventario de computadoras
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS computadoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            asignado_a TEXT,
            departamento TEXT,
            estado TEXT NOT NULL
        )
        ''')
        
        # Tabla de proveedores
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            contacto TEXT,
            telefono TEXT,
            email TEXT
        )
        ''')
        
        # Tabla de compras
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            proveedor_id INTEGER NOT NULL,
            tipo_producto TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores (id)
        )
        ''')
        
        # Tabla de rutas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            distancia REAL NOT NULL,
            tiempo_estimado TEXT NOT NULL,
            precio_boleto REAL NOT NULL
        )
        ''')
        
        # Tabla de horarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruta_id INTEGER NOT NULL,
            autobus_id INTEGER NOT NULL,
            hora_salida TEXT NOT NULL,
            hora_llegada TEXT NOT NULL,
            dias_semana TEXT NOT NULL,
            FOREIGN KEY (ruta_id) REFERENCES rutas (id),
            FOREIGN KEY (autobus_id) REFERENCES autobuses (id)
        )
        ''')
        
        # Tabla de boletos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS boletos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_pasajero TEXT NOT NULL,
            apellidos_pasajero TEXT NOT NULL,
            horario_id INTEGER NOT NULL,
            numero_asiento INTEGER NOT NULL,
            fecha_viaje TEXT NOT NULL,
            fecha_compra TEXT NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (horario_id) REFERENCES horarios (id)
        )
        ''')
        
        # Tabla de pagos a empleados
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos_empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            concepto TEXT NOT NULL,
            FOREIGN KEY (empleado_id) REFERENCES empleados (id)
        )
        ''')
        
        # Insertar saldo inicial en finanzas
        cursor.execute("SELECT COUNT(*) FROM finanzas")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
            INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
            VALUES (?, ?, ?, ?, ?)
            ''', (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Saldo inicial", 100000000, 0, 100000000))
        
        # Insertar proveedores predefinidos
        cursor.execute("SELECT COUNT(*) FROM proveedores")
        if cursor.fetchone()[0] == 0:
            proveedores = [
                ("Volvo", "Autobuses", "Juan Pérez", "555-1234", "ventas@volvo.com"),
                ("Mercedes Benz", "Autobuses", "María López", "555-5678", "ventas@mercedes.com"),
                ("HP", "Computadoras", "Carlos Rodríguez", "555-9876", "ventas@hp.com"),
                ("Dell", "Computadoras", "Ana García", "555-5432", "ventas@dell.com")
            ]
            
            for proveedor in proveedores:
                cursor.execute('''
                INSERT INTO proveedores (nombre, tipo, contacto, telefono, email)
                VALUES (?, ?, ?, ?, ?)
                ''', proveedor)
        
        conn.commit()
        conn.close()
    
    def crear_usuarios_predefinidos(self):
        # Función para hashear contraseñas
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # Crear usuarios predefinidos
            usuarios = [
                ("Admin", "Principal", "admin", hash_password("admin123"), "Admin", "Administración"),
                ("Jefe", "RH", "rh_jefe", hash_password("rh123"), "Jefe", "RH"),
                ("Jefe", "Finanzas", "finanzas_jefe", hash_password("fin123"), "Jefe", "Finanzas"),
                ("Jefe", "Inventario", "inventario_jefe", hash_password("inv123"), "Jefe", "Inventario"),
                ("Jefe", "Compras", "compras_jefe", hash_password("comp123"), "Jefe", "Compras"),
                ("Jefe", "Proveedores", "proveedores_jefe", hash_password("prov123"), "Jefe", "Proveedores"),
                ("Jefe", "Ventas", "ventas_jefe", hash_password("vent123"), "Jefe", "Ventas"),
                ("Jefe", "Logística", "logistica_jefe", hash_password("log123"), "Jefe", "Logística")
            ]
            
            for usuario in usuarios:
                cursor.execute('''
                INSERT INTO usuarios (nombre, apellidos, username, password, rol, departamento)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', usuario)
        
        conn.commit()
        conn.close()
    
    def generar_usuario_unico(self, nombre, apellidos):
        # Generar nombre de usuario a partir del nombre y apellido
        nombre_simple = re.sub(r'[^a-zA-Z]', '', nombre.lower())
        apellido_simple = re.sub(r'[^a-zA-Z]', '', apellidos.split()[0].lower())
        base_username = f"{nombre_simple[0:3]}{apellido_simple[0:3]}"
        
        # Verificar si ya existe
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM usuarios WHERE username LIKE ?", (f"{base_username}%",))
        usernames_existentes = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Si no existe, usar base_username
        if base_username not in usernames_existentes:
            return base_username
        
        # Si existe, añadir número
        i = 1
        while f"{base_username}{i}" in usernames_existentes:
            i += 1
        
        return f"{base_username}{i}"
    
    def generar_contraseña_unica(self, longitud=8):
        # Generar contraseña aleatoria
        caracteres = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choice(caracteres) for _ in range(longitud))
    
    def mostrar_login(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Fondo de la ventana
        self.root.configure(bg="#e6ecf0")

        # Crear Frame principal
        login_frame = tk.Frame(self.root, bg="white", bd=2, relief="ridge", padx=30, pady=30)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Cargar y mostrar el logo
        try:
            logo_img = Image.open("logo.png")
            logo_img = logo_img.resize((150, 150), Image.LANCZOS)  # Usa LANCZOS para mejor calidad
            self.logo_tk = ImageTk.PhotoImage(logo_img)  # IMPORTANTE: guardar como atributo de clase
            logo_label = tk.Label(login_frame, image=self.logo_tk, bg="white")
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

        # Título
        tk.Label(
            login_frame,
            text="Enlaces Terrestres Nacionales",
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg="#003366"
        ).pack(pady=(0, 20))

        # Campo Usuario
        tk.Label(login_frame, text="Usuario", font=("Helvetica", 12), bg="white").pack(anchor="w")
        self.username_entry = tk.Entry(login_frame, width=30, font=("Helvetica", 11), bd=1, relief="solid")
        self.username_entry.pack(pady=(0, 15))

        # Campo Contraseña
        tk.Label(login_frame, text="Contraseña", font=("Helvetica", 12), bg="white").pack(anchor="w")
        self.password_entry = tk.Entry(login_frame, width=30, font=("Helvetica", 11), show="*", bd=1, relief="solid")
        self.password_entry.pack(pady=(0, 25))

        # Botón Iniciar Sesión
        tk.Button(
            login_frame,
            text="Iniciar Sesión",
            command=self.validar_login,
            font=("Helvetica", 12, "bold"),
            bg="#003366",
            fg="white",
            activebackground="#002244",
            activeforeground="white",
            width=20,
            relief="flat",
            cursor="hand2"
        ).pack()

        # Footer opcional
        tk.Label(
            login_frame,
            text="© ETN Autotransporte 2025",
            font=("Helvetica", 9),
            bg="white",
            fg="#666666"
        ).pack(pady=(30, 0))
    
    def validar_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return
        
        # Hashear contraseña para comparar
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Verificar en la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, nombre, apellidos, rol, departamento 
        FROM usuarios 
        WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            self.usuario_actual = {
                'id': usuario[0],
                'nombre': usuario[1],
                'apellidos': usuario[2],
                'username': username,
                'rol': usuario[3],
                'departamento': usuario[4]
            }
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def mostrar_menu_principal(self):
        # Importar datetime para la fecha y hora
        from datetime import datetime
        import tkinter as tk
        from tkinter import font as tkfont
        
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar fondo de la ventana
        self.root.configure(bg="#e6ecf0")

        # Frame principal con estilo
        main_frame = tk.Frame(self.root, bg="white", bd=2, relief="ridge")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame superior para información y cierre de sesión
        top_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        # Botón de cierre de sesión con estilo mejorado
        logout_btn = tk.Button(
            top_frame, 
            text="Cerrar Sesión", 
            command=self.mostrar_login,
            font=("Helvetica", 10, "bold"),
            bg="#cc0000",
            fg="white",
            activebackground="#990000",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            bd=0,
            borderwidth=0,
        )
        logout_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Frame para fecha y hora (antes del botón de cerrar sesión)
        datetime_frame = tk.Frame(top_frame, bg="white")
        datetime_frame.pack(side=tk.RIGHT, padx=(0, 15))

        # Obtener fecha y hora actual
        now = datetime.now()
        fecha_str = now.strftime("%d/%m/%Y")
        hora_str = now.strftime("%H:%M:%S")

        # Mostrar fecha y hora con estilo
        fecha_label = tk.Label(
            datetime_frame, 
            text=f"Fecha: {fecha_str}", 
            font=("Helvetica", 9),
            bg="white",
            fg="#666666"
        )
        fecha_label.pack(anchor="e")
        
        hora_label = tk.Label(
            datetime_frame, 
            text=f"Hora: {hora_str}", 
            font=("Helvetica", 9),
            bg="white",
            fg="#666666"
        )
        hora_label.pack(anchor="e")
        
        # Función para actualizar la hora
        def actualizar_hora():
            current_time = datetime.now().strftime("%H:%M:%S")
            hora_label.config(text=f"Hora: {current_time}")
            main_frame.after(1000, actualizar_hora)  # Actualizar cada segundo
        
        # Iniciar la actualización de la hora
        actualizar_hora()

        # Información del usuario con estilo y alineada a la izquierda
        info_frame = tk.Frame(top_frame, bg="white")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separar la información del usuario en múltiples líneas para mejor visualización
        nombre_completo = f"{self.usuario_actual['nombre']} {self.usuario_actual['apellidos']}"
        
        usuario_label = tk.Label(
            info_frame, 
            text=f"Usuario: {nombre_completo}",
            font=("Helvetica", 10, "bold"),
            bg="white",
            fg="#333333",
            anchor="w"
        )
        usuario_label.pack(side=tk.TOP, anchor="w", padx=10)
        
        rol_dept_label = tk.Label(
            info_frame, 
            text=f"Rol: {self.usuario_actual['rol']} | Departamento: {self.usuario_actual['departamento']}",
            font=("Helvetica", 10),
            bg="white",
            fg="#666666",
            anchor="w"
        )
        rol_dept_label.pack(side=tk.TOP, anchor="w", padx=10)

        # Línea separadora horizontal con degradado
        separator_frame = tk.Frame(main_frame, height=2, bg="#e0e0e0")
        separator_frame.pack(fill=tk.X, pady=(5, 0))

        # Frame para contenido principal
        content_frame = tk.Frame(main_frame, bg="white", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para el logo centrado
        logo_frame = tk.Frame(content_frame, bg="white")
        logo_frame.pack(pady=(10, 20), fill=tk.X)

        # Cargar, redimensionar y mostrar logo
        try:
            # Cargar la imagen original
            original_logo = tk.PhotoImage(file="logo.png")
            
            # Redimensionar la imagen (ajustar estos valores según necesites)
            width = 200  # Ancho deseado
            height = 200  # Alto deseado
            logo_img = original_logo.subsample(
                max(1, original_logo.width() // width),
                max(1, original_logo.height() // height)
            )
            
            # Mostrar logo centrado
            logo_label = tk.Label(logo_frame, image=logo_img, bg="white")
            logo_label.image = logo_img  # Guardar referencia
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            # Mostrar un placeholder si no se carga la imagen
            tk.Label(
                logo_frame, 
                text="LOGO", 
                font=("Helvetica", 24, "bold"),
                bg="white",
                fg="#cccccc"
            ).pack(pady=20)

        # Título con estilo mejorado
        titulo_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        titulo_label = tk.Label(
            content_frame, 
            text="Menú Principal", 
            font=titulo_font,
            bg="white",
            fg="#003366"
        )
        titulo_label.pack(pady=(0, 25))
        
        # Línea decorativa debajo del título
        title_underline = tk.Frame(content_frame, height=3, width=200, bg="#003366")
        title_underline.pack(pady=(0, 25))

        # Frame para botones
        buttons_frame = tk.Frame(content_frame, bg="white")
        buttons_frame.pack(pady=15)

        # Si es Admin, tiene acceso a todo
        if self.usuario_actual['rol'] == 'Admin':
            self.crear_botones_admin(buttons_frame)
        else:
            # Otros roles solo tienen acceso a su departamento
            self.crear_botones_departamento(buttons_frame)

    def crear_botones_admin(self, parent_frame):
        # Botones para todos los departamentos con estilo
        departamentos = [
            ("Recursos Humanos", self.mostrar_modulo_rh),
            ("Finanzas", self.mostrar_modulo_finanzas),
            ("Inventario", self.mostrar_modulo_inventario),
            ("Compras", self.mostrar_modulo_compras),
            ("Proveedores", self.mostrar_modulo_proveedores),
            ("Ventas", self.mostrar_modulo_ventas),
            ("Logística", self.mostrar_modulo_logistica),
            ("Reportes Generales", self.mostrar_reportes_generales)
        ]
        
        # Configurar el grid para 4 filas y 2 columnas
        for i in range(2):  # 2 columnas
            parent_frame.grid_columnconfigure(i, weight=1, uniform="cols")
        for i in range(4):  # 4 filas
            parent_frame.grid_rowconfigure(i, weight=1)
        
        # Colocar los botones en la cuadrícula 4x2
        for i, (texto, comando) in enumerate(departamentos):
            row = i // 2  # 0-3 (4 filas)
            col = i % 2   # 0-1 (2 columnas)
            
            # Frame contenedor para efecto hover
            btn_container = tk.Frame(parent_frame, bg="white", padx=3, pady=3)
            btn_container.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            
            # El botón ocupa todo el espacio del contenedor
            btn = tk.Button(
                btn_container, 
                text=texto, 
                command=comando, 
                width=22,  # Un poco más ancho para mejor visualización
                height=2,
                font=("Helvetica", 12, "bold"),
                bg="#003366",
                fg="white",
                activebackground="#002244",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                bd=0,  # Sin borde
                padx=10
            )
            btn.pack(fill=tk.BOTH, expand=True)

    def crear_botones_departamento(self, parent_frame):
        # Mostrar solo el botón del departamento correspondiente con estilo
        departmento_actual = self.usuario_actual['departamento']
        
        # Diccionario que mapea departamentos a sus funciones
        dept_funciones = {
            "RH": (self.mostrar_modulo_rh, "Recursos Humanos"),
            "Finanzas": (self.mostrar_modulo_finanzas, "Finanzas"),
            "Inventario": (self.mostrar_modulo_inventario, "Inventario"),
            "Compras": (self.mostrar_modulo_compras, "Compras"),
            "Proveedores": (self.mostrar_modulo_proveedores, "Proveedores"),
            "Ventas": (self.mostrar_modulo_ventas, "Ventas"),
            "Logística": (self.mostrar_modulo_logistica, "Logística")
        }
        
        if departmento_actual in dept_funciones:
            funcion, texto = dept_funciones[departmento_actual]
            
            # Frame contenedor para efecto hover
            btn_container = tk.Frame(parent_frame, bg="white", padx=3, pady=3)
            btn_container.pack(pady=25)
            
            # Botón con estilo mejorado
            btn = tk.Button(
                btn_container, 
                text=texto, 
                command=funcion, 
                width=24, 
                height=3,
                font=("Helvetica", 14, "bold"),
                bg="#003366",
                fg="white",
                activebackground="#002244",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                bd=0
            )
            btn.pack(fill=tk.BOTH, expand=True)
# ==================== MÓDULO DE RECURSOS HUMANOS ====================
    def mostrar_modulo_rh(self):
        # Configurar color de fondo de la ventana
        self.root.configure(bg='#e6ecf0')
    
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#e6ecf0')
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame, bg='#FFFFFF', bd=2, relief='ridge')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", 
                            command=self.mostrar_menu_principal,
                            bg='#003366', fg='#FFFFFF', activebackground='#002244',
                            font=('Arial', 10, 'bold'), relief='flat', cursor='hand2')
        back_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Título
        tk.Label(top_frame, text="Módulo de Recursos Humanos", 
                font=("Arial", 16, 'bold'), fg='#003366', bg='#FFFFFF').pack(side=tk.LEFT, padx=10)
        
        # Frame de pestañas
        style = ttk.Style()
        style.configure('TNotebook', background='#e6ecf0')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
        
        tab_control = ttk.Notebook(main_frame)
        
        # Pestaña Contratar
        tab_contratar = ttk.Frame(tab_control)
        tab_control.add(tab_contratar, text="Contratar")
        self.setup_tab_contratar(tab_contratar)
        
        # Pestaña Empleados
        tab_empleados = ttk.Frame(tab_control)
        tab_control.add(tab_empleados, text="Empleados")
        self.setup_tab_empleados(tab_empleados)
        
        # Pestaña Pagos
        tab_pagos = ttk.Frame(tab_control)
        tab_control.add(tab_pagos, text="Pagos")
        self.setup_tab_pagos(tab_pagos)
        
        # Pestaña Contraseñas
        tab_contrasenas = ttk.Frame(tab_control)
        tab_control.add(tab_contrasenas, text="Contraseñas")
        self.setup_tab_contrasenas(tab_contrasenas)
        
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

    def setup_tab_contratar(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='#FFFFFF', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Título
        tk.Label(frame, text="Contratar Nuevo Empleado", 
                font=("Arial", 14, 'bold'), fg='#003366', bg='#FFFFFF').pack(pady=(10, 5))

        # Logo debajo del título
        try:
            logo_img = Image.open("logo.png")  # Asegúrate que la ruta es correcta
            logo_img = logo_img.resize((150, 150), Image.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo_img)  # Mantener en self para evitar garbage collection
            logo_label = tk.Label(frame, image=self.logo_tk, bg='#FFFFFF')
            logo_label.pack(pady=(0, 10))
        except Exception as e:
            print("Error cargando logo:", e)

        # Formulario
        form_frame = tk.Frame(frame, bg='#FFFFFF')
        form_frame.pack(pady=10)
        
        # Nombre
        tk.Label(form_frame, text="Nombre:", font=('Arial', 11), bg='#FFFFFF').grid(row=0, column=0, sticky="w", pady=5)
        self.nombre_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Apellidos
        tk.Label(form_frame, text="Apellidos:", font=('Arial', 11), bg='#FFFFFF').grid(row=1, column=0, sticky="w", pady=5)
        self.apellidos_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')
        self.apellidos_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Edad
        tk.Label(form_frame, text="Edad:", font=('Arial', 11), bg='#FFFFFF').grid(row=2, column=0, sticky="w", pady=5)
        self.edad_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')
        self.edad_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Puesto
        tk.Label(form_frame, text="Puesto:", font=('Arial', 11), bg='#FFFFFF').grid(row=3, column=0, sticky="w", pady=5)
        puestos = ["Agente RH", "Agente Finanzas", "Agente Inventario", "Agente Compras", 
                "Agente Proveedores", "Agente Ventas", "Agente Logística", "Conductor"]
        self.puesto_combobox = ttk.Combobox(form_frame, values=puestos, width=27, font=('Arial', 11))
        self.puesto_combobox.grid(row=3, column=1, pady=5, padx=5)
        
        # Salario
        tk.Label(form_frame, text="Salario:", font=('Arial', 11), bg='#FFFFFF').grid(row=4, column=0, sticky="w", pady=5)
        self.salario_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')
        self.salario_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Botón para contratar
        tk.Button(frame, text="Contratar", command=self.contratar_empleado,
                bg='#003366', fg='#FFFFFF', activebackground='#002244',
                font=('Arial', 11, 'bold'), relief='flat', cursor='hand2').pack(pady=20)

    def setup_tab_empleados(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='#FFFFFF', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Controles superiores
        controls_frame = tk.Frame(frame, bg='#FFFFFF')
        controls_frame.pack(fill=tk.X, pady=10)

        # Botón para despedir empleado
        btn_despedir = tk.Button(
            controls_frame, text="Despedir Empleado",
            command=self.despedir_empleado_y_refrescar,
            bg='#990000', fg='#FFFFFF', activebackground='#660000',
            font=('Arial', 10, 'bold'), relief='flat', cursor='hand2'
        )
        btn_despedir.pack(side=tk.LEFT, padx=5)

        # Botón para ver despedidos
        self.mostrando_despedidos = False
        self.btn_ver_despedidos = tk.Button(
            controls_frame, text="Ver Empleados Despedidos",
            command=self.toggle_empleados_despedidos,
            bg='#003366', fg='#FFFFFF', activebackground='#002244',
            font=('Arial', 10, 'bold'), relief='flat', cursor='hand2'
        )
        self.btn_ver_despedidos.pack(side=tk.LEFT, padx=5)

        # Treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 11), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))

        columns = ("ID", "Nombre", "Apellidos", "Edad", "Puesto", "Fecha Contratación", "Salario", "Estado")
        self.tree_empleados = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.tree_empleados.heading(col, text=col)
            self.tree_empleados.column(col, width=100)

        self.tree_empleados.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_empleados.yview)
        self.tree_empleados.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mostrar empleados activos al inicio
        self.cargar_empleados(self.tree_empleados, solo_activos=True)
    
    def refrescar_lista_empleados(self):
        """Recarga la lista respetando el estado actual (activos o despedidos)."""
        if self.mostrando_despedidos:
            self.cargar_empleados(self.tree_empleados, solo_activos=False)
        else:
            self.cargar_empleados(self.tree_empleados, solo_activos=True)

    def despedir_empleado_y_refrescar(self):
        """Despide al empleado seleccionado y recarga solo los activos."""
        self.despedir_empleado(self.tree_empleados)
        self.mostrando_despedidos = False
        self.btn_ver_despedidos.config(text="Ver Empleados Despedidos")
        self.cargar_empleados(self.tree_empleados, solo_activos=True)

    def toggle_empleados_despedidos(self):
        """Alterna entre ver activos y despedidos."""
        self.mostrando_despedidos = not self.mostrando_despedidos
        if self.mostrando_despedidos:
            self.btn_ver_despedidos.config(text="Ver Empleados Activos")
            self.cargar_empleados(self.tree_empleados, solo_activos=False)
        else:
            self.btn_ver_despedidos.config(text="Ver Empleados Despedidos")
            self.cargar_empleados(self.tree_empleados, solo_activos=True)

    def setup_tab_pagos(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='#FFFFFF', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame superior para filtros
        top_frame = tk.Frame(frame, bg='#FFFFFF')
        top_frame.pack(fill=tk.X, pady=10)

        # Barra de búsqueda
        tk.Label(top_frame, text="Buscar Empleado:", font=('Arial', 11), bg='#FFFFFF').pack(side=tk.LEFT, padx=5)
        self.busqueda_empleado = tk.StringVar()
        search_entry = tk.Entry(top_frame, textvariable=self.busqueda_empleado, width=30, 
                            font=('Arial', 11), bd=1, relief='solid')
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.filtrar_empleados())

        # Botón para realizar pago
        tk.Button(top_frame, text="Realizar Pago", command=self.realizar_pago,
                bg='#003366', fg='#FFFFFF', activebackground='#002244',
                font=('Arial', 10, 'bold'), relief='flat', cursor='hand2').pack(side=tk.RIGHT, padx=10)

        # Lista de empleados con scrollbar
        list_frame = tk.Frame(frame, bg='#FFFFFF')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_empleados = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Arial', 11), bd=1, relief='solid')
        self.lista_empleados.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_empleados.yview)

        # Frame para gráfico mejorado
        grafico_frame = tk.Frame(frame, bg='#FFFFFF')
        grafico_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear figura para el gráfico mejorado
        self.figure_pagos = plt.Figure(figsize=(8, 5), dpi=100)
        self.ax_pagos = self.figure_pagos.add_subplot(111)
        self.figure_pagos.subplots_adjust(bottom=0.3)  # Ajustar espacio para etiquetas

        # Canvas para el gráfico
        self.canvas_pagos = FigureCanvasTkAgg(self.figure_pagos, grafico_frame)
        self.canvas_pagos.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cargar datos iniciales
        self.cargar_empleados_lista()
        self.actualizar_grafico_pagos()

    def setup_tab_contrasenas(self, parent):
        """Nueva pestaña para gestión de contraseñas"""
        frame = tk.Frame(parent, bg='#FFFFFF', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        tk.Label(frame, text="Gestión de Contraseñas", 
                font=("Arial", 14, 'bold'), fg='#003366', bg='#FFFFFF').pack(pady=10)

        # Frame para búsqueda de empleado
        empleado_frame = tk.Frame(frame, bg='#FFFFFF')
        empleado_frame.pack(fill=tk.X, pady=5)

        tk.Label(empleado_frame, text="Buscar Empleado:", font=('Arial', 11), bg='#FFFFFF').pack(side=tk.LEFT, padx=5)

        self.busqueda_contrasena = tk.StringVar()
        search_entry = tk.Entry(empleado_frame, textvariable=self.busqueda_contrasena, width=40, 
                              font=('Arial', 11), bd=1, relief='solid')
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.filtrar_empleados_contrasena())

        # Lista de empleados con scrollbar (debajo del buscador)
        list_frame = tk.Frame(frame, bg='#FFFFFF')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_empleados_contrasena = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Arial', 11), bd=1, relief='solid', height=6)
        self.lista_empleados_contrasena.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_empleados_contrasena.yview)

        # Frame para formulario de contraseña (debajo de la lista)
        form_frame = tk.Frame(frame, bg='#FFFFFF')
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Nueva Contraseña:", font=('Arial', 11), bg='#FFFFFF').grid(row=0, column=0, sticky="w", pady=5)
        self.nueva_contrasena_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')  # sin show="*"
        self.nueva_contrasena_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Confirmar Contraseña:", font=('Arial', 11), bg='#FFFFFF').grid(row=1, column=0, sticky="w", pady=5)
        self.confirmar_contrasena_entry = tk.Entry(form_frame, width=30, font=('Arial', 11), bd=1, relief='solid')  # sin show="*"
        self.confirmar_contrasena_entry.grid(row=1, column=1, pady=5, padx=5)

        # Frame para botones
        button_frame = tk.Frame(frame, bg='#FFFFFF')
        button_frame.pack(pady=10)

        # Botón para cambiar contraseña
        cambiar_btn = tk.Button(button_frame, text="Cambiar Contraseña", command=self.cambiar_contrasena,
                bg='#003366', fg='#FFFFFF', activebackground='#002244',
                font=('Arial', 11, 'bold'), relief='flat', cursor='hand2', width=25, height=2)
        cambiar_btn.pack(side=tk.LEFT, padx=10)

        # Botón para generar contraseña aleatoria
        generar_btn = tk.Button(button_frame, text="Generar Contraseña Aleatoria", 
                command=self.generar_contrasena_aleatoria,
                bg='#003366', fg='#FFFFFF', activebackground='#002244',
                font=('Arial', 11, 'bold'), relief='flat', cursor='hand2', width=25, height=2)
        generar_btn.pack(side=tk.LEFT, padx=10)

        # Cargar empleados inicialmente
        self.cargar_empleados_para_contrasena()

    def filtrar_empleados_contrasena(self):
        """Filtra la lista de empleados según el texto de búsqueda"""
        busqueda = self.busqueda_contrasena.get().lower()
        self.lista_empleados_contrasena.delete(0, tk.END)

        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT u.id, e.nombre, e.apellidos, u.username 
                FROM usuarios u
                JOIN empleados e ON u.nombre = e.nombre AND u.apellidos = e.apellidos
                WHERE e.activo = 1
                ORDER BY e.nombre, e.apellidos
            ''')

            for row in cursor.fetchall():
                empleado_str = f"{row[0]} - {row[1]} {row[2]} ({row[3]})"
                if busqueda in empleado_str.lower():
                    self.lista_empleados_contrasena.insert(tk.END, empleado_str)

        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar empleados: {str(e)}")
        finally:
            conn.close()

    def cargar_empleados_para_contrasena(self):
        """Carga los empleados que tienen cuentas de usuario"""
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT u.id, e.nombre, e.apellidos, u.username 
                FROM usuarios u
                JOIN empleados e ON u.nombre = e.nombre AND u.apellidos = e.apellidos
                WHERE e.activo = 1
                ORDER BY e.nombre, e.apellidos
            ''')

            self.lista_empleados_contrasena.delete(0, tk.END)

            for row in cursor.fetchall():
                self.lista_empleados_contrasena.insert(tk.END, f"{row[0]} - {row[1]} {row[2]} ({row[3]})")

            if self.lista_empleados_contrasena.size() == 0:
                messagebox.showinfo("Información", "No hay empleados con cuentas de usuario activas")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")
        finally:
            conn.close()

    def cambiar_contrasena(self):
        """Cambia la contraseña del empleado seleccionado"""
        seleccion = self.lista_empleados_contrasena.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Debe seleccionar un empleado")
            return

        empleado_str = self.lista_empleados_contrasena.get(seleccion[0])
        usuario_id = int(empleado_str.split("-")[0].strip())

        nueva_contrasena = self.nueva_contrasena_entry.get()
        confirmar_contrasena = self.confirmar_contrasena_entry.get()

        if not nueva_contrasena or not confirmar_contrasena:
            messagebox.showwarning("Advertencia", "Debe ingresar y confirmar la nueva contraseña")
            return

        if nueva_contrasena != confirmar_contrasena:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden")
            return

        if len(nueva_contrasena) < 6:
            messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 6 caracteres")
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de cambiar la contraseña de este empleado?"):
            return

        contrasena_hash = hashlib.sha256(nueva_contrasena.encode()).hexdigest()

        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE usuarios SET password = ?
                WHERE id = ?
            ''', (contrasena_hash, usuario_id))

            conn.commit()
            messagebox.showinfo("Éxito", "Contraseña cambiada exitosamente")
            self.nueva_contrasena_entry.delete(0, tk.END)
            self.confirmar_contrasena_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar contraseña: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def generar_contrasena_aleatoria(self):
        """Genera una contraseña aleatoria segura"""
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        contrasena = ''.join(random.choice(caracteres) for i in range(10))

        self.nueva_contrasena_entry.delete(0, tk.END)
        self.nueva_contrasena_entry.insert(0, contrasena)
        self.confirmar_contrasena_entry.delete(0, tk.END)
        self.confirmar_contrasena_entry.insert(0, contrasena)

        messagebox.showinfo("Contraseña Generada", f"Se ha generado una nueva contraseña:\n\n{contrasena}")

    def toggle_empleados_despedidos(self):
        """Alterna entre mostrar empleados activos y despedidos"""
        self.mostrando_despedidos = not self.mostrando_despedidos
    
        if self.mostrando_despedidos:
            self.btn_ver_despedidos.config(text="Ver Empleados Activos")
            # Mostrar solo despedidos
            self.cargar_empleados(self.tree_empleados, solo_despedidos=True)
        else:
            self.btn_ver_despedidos.config(text="Ver Empleados Despedidos")
            # Mostrar solo activos
            self.cargar_empleados(self.tree_empleados, solo_activos=True)
    
    def filtrar_empleados(self):
        busqueda = self.busqueda_empleado.get().lower()
        self.lista_empleados.delete(0, tk.END)
    
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, nombre, apellidos FROM empleados 
                WHERE activo = 1 
                ORDER BY nombre, apellidos
            ''')
            for row in cursor.fetchall():
                empleado_str = f"{row[0]} - {row[1]} {row[2]}"
                if busqueda in empleado_str.lower():
                    self.lista_empleados.insert(tk.END, empleado_str)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")
        finally:
            conn.close()
    
    def contratar_empleado(self):
        # Obtener datos del formulario
        nombre = self.nombre_entry.get()
        apellidos = self.apellidos_entry.get()
    
        try:
            edad = int(self.edad_entry.get())
            if edad < 18 or edad > 70:
                messagebox.showerror("Error", "La edad debe estar entre 18 y 70 años")
                return
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número")
            return
    
        puesto = self.puesto_combobox.get()
        if not puesto:
            messagebox.showerror("Error", "Debe seleccionar un puesto")
            return
    
        try:
            salario = float(self.salario_entry.get())
            if salario <= 0:
                messagebox.showerror("Error", "El salario debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número")
            return
    
        # Fecha actual como fecha de contratación
        fecha_contratacion = datetime.datetime.now().strftime("%Y-%m-%d")
    
        # Insertar en la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute('''
            INSERT INTO empleados (nombre, apellidos, edad, puesto, fecha_contratacion, salario, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (nombre, apellidos, edad, puesto, fecha_contratacion, salario))
        
            empleado_id = cursor.lastrowid
        
            # Si no es conductor, crear cuenta de usuario
            if puesto != "Conductor":
                # Generar usuario y contraseña
                username = self.generar_usuario_unico(nombre, apellidos)
                password_plain = self.generar_contraseña_unica()
                password_hash = hashlib.sha256(password_plain.encode()).hexdigest()
            
                # Determinar departamento según puesto
                departamento = puesto.replace("Agente ", "")
            
                # Insertar usuario en la tabla de usuarios
                cursor.execute('''
                INSERT INTO usuarios (nombre, apellidos, username, password, rol, departamento)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (nombre, apellidos, username, password_hash, "Empleado", departamento))
            
                # Mostrar credenciales
                messagebox.showinfo("Empleado Contratado", 
                                f"Empleado contratado exitosamente.\n\nDatos de acceso:\nUsuario: {username}\nContraseña: {password_plain}")
            else:
                messagebox.showinfo("Empleado Contratado", "Conductor contratado exitosamente.")
        
            conn.commit()
        
            # Limpiar formulario
            self.nombre_entry.delete(0, tk.END)
            self.apellidos_entry.delete(0, tk.END)
            self.edad_entry.delete(0, tk.END)
            self.puesto_combobox.set("")
            self.salario_entry.delete(0, tk.END)
        
            # Actualizar todas las listas de empleados
            self.actualizar_vistas_empleados()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al contratar empleado: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def actualizar_vistas_empleados(self):
        """Actualiza todas las vistas que muestran listas de empleados"""
        # Actualizar lista en pestaña de Empleados
        if hasattr(self, 'tree_empleados') and self.tree_empleados:
            self.cargar_empleados(self.tree_empleados)
    
        # Actualizar lista en pestaña de Pagos
        if hasattr(self, 'lista_empleados'):
            self.cargar_empleados_lista()
    
        # Actualizar lista en pestaña de Contraseñas
        if hasattr(self, 'lista_empleados_contrasena'):
            self.cargar_empleados_para_contrasena()
    
        # Actualizar gráfico de pagos si está visible
        if hasattr(self, 'canvas_pagos'):
            self.actualizar_grafico_pagos()
    
    def cargar_empleados(self, tree, solo_activos=False, solo_despedidos=False):
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
    
        # Cargar empleados de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            query = '''
            SELECT id, nombre, apellidos, edad, puesto, fecha_contratacion, salario, 
                CASE WHEN activo = 1 THEN 'Activo' ELSE 'Despedido' END as estado
            FROM empleados
            '''
        
            conditions = []
            if solo_activos:
                conditions.append('activo = 1')
            if solo_despedidos:
                conditions.append('activo = 0')
        
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
            # Ordenar siempre por ID (cambiar 'nombre, apellidos' por 'id')
            query += ' ORDER BY id ASC'  # ASC para orden ascendente
        
            cursor.execute(query)
        
            for row in cursor.fetchall():
                # Formatear el salario para mostrar 2 decimales
                row_list = list(row)
                if row_list[6]:  # Si tiene valor salario
                    row_list[6] = f"${float(row_list[6]):.2f}"
                else:
                    row_list[6] = "$0.00"
                tree.insert("", tk.END, values=tuple(row_list))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")
        finally:
            conn.close()

    def despedir_empleado(self, tree):
        # Obtener el elemento seleccionado
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Debe seleccionar un empleado")
            return

        # Obtener ID del empleado
        empleado_id = tree.item(selection[0], "values")[0]
    
        # Confirmar despido
        if messagebox.askyesno("Confirmar", "¿Está seguro de despedir a este empleado?"):
            conn = sqlite3.connect('erp_autobuses.db')
            cursor = conn.cursor()
        
            try:
                # 1. Obtener datos del empleado antes de despedirlo
                cursor.execute('''
                    SELECT nombre, apellidos, puesto FROM empleados WHERE id = ?
                ''', (empleado_id,))
                empleado_data = cursor.fetchone()
            
                if not empleado_data:
                    messagebox.showerror("Error", "Empleado no encontrado")
                    return
            
                nombre, apellidos, puesto = empleado_data
        
                # 2. Actualizar estado del empleado a inactivo (solo esto es esencial)
                cursor.execute('''
                    UPDATE empleados SET activo = 0 
                    WHERE id = ?
                ''', (empleado_id,))
            
                # 3. Si no es conductor, eliminar su usuario (opcional)
                if puesto != "Conductor":
                    cursor.execute('''
                        DELETE FROM usuarios
                        WHERE nombre = ? AND apellidos = ?
                    ''', (nombre, apellidos))
            
                conn.commit()
                messagebox.showinfo("Éxito", f"Empleado despedido exitosamente\n\nNombre: {nombre} {apellidos}\nPuesto: {puesto}")
            
                # 4. Refrescar listas según lo que estemos viendo actualmente
                if hasattr(self, 'mostrando_despedidos') and self.mostrando_despedidos:
                    # Si estamos viendo despedidos, recargar solo despedidos
                    self.cargar_empleados(tree, solo_despedidos=True)
                else:
                    # Si estamos viendo activos, recargar solo activos
                    self.cargar_empleados(tree, solo_activos=True)
            
                # 5. Actualizar otras vistas del sistema
                if hasattr(self, 'lista_empleados'):
                    self.cargar_empleados_lista()  # Actualizar lista en pestaña de Pagos
            
                if hasattr(self, 'canvas_pagos'):
                    self.actualizar_grafico_pagos()  # Actualizar gráfico de pagos
                
                if hasattr(self, 'lista_empleados_contrasena'):
                    self.cargar_empleados_para_contrasena()  # Actualizar lista en pestaña de Contraseñas
        
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Error al despedir empleado: {str(e)}")
            finally:
                conn.close()
    
    def cargar_empleados_lista(self):
        self.lista_empleados.delete(0, tk.END)
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, nombre, apellidos FROM empleados 
                WHERE activo = 1 
                ORDER BY nombre, apellidos
            ''')
            for row in cursor.fetchall():
                self.lista_empleados.insert(tk.END, f"{row[0]} - {row[1]} {row[2]}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")
        finally:
            conn.close()
    
        # Limpiar la búsqueda para mostrar todos los empleados
        self.busqueda_empleado.set("")
    
    def realizar_pago(self):
        # Obtener empleado seleccionado
        seleccion = self.lista_empleados.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Debe seleccionar un empleado")
            return
    
        empleado_str = self.lista_empleados.get(seleccion[0])
        empleado_id = int(empleado_str.split("-")[0].strip())
        
        # Obtener datos del empleado
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT nombre, apellidos, salario 
            FROM empleados 
            WHERE id = ?
            ''', (empleado_id,))
            
            empleado = cursor.fetchone()
            if not empleado:
                messagebox.showerror("Error", "Empleado no encontrado")
                return
            
            nombre_completo = f"{empleado[0]} {empleado[1]}"
            salario = float(empleado[2])
            
            # Confirmar monto del pago
            monto = salario
            concepto = f"Pago de salario a {nombre_completo}"
            
            # Verificar saldo disponible
            cursor.execute('''
            SELECT saldo_actual FROM finanzas 
            ORDER BY id DESC LIMIT 1
            ''')
            
            saldo_actual = cursor.fetchone()[0]
            
            if saldo_actual < monto:
                messagebox.showerror("Error", "Saldo insuficiente para realizar el pago")
                return
            
            # Registrar pago en la tabla de pagos
            fecha_pago = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
            INSERT INTO pagos_empleados (empleado_id, fecha, monto, concepto)
            VALUES (?, ?, ?, ?)
            ''', (empleado_id, fecha_pago, monto, concepto))
            
            # Actualizar saldo en finanzas
            nuevo_saldo = saldo_actual - monto
            
            cursor.execute('''
            INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
            VALUES (?, ?, ?, ?, ?)
            ''', (fecha_pago, concepto, 0, monto, nuevo_saldo))
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Pago realizado exitosamente a {nombre_completo}\nMonto: ${monto:.2f}")
            
            # Actualizar gráfico
            self.actualizar_grafico_pagos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar pago: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    def actualizar_grafico_pagos(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            # Obtener últimos 10 pagos
            cursor.execute('''
                SELECT p.fecha, e.nombre || ' ' || e.apellidos as empleado, p.monto 
                FROM pagos_empleados p 
                JOIN empleados e ON p.empleado_id = e.id 
                ORDER BY p.fecha DESC 
                LIMIT 10
            ''')
            pagos = cursor.fetchall()
        
            # Limpiar gráfico actual
            self.ax_pagos.clear()
        
            if pagos:
                # Preparar datos para el gráfico
                fechas = [pago[0][:10] for pago in reversed(pagos)]  # Solo fecha, sin hora
                nombres = [pago[1] for pago in reversed(pagos)]
                montos = [pago[2] for pago in reversed(pagos)]
            
                # Crear gráfico de barras horizontales
                bars = self.ax_pagos.barh(nombres, montos, color='skyblue')
            
                # Configuración del gráfico
                self.ax_pagos.set_title('Últimos Pagos Realizados', pad=20)
                self.ax_pagos.set_xlabel('Monto ($)')
                self.ax_pagos.set_ylabel('Empleado')
            
                # Añadir etiquetas con valores
                for bar in bars:
                    width = bar.get_width()
                    self.ax_pagos.text(width + 100, bar.get_y() + bar.get_height()/2,
                                    f"${width:,.2f}",
                                    va='center', ha='left', fontsize=9)
            
                # Ajustar diseño
                self.ax_pagos.grid(axis='x', linestyle='--', alpha=0.7)
                self.figure_pagos.tight_layout()
            else:
                self.ax_pagos.text(0.5, 0.5, "No hay pagos registrados", 
                                horizontalalignment='center',
                                verticalalignment='center',
                                transform=self.ax_pagos.transAxes)
        
            # Actualizar canvas
            self.canvas_pagos.draw()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos de pagos: {str(e)}")
        finally:
            conn.close()

    def generar_usuario_unico(self, nombre, apellidos):
        """Genera un nombre de usuario único basado en el nombre y apellidos"""
        base_user = nombre[0].lower() + apellidos.lower().replace(" ", "")
        username = base_user
        counter = 1
        
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            while True:
                cursor.execute("SELECT 1 FROM usuarios WHERE username = ?", (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_user}{counter}"
                counter += 1
        finally:
            conn.close()
            
        return username

    def generar_contraseña_unica(self):
        """Genera una contraseña aleatoria segura"""
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(caracteres) for i in range(10))
    
# ==================== MÓDULO DE FINANZAS ====================
    
    def mostrar_modulo_finanzas(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar fondo general
        self.root.configure(bg='#e6ecf0')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#e6ecf0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Barra superior
        top_frame = tk.Frame(main_frame, bg='white', bd=2, relief='ridge')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", 
                           command=self.mostrar_menu_principal,
                           bg='#003366', fg='white',
                           font=('Arial', 10, 'bold'),
                           relief='flat', activebackground='#002244')
        back_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Título
        tk.Label(top_frame, text="Módulo de Finanzas", 
                font=("Arial", 16, "bold"), fg='#003366', bg='white').pack(side=tk.LEFT, padx=10)
        
        # Frame de pestañas
        tab_style = ttk.Style()
        tab_style.configure('TNotebook', background='#e6ecf0')
        tab_style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
        
        tab_control = ttk.Notebook(main_frame)
        
        # Pestaña Resumen
        tab_resumen = ttk.Frame(tab_control)
        tab_control.add(tab_resumen, text="Resumen")
        self.setup_tab_resumen_finanzas(tab_resumen)
        
        # Pestaña Transacciones
        tab_transacciones = ttk.Frame(tab_control)
        tab_control.add(tab_transacciones, text="Transacciones")
        self.setup_tab_transacciones(tab_transacciones)
        
        # Pestaña Informes
        tab_informes = ttk.Frame(tab_control)
        tab_control.add(tab_informes, text="Informes")
        self.setup_tab_informes_finanzas(tab_informes)
        
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)
    
    def setup_tab_resumen_finanzas(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='white', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame superior para información de saldo
        info_frame = tk.Frame(frame, bg='white')
        info_frame.pack(fill=tk.X, pady=20, padx=10)
        
        # Obtener saldo actual
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
            saldo = cursor.fetchone()[0]
            
            # Mostrar saldo
            tk.Label(info_frame, text="Saldo Actual:", 
                    font=("Arial", 14), bg='white', fg='#003366').pack(side=tk.LEFT, padx=10)
            
            self.saldo_label = tk.Label(info_frame, text=f"${saldo:,.2f}", 
                                      font=("Arial", 16, "bold"), bg='white', fg='#003366')
            self.saldo_label.pack(side=tk.LEFT, padx=10)
            
            # Botón para refrescar
            tk.Button(info_frame, text="Refrescar", command=self.actualizar_saldo,
                     bg='#003366', fg='white', font=('Arial', 10, 'bold'),
                     relief='flat', activebackground='#002244').pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar saldo: {str(e)}")
        finally:
            conn.close()
        
        # Frame para gráfico
        grafico_frame = tk.Frame(frame, bg='white')
        grafico_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Crear figura para el gráfico
        figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor='white')
        self.ax_finanzas = figure.add_subplot(111)
        self.ax_finanzas.set_facecolor('white')
        
        # Configurar colores del gráfico
        self.ax_finanzas.spines['bottom'].set_color('#003366')
        self.ax_finanzas.spines['top'].set_color('#003366') 
        self.ax_finanzas.spines['right'].set_color('#003366')
        self.ax_finanzas.spines['left'].set_color('#003366')
        self.ax_finanzas.tick_params(axis='x', colors='#003366')
        self.ax_finanzas.tick_params(axis='y', colors='#003366')
        self.ax_finanzas.yaxis.label.set_color('#003366')
        self.ax_finanzas.xaxis.label.set_color('#003366')
        self.ax_finanzas.title.set_color('#003366')
        
        # Canvas para el gráfico
        self.canvas_finanzas = FigureCanvasTkAgg(figure, grafico_frame)
        self.canvas_finanzas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Cargar datos para el gráfico
        self.actualizar_grafico_finanzas()
    
    def setup_tab_transacciones(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='white', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Controles superiores
        controls_frame = tk.Frame(frame, bg='white')
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Configurar estilo para combobox
        style = ttk.Style()
        style.configure('TCombobox', fieldbackground='white', background='white')
        
        # Frame para filtros
        filter_frame = tk.Frame(frame, bg='white')
        filter_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Filtro por tipo de transacción
        tk.Label(filter_frame, text="Filtrar por:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.filtro_transaccion = ttk.Combobox(filter_frame, values=["Ver todo", "Ingresos", "Egresos"], width=15)
        self.filtro_transaccion.pack(side=tk.LEFT, padx=5)
        self.filtro_transaccion.set("Ver todo")
        self.filtro_transaccion.bind("<<ComboboxSelected>>", lambda e: self.cargar_transacciones())
        
        # Opciones de transacción
        tk.Label(controls_frame, text="Tipo:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.tipo_transaccion = ttk.Combobox(controls_frame, values=["Ingreso", "Egreso"], width=15)
        self.tipo_transaccion.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Concepto:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.concepto_transaccion = tk.Entry(controls_frame, width=30, relief='solid', bd=1)
        self.concepto_transaccion.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Monto:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.monto_transaccion = tk.Entry(controls_frame, width=15, relief='solid', bd=1)
        self.monto_transaccion.pack(side=tk.LEFT, padx=5)
        
        # Botón para registrar
        tk.Button(controls_frame, text="Registrar", command=self.registrar_transaccion,
                bg='#003366', fg='white', font=('Arial', 10, 'bold'),
                relief='flat', activebackground='#002244').pack(side=tk.RIGHT, padx=10)
        
        # Treeview para mostrar transacciones
        style = ttk.Style()
        style.configure("Treeview", 
                    background="white", 
                    foreground="#003366",
                    rowheight=25,
                    fieldbackground="white")
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#003366')])
        
        # Definir todas las columnas posibles
        self.all_columns = ("ID", "Fecha", "Concepto", "Ingreso", "Egreso", "Saldo")
        
        # Crear Treeview con todas las columnas
        self.tree_transacciones = ttk.Treeview(frame, columns=self.all_columns, show="headings", style="Treeview")
        
        # Configurar encabezados y columnas
        self.tree_transacciones.heading("ID", text="ID", anchor='center')
        self.tree_transacciones.heading("Fecha", text="Fecha", anchor='center')
        self.tree_transacciones.heading("Concepto", text="Concepto", anchor='center')
        self.tree_transacciones.heading("Ingreso", text="Ingreso", anchor='center')
        self.tree_transacciones.heading("Egreso", text="Egreso", anchor='center')
        self.tree_transacciones.heading("Saldo", text="Saldo", anchor='center')
        
        self.tree_transacciones.column("ID", width=50, anchor='center')
        self.tree_transacciones.column("Fecha", width=120, anchor='center')
        self.tree_transacciones.column("Concepto", width=300, anchor='w', stretch=tk.YES)
        self.tree_transacciones.column("Ingreso", width=100, anchor='center')
        self.tree_transacciones.column("Egreso", width=100, anchor='center')
        self.tree_transacciones.column("Saldo", width=120, anchor='center')
        
        # Configurar tags para colores de fila
        self.tree_transacciones.tag_configure('ingreso', background='#e6f7e6')
        self.tree_transacciones.tag_configure('egreso', background='#ffe6e6')
        
        # Tooltip para concepto
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip_label = tk.Label(self.tooltip, text="", background="lightyellow", 
                                    relief="solid", borderwidth=1, wraplength=300)
        self.tooltip_label.pack()
        
        def show_tooltip(event):
            item = self.tree_transacciones.identify_row(event.y)
            col = self.tree_transacciones.identify_column(event.x)
            if item and col == "#3":  # Columna Concepto
                x, y, _, _ = self.tree_transacciones.bbox(item, col)
                x += event.x_root - event.x
                y += event.y_root - event.y + 20
                texto = self.tree_transacciones.item(item, "values")[2]
                self.tooltip_label.config(text=texto)
                self.tooltip.geometry(f"+{x}+{y}")
                self.tooltip.deiconify()
        
        def hide_tooltip(event):
            self.tooltip.withdraw()
        
        self.tree_transacciones.bind("<Motion>", show_tooltip)
        self.tree_transacciones.bind("<Leave>", hide_tooltip)
        
        self.tree_transacciones.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_transacciones.yview)
        self.tree_transacciones.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar datos iniciales
        self.cargar_transacciones()
    
    def setup_tab_informes_finanzas(self, parent):
        # Frame principal
        frame = tk.Frame(parent, bg='white', bd=2, relief='ridge')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Opciones para generar informes
        options_frame = tk.Frame(frame, bg='white')
        options_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Selector de tipo de informe
        tk.Label(options_frame, text="Tipo de Informe:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.tipo_informe = ttk.Combobox(options_frame, 
                                       values=["Ingresos y Egresos", "Ventas por Ruta", "Gastos por Categoría"], 
                                       width=20)
        self.tipo_informe.pack(side=tk.LEFT, padx=5)
        
        # Fechas
        tk.Label(options_frame, text="Desde:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.fecha_desde = DateEntry(options_frame, width=12, 
                                   background='#003366', foreground='white', 
                                   borderwidth=2, font=('Arial', 10))
        self.fecha_desde.pack(side=tk.LEFT, padx=5)
        
        tk.Label(options_frame, text="Hasta:", bg='white', fg='#003366').pack(side=tk.LEFT, padx=5)
        self.fecha_hasta = DateEntry(options_frame, width=12, 
                                   background='#003366', foreground='white', 
                                   borderwidth=2, font=('Arial', 10))
        self.fecha_hasta.pack(side=tk.LEFT, padx=5)
        
        # Botón para generar
        tk.Button(options_frame, text="Generar Informe", command=self.generar_informe_finanzas,
                bg='#003366', fg='white', font=('Arial', 10, 'bold'),
                relief='flat', activebackground='#002244').pack(side=tk.RIGHT, padx=10)
        
        # Frame para resultado
        self.resultado_frame = tk.Frame(frame, bg='white')
        self.resultado_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
    
    def actualizar_saldo(self):
        # Actualizar el saldo mostrado
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
            saldo = cursor.fetchone()[0]
            self.saldo_label.config(text=f"${saldo:,.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar saldo: {str(e)}")
        finally:
            conn.close()
    
    def actualizar_grafico_finanzas(self):
        # Obtener datos de transacciones recientes
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            # Obtener últimas 10 transacciones
            cursor.execute('''
            SELECT fecha, ingreso, egreso, saldo_actual
            FROM finanzas
            ORDER BY id DESC
            LIMIT 10
            ''')
            
            transacciones = cursor.fetchall()
            
            # Preparar datos para el gráfico
            fechas = []
            saldos = []
            
            for transaccion in reversed(transacciones):  # Invertir para orden cronológico
                fechas.append(transaccion[0][:10])  # Solo la fecha, sin la hora
                saldos.append(transaccion[3])
            
            # Limpiar gráfico actual
            self.ax_finanzas.clear()
            
            # Si hay datos, crear el gráfico
            if transacciones:
                # Gráfico principal (manteniendo tus estilos exactos)
                self.ax_finanzas.plot(fechas, saldos, 'o-', linewidth=2, color='#003366')
                
                # Configuración de ejes (sin rotación)
                self.ax_finanzas.set_title('Evolución del Saldo', color='#003366')
                self.ax_finanzas.set_xlabel('Fecha', color='#003366')
                self.ax_finanzas.set_ylabel('Saldo ($)', color='#003366')
                self.ax_finanzas.tick_params(axis='x', colors='#003366')
                self.ax_finanzas.tick_params(axis='y', colors='#003366')
                self.ax_finanzas.grid(True, color='#e6ecf0')
                
                # Formatear eje Y como moneda (mejora simple pero útil)
                self.ax_finanzas.yaxis.set_major_formatter('${x:,.0f}')
                
            else:
                self.ax_finanzas.text(0.5, 0.5, "No hay transacciones registradas", 
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    transform=self.ax_finanzas.transAxes,
                                    color='#003366')
            
            # Ajustar layout automáticamente
            plt.tight_layout()
            
            # Actualizar canvas
            self.canvas_finanzas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos financieros: {str(e)}")
        finally:
            conn.close()
    
    def registrar_transaccion(self):
        # Validar datos
        tipo = self.tipo_transaccion.get()
        concepto = self.concepto_transaccion.get()
        monto_str = self.monto_transaccion.get()
        
        if not tipo or not concepto or not monto_str:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
        
        try:
            monto = float(monto_str)
            if monto <= 0:
                messagebox.showwarning("Advertencia", "El monto debe ser mayor a cero")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            return
        
        # Registrar transacción
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            # Obtener último saldo
            cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
            resultado = cursor.fetchone()
            saldo_actual = resultado[0] if resultado else 0.0
            
            # Calcular nuevo saldo
            if tipo == "Ingreso":
                ingreso = monto
                egreso = 0.0
                nuevo_saldo = saldo_actual + monto
            else:  # Egreso
                if saldo_actual < monto:
                    messagebox.showerror("Error", "Saldo insuficiente para realizar esta transacción")
                    return
                ingreso = 0.0
                egreso = monto
                nuevo_saldo = saldo_actual - monto
            
            # Insertar transacción
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
                VALUES (?, ?, ?, ?, ?)
            ''', (fecha, concepto, ingreso, egreso, nuevo_saldo))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Transacción registrada exitosamente")
            
            # Limpiar campos
            self.tipo_transaccion.set("")
            self.concepto_transaccion.delete(0, tk.END)
            self.monto_transaccion.delete(0, tk.END)
            
            # Actualizar vista
            self.cargar_transacciones()
            self.actualizar_saldo()
            self.actualizar_grafico_finanzas()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al registrar transacción: {str(e)}")
        finally:
            conn.close()
        
    def cargar_transacciones(self):
        # Limpiar treeview
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)
        
        # Determinar filtro
        filtro = self.filtro_transaccion.get()
        
        # Configurar columnas visibles según filtro
        if filtro == "Ingresos":
            visible_columns = ("ID", "Fecha", "Concepto", "Ingreso", "Saldo")
        elif filtro == "Egresos":
            visible_columns = ("ID", "Fecha", "Concepto", "Egreso", "Saldo")
        else:  # Ver todo
            visible_columns = ("ID", "Fecha", "Concepto", "Ingreso", "Egreso", "Saldo")
        
        # Configurar columnas visibles
        self.tree_transacciones["displaycolumns"] = visible_columns
        
        # Obtener datos de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            # Consulta optimizada que calcula correctamente el saldo acumulado
            query = '''
            SELECT 
                f.id,
                f.fecha,
                f.concepto,
                f.ingreso,
                f.egreso,
                f.saldo_actual
            FROM finanzas f
            '''
            
            if filtro == "Ingresos":
                query += ' WHERE f.ingreso > 0'
            elif filtro == "Egresos":
                query += ' WHERE f.egreso > 0'
            
            query += ' ORDER BY f.id DESC LIMIT 100'
            
            cursor.execute(query)
            transacciones = cursor.fetchall()
            
            for row in transacciones:
                # Formatear valores
                fecha = row[1].split()[0] if ' ' in row[1] else row[1]
                
                # Crear diccionario con todos los valores posibles
                valores = (
                    row[0],  # ID
                    fecha,   # Fecha
                    row[2],  # Concepto
                    f"${row[3]:,.2f}" if row[3] > 0 else "",  # Ingreso
                    f"${row[4]:,.2f}" if row[4] > 0 else "",  # Egreso
                    f"${row[5]:,.2f}" if row[5] is not None else "$0.00"  # Saldo
                )
                
                # Determinar estilo de fila
                tags = ('ingreso',) if row[3] > 0 else ('egreso',) if row[4] > 0 else ()
                
                # Insertar fila con todos los valores (el Treeview mostrará solo las columnas visibles)
                self.tree_transacciones.insert("", tk.END, values=valores, tags=tags)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar transacciones: {str(e)}")
        finally:
            conn.close()

    
    def generar_informe_finanzas(self):
        # Limpiar frame de resultados
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
        
        # Validar datos
        tipo_informe = self.tipo_informe.get()
        fecha_desde = self.fecha_desde.get_date()
        fecha_hasta = self.fecha_hasta.get_date()
        
        if not tipo_informe:
            messagebox.showwarning("Advertencia", "Debe seleccionar un tipo de informe")
            return
        
        if fecha_hasta < fecha_desde:
            messagebox.showwarning("Advertencia", "La fecha final debe ser posterior a la fecha inicial")
            return
        
        # Convertir fechas a strings para SQL
        fecha_desde_str = fecha_desde.strftime("%Y-%m-%d")
        fecha_hasta_str = fecha_hasta.strftime("%Y-%m-%d 23:59:59")
        
        # Generar informe según tipo
        if tipo_informe == "Ingresos y Egresos":
            self.generar_informe_ingresos_egresos(fecha_desde_str, fecha_hasta_str)
        elif tipo_informe == "Ventas por Ruta":
            self.generar_informe_ventas_ruta(fecha_desde_str, fecha_hasta_str)
        elif tipo_informe == "Gastos por Categoría":
            self.generar_informe_gastos_categoria(fecha_desde_str, fecha_hasta_str)
    
    def generar_informe_ingresos_egresos(self, fecha_desde, fecha_hasta):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            # Obtener total de ingresos y egresos
            cursor.execute('''
            SELECT SUM(ingreso), SUM(egreso)
            FROM finanzas
            WHERE fecha BETWEEN ? AND ?
            ''', (fecha_desde, fecha_hasta))
            
            totales = cursor.fetchone()
            total_ingresos = totales[0] or 0
            total_egresos = totales[1] or 0
            
            # Crear tabla resumen
            tk.Label(self.resultado_frame, text="Resumen de Ingresos y Egresos", 
                    font=("Arial", 14, "bold"), bg='white', fg='#003366').pack(pady=10)
            
            tabla_frame = tk.Frame(self.resultado_frame, bg='white')
            tabla_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(tabla_frame, text="Total Ingresos:", 
                    font=("Arial", 12), bg='white', fg='#003366').grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(tabla_frame, text=f"${total_ingresos:,.2f}", 
                    font=("Arial", 12), bg='white', fg='#003366').grid(row=0, column=1, padx=10, pady=5)
            
            tk.Label(tabla_frame, text="Total Egresos:", 
                    font=("Arial", 12), bg='white', fg='#003366').grid(row=1, column=0, padx=10, pady=5, sticky="w")
            tk.Label(tabla_frame, text=f"${total_egresos:,.2f}", 
                    font=("Arial", 12), bg='white', fg='#003366').grid(row=1, column=1, padx=10, pady=5)
            
            tk.Label(tabla_frame, text="Balance:", 
                    font=("Arial", 12, "bold"), bg='white', fg='#003366').grid(row=2, column=0, padx=10, pady=5, sticky="w")
            balance = total_ingresos - total_egresos
            balance_color = "green" if balance >= 0 else "red"
            tk.Label(tabla_frame, text=f"${balance:,.2f}", 
                    font=("Arial", 12, "bold"), bg='white', fg=balance_color).grid(row=2, column=1, padx=10, pady=5)
            
            # Crear gráfico
            figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor='white')
            ax = figure.add_subplot(111)
            ax.set_facecolor('white')
            
            # Configurar colores del gráfico
            ax.spines['bottom'].set_color('#003366')
            ax.spines['top'].set_color('#003366') 
            ax.spines['right'].set_color('#003366')
            ax.spines['left'].set_color('#003366')
            ax.tick_params(axis='x', colors='#003366')
            ax.tick_params(axis='y', colors='#003366')
            ax.yaxis.label.set_color('#003366')
            ax.xaxis.label.set_color('#003366')
            ax.title.set_color('#003366')
            
            labels = ['Ingresos', 'Egresos']
            values = [total_ingresos, total_egresos]
            colors = ['#4CAF50', '#F44336']  # Verde y rojo
            
            ax.bar(labels, values, color=colors)
            ax.set_title('Ingresos vs Egresos', color='#003366')
            ax.set_ylabel('Monto ($)', color='#003366')
            ax.grid(True, color='#e6ecf0')
            
            # Agregar etiquetas con valores
            for i, v in enumerate(values):
                ax.text(i, v + 0.1, f"${v:,.2f}", ha='center', color='#003366')
            
            canvas = FigureCanvasTkAgg(figure, self.resultado_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
        finally:
            conn.close()
    
    def generar_informe_ventas_ruta(self, fecha_desde, fecha_hasta):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        
        try:
            # Obtener ventas por ruta
            cursor.execute('''
            SELECT r.origen || ' - ' || r.destino as ruta, COUNT(b.id) as total_boletos, SUM(b.precio) as total_ventas
            FROM boletos b
            JOIN horarios h ON b.horario_id = h.id
            JOIN rutas r ON h.ruta_id = r.id
            WHERE b.fecha_compra BETWEEN ? AND ?
            GROUP BY r.id
            ORDER BY total_ventas DESC
            ''', (fecha_desde, fecha_hasta))
            
            ventas_ruta = cursor.fetchall()
            
            # Crear tabla resumen
            tk.Label(self.resultado_frame, text="Ventas por Ruta", 
                    font=("Arial", 14, "bold"), bg='white', fg='#003366').pack(pady=10)
            
            if not ventas_ruta:
                tk.Label(self.resultado_frame, text="No hay ventas registradas en este período",
                        bg='white', fg='#003366').pack(pady=20)
                return
            
            # Crear treeview
            style = ttk.Style()
            style.configure("Treeview", 
                          background="white", 
                          foreground="#003366",
                          rowheight=25,
                          fieldbackground="white")
            style.map('Treeview', background=[('selected', '#003366')])
            
            columns = ("Ruta", "Total Boletos", "Total Ventas")
            tree = ttk.Treeview(self.resultado_frame, columns=columns, show="headings", style="Treeview")
            
            # Configurar columnas
            for col in columns:
                tree.heading(col, text=col, anchor='center')
                tree.column(col, width=150, anchor='center')
            
            # Insertar datos
            for row in ventas_ruta:
                tree.insert("", tk.END, values=(row[0], row[1], f"${row[2]:,.2f}"))
            
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Crear gráfico
            figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor='white')
            ax = figure.add_subplot(111)
            ax.set_facecolor('white')
            
            # Configurar colores del gráfico
            ax.spines['bottom'].set_color('#003366')
            ax.spines['top'].set_color('#003366') 
            ax.spines['right'].set_color('#003366')
            ax.spines['left'].set_color('#003366')
            ax.tick_params(axis='x', colors='#003366')
            ax.tick_params(axis='y', colors='#003366')
            ax.yaxis.label.set_color('#003366')
            ax.xaxis.label.set_color('#003366')
            ax.title.set_color('#003366')
            
            rutas = [row[0] for row in ventas_ruta]
            ventas = [row[2] for row in ventas_ruta]
            
            # Limitar a las 5 rutas con más ventas para el gráfico
            if len(rutas) > 5:
                rutas = rutas[:5]
                ventas = ventas[:5]
            
            bars = ax.bar(rutas, ventas, color='#003366')
            ax.set_title('Top Ventas por Ruta', color='#003366')
            ax.set_ylabel('Ventas ($)', color='#003366')
            ax.set_xlabel('Ruta', color='#003366')
            ax.grid(True, color='#e6ecf0')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color='#003366')
            
            # Agregar etiquetas con valores
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', color='#003366')
            
            canvas = FigureCanvasTkAgg(figure, self.resultado_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
        finally:
            conn.close()

    def generar_informe_gastos_categoria(self, fecha_desde, fecha_hasta):
        """Genera un informe de gastos por categoría"""
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            # Obtener gastos por categoría
            cursor.execute('''
                SELECT tipo_producto, SUM(total) as total
                FROM compras
                WHERE fecha BETWEEN ? AND ?
                GROUP BY tipo_producto
                ORDER BY total DESC
            ''', (fecha_desde, fecha_hasta))
            resultados = cursor.fetchall()
        
            # Limpiar frame de resultados
            for widget in self.resultado_frame.winfo_children():
                widget.destroy()
            
            if not resultados:
                tk.Label(self.resultado_frame, text="No hay gastos registrados en este período",
                        bg='white', fg='#003366').pack(pady=20)
                return
            
            # Crear tabla resumen
            tk.Label(self.resultado_frame, text="Gastos por Categoría", 
                    font=("Arial", 14, "bold"), bg='white', fg='#003366').pack(pady=10)
        
            tabla_frame = tk.Frame(self.resultado_frame, bg='white')
            tabla_frame.pack(fill=tk.X, pady=10)
        
            # Encabezados
            tk.Label(tabla_frame, text="Categoría", 
                    font=("Arial", 12, "bold"), bg='white', fg='#003366').grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(tabla_frame, text="Total", 
                    font=("Arial", 12, "bold"), bg='white', fg='#003366').grid(row=0, column=1, padx=10, pady=5)
        
            # Datos
            for i, row in enumerate(resultados, start=1):
                tk.Label(tabla_frame, text=row[0], bg='white', fg='#003366').grid(row=i, column=0, padx=10, pady=5, sticky="w")
                tk.Label(tabla_frame, text=f"${row[1]:,.2f}", bg='white', fg='#003366').grid(row=i, column=1, padx=10, pady=5)
        
            # Crear gráfico
            figure = plt.Figure(figsize=(6, 4), dpi=100, facecolor='white')
            ax = figure.add_subplot(111)
            ax.set_facecolor('white')
            
            # Configurar colores del gráfico
            ax.spines['bottom'].set_color('#003366')
            ax.spines['top'].set_color('#003366') 
            ax.spines['right'].set_color('#003366')
            ax.spines['left'].set_color('#003366')
            ax.tick_params(axis='x', colors='#003366')
            ax.tick_params(axis='y', colors='#003366')
            ax.yaxis.label.set_color('#003366')
            ax.xaxis.label.set_color('#003366')
            ax.title.set_color('#003366')
        
            categorias = [row[0] for row in resultados]
            montos = [row[1] for row in resultados]
        
            bars = ax.bar(categorias, montos, color='#F44336')
            ax.set_title('Gastos por Categoría', color='#003366')
            ax.set_ylabel('Monto ($)', color='#003366')
            ax.grid(True, color='#e6ecf0')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', color='#003366')
        
            # Agregar etiquetas con valores
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', color='#003366')
            
            canvas = FigureCanvasTkAgg(figure, self.resultado_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar informe: {str(e)}")
        finally:
            conn.close()

    def limpiar_ventana(self):
        """Elimina todos los widgets de la ventana principal"""
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==================== MÓDULO DE INVENTARIO ====================
    def mostrar_modulo_inventario(self):
        """Muestra la interfaz principal del módulo de inventario"""
        self.limpiar_ventana()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal).pack(side=tk.RIGHT)
        tk.Label(top_frame, text="Módulo de Inventario", font=("Arial", 16)).pack(side=tk.LEFT)
        
        # Pestañas
        tab_control = ttk.Notebook(main_frame)
        
        # Pestaña Autobuses
        tab_autobuses = ttk.Frame(tab_control)
        tab_control.add(tab_autobuses, text="Autobuses")
        self.setup_tab_autobuses(tab_autobuses)
        
        # Pestaña Computadoras
        tab_computadoras = ttk.Frame(tab_control)
        tab_control.add(tab_computadoras, text="Computadoras")
        self.setup_tab_computadoras(tab_computadoras)
        
        tab_control.pack(expand=1, fill="both")

    # ------ Autobuses ------
    def setup_tab_autobuses(self, parent):
        """Configura la pestaña de autobuses"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Controles
        controls_frame = tk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=10)
        tk.Button(controls_frame, text="Agregar Autobús", command=self.mostrar_formulario_autobus).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Refrescar", command=self.cargar_autobuses).pack(side=tk.LEFT, padx=5)
        
        # Tabla
        columns = ("ID", "Marca", "Modelo", "Año", "Capacidad", "Estado")
        self.tree_autobuses = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_autobuses.heading(col, text=col)
            self.tree_autobuses.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_autobuses.yview)
        self.tree_autobuses.configure(yscrollcommand=scrollbar.set)
        
        self.tree_autobuses.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cargar_autobuses()

    def mostrar_formulario_autobus(self):
        """Muestra el formulario para agregar un nuevo autobús"""
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Autobús")
        popup.geometry("400x300")
        
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
        
        # Campos del formulario
        tk.Label(frame, text="Marca:").grid(row=0, column=0, sticky="w", pady=5)
        marca_entry = tk.Entry(frame, width=30)
        marca_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(frame, text="Modelo:").grid(row=1, column=0, sticky="w", pady=5)
        modelo_entry = tk.Entry(frame, width=30)
        modelo_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(frame, text="Año:").grid(row=2, column=0, sticky="w", pady=5)
        año_entry = tk.Entry(frame, width=30)
        año_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(frame, text="Capacidad:").grid(row=3, column=0, sticky="w", pady=5)
        capacidad_entry = tk.Entry(frame, width=30)
        capacidad_entry.grid(row=3, column=1, pady=5)
        capacidad_entry.insert(0, "24")
        
        tk.Label(frame, text="Estado:").grid(row=4, column=0, sticky="w", pady=5)
        estado_combobox = ttk.Combobox(frame, values=["Nuevo", "Usado", "Mantenimiento", "Inactivo"], width=27)
        estado_combobox.grid(row=4, column=1, pady=5)
        estado_combobox.set("Nuevo")
        
        # Botón guardar
        tk.Button(frame, text="Guardar", command=lambda: self.guardar_autobus(
            marca_entry.get(),
            modelo_entry.get(),
            año_entry.get(),
            capacidad_entry.get(),
            estado_combobox.get(),
            popup
        )).grid(row=5, columnspan=2, pady=20)

    def guardar_autobus(self, marca, modelo, año, capacidad, estado, popup):
        """Guarda un nuevo autobús en la base de datos"""
        if not all([marca, modelo, año, capacidad, estado]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
        
        try:
            año_int = int(año)
            capacidad_int = int(capacidad)
        except ValueError:
            messagebox.showerror("Error", "Año y capacidad deben ser números")
            return
        
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO autobuses (marca, modelo, año, capacidad, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (marca, modelo, año_int, capacidad_int, estado))
            
            # Registrar transacción financiera
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            concepto = f"Compra de autobús {marca} {modelo}"
            precio = 2500000 if marca.lower() == "volvo" else 2000000
            
            cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
            saldo_actual = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
                VALUES (?, ?, ?, ?, ?)
            """, (fecha, concepto, 0, precio, saldo_actual - precio))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Autobús agregado correctamente")
            popup.destroy()
            self.cargar_autobuses()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar autobús: {str(e)}")
        finally:
            conn.close()

    def cargar_autobuses(self):
        """Carga los autobuses desde la base de datos al TreeView"""
        for item in self.tree_autobuses.get_children():
            self.tree_autobuses.delete(item)
        
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, marca, modelo, año, capacidad, estado FROM autobuses ORDER BY id")
            for row in cursor.fetchall():
                self.tree_autobuses.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar autobuses: {str(e)}")
        finally:
            conn.close()

    # ------ Computadoras ------
    def setup_tab_computadoras(self, parent):
        """Configura la pestaña de computadoras"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Controles
        controls_frame = tk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=10)
        tk.Button(controls_frame, text="Agregar Computadora", command=self.mostrar_formulario_computadora).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Refrescar", command=self.cargar_computadoras).pack(side=tk.LEFT, padx=5)
        
        # Tabla
        columns = ("ID", "Marca", "Modelo", "Asignado a", "Departamento", "Estado")
        self.tree_computadoras = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_computadoras.heading(col, text=col)
            self.tree_computadoras.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_computadoras.yview)
        self.tree_computadoras.configure(yscrollcommand=scrollbar.set)
        
        self.tree_computadoras.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cargar_computadoras()

    def mostrar_formulario_computadora(self):
        """Muestra el formulario para agregar una nueva computadora"""
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Computadora")
        popup.geometry("400x300")
        
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
        
        # Campos del formulario
        tk.Label(frame, text="Marca:").grid(row=0, column=0, sticky="w", pady=5)
        marca_entry = tk.Entry(frame, width=30)
        marca_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(frame, text="Modelo:").grid(row=1, column=0, sticky="w", pady=5)
        modelo_entry = tk.Entry(frame, width=30)
        modelo_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(frame, text="Asignado a:").grid(row=2, column=0, sticky="w", pady=5)
        asignado_entry = tk.Entry(frame, width=30)
        asignado_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(frame, text="Departamento:").grid(row=3, column=0, sticky="w", pady=5)
        depto_entry = tk.Entry(frame, width=30)
        depto_entry.grid(row=3, column=1, pady=5)
        
        tk.Label(frame, text="Estado:").grid(row=4, column=0, sticky="w", pady=5)
        estado_combobox = ttk.Combobox(frame, values=["Nuevo", "Usado", "Mantenimiento", "Inactivo"], width=27)
        estado_combobox.grid(row=4, column=1, pady=5)
        estado_combobox.set("Nuevo")
        
        # Botón guardar
        tk.Button(frame, text="Guardar", command=lambda: self.guardar_computadora(
            marca_entry.get(),
            modelo_entry.get(),
            asignado_entry.get(),
            depto_entry.get(),
            estado_combobox.get(),
            popup
        )).grid(row=5, columnspan=2, pady=20)

    def guardar_computadora(self, marca, modelo, asignado_a, departamento, estado, popup):
        """Guarda una nueva computadora en la base de datos"""
        if not all([marca, modelo, estado]):
            messagebox.showwarning("Advertencia", "Marca, modelo y estado son obligatorios")
            return
        
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO computadoras (marca, modelo, asignado_a, departamento, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (marca, modelo, asignado_a, departamento, estado))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Computadora agregada correctamente")
            popup.destroy()
            self.cargar_computadoras()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar computadora: {str(e)}")
        finally:
            conn.close()

    def cargar_computadoras(self):
        """Carga las computadoras desde la base de datos al TreeView"""
        for item in self.tree_computadoras.get_children():
            self.tree_computadoras.delete(item)
        
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, marca, modelo, asignado_a, departamento, estado
                FROM computadoras
                ORDER BY id
            """)
            for row in cursor.fetchall():
                self.tree_computadoras.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar computadoras: {str(e)}")
        finally:
            conn.close()

# =================== MÓDULO DE COMPRAS ================================
    def mostrar_modulo_compras(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
    
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal)
        back_btn.pack(side=tk.RIGHT)
    
        # Título
        tk.Label(top_frame, text="Módulo de Compras", font=("Arial", 16)).pack(side=tk.LEFT)
    
        # Frame de pestañas
        tab_control = ttk.Notebook(main_frame)
    
        # Pestaña Registrar Compra
        tab_registrar = tk.Frame(tab_control)
        tab_control.add(tab_registrar, text="Registrar Compra")
        self.setup_tab_registrar_compra(tab_registrar)
    
        # Pestaña Historial
        tab_historial = tk.Frame(tab_control)
        tab_control.add(tab_historial, text="Historial")
        self.setup_tab_historial_compras(tab_historial)
    
        tab_control.pack(expand=1, fill="both")

    def setup_tab_registrar_compra(self, parent):
        # Frame principal
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Título
        tk.Label(frame, text="Registrar Nueva Compra", font=("Arial", 14)).pack(pady=10)
    
        # Formulario
        form_frame = tk.Frame(frame)
        form_frame.pack(pady=10)
    
        # Proveedor
        tk.Label(form_frame, text="Proveedor:").grid(row=0, column=0, sticky="w", pady=5)
        self.proveedor_combobox = ttk.Combobox(form_frame, width=27)
        self.proveedor_combobox.grid(row=0, column=1, pady=5)
    
        # Tipo de producto
        tk.Label(form_frame, text="Tipo de Producto:").grid(row=1, column=0, sticky="w", pady=5)
        self.tipo_producto_combobox = ttk.Combobox(form_frame, values=["Autobús", "Computadora", "Productos de limpieza", "Otros"], width=27)
        self.tipo_producto_combobox.grid(row=1, column=1, pady=5)
    
        # Descripción
        tk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky="w", pady=5)
        self.descripcion_compra_entry = tk.Entry(form_frame, width=30)
        self.descripcion_compra_entry.grid(row=2, column=1, pady=5)
    
        # Cantidad
        tk.Label(form_frame, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=5)
        self.cantidad_compra_entry = tk.Entry(form_frame, width=30)
        self.cantidad_compra_entry.grid(row=3, column=1, pady=5)
    
        # Precio unitario
        tk.Label(form_frame, text="Precio Unitario:").grid(row=4, column=0, sticky="w", pady=5)
        self.precio_unitario_entry = tk.Entry(form_frame, width=30)
        self.precio_unitario_entry.grid(row=4, column=1, pady=5)
    
        # Total (calculado automáticamente)
        tk.Label(form_frame, text="Total:").grid(row=5, column=0, sticky="w", pady=5)
        self.total_compra_label = tk.Label(form_frame, text="$0.00")
        self.total_compra_label.grid(row=5, column=1, pady=5, sticky="w")
    
        # Botón para calcular total
        tk.Button(form_frame, text="Calcular Total", command=self.calcular_total_compra).grid(row=6, column=1, pady=5, sticky="e")
    
        # Botón para registrar compra
        tk.Button(frame, text="Registrar Compra", command=self.registrar_compra).pack(pady=20)
    
        # Cargar proveedores en el combobox
        self.cargar_proveedores_combobox()

    def calcular_total_compra(self):
        try:
            cantidad = int(self.cantidad_compra_entry.get())
            precio_unitario = float(self.precio_unitario_entry.get())
            total = cantidad * precio_unitario
            self.total_compra_label.config(text=f"${total:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")

    def cargar_proveedores_combobox(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
            proveedores = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
            self.proveedor_combobox['values'] = proveedores
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
        finally:
            conn.close()

    def registrar_compra(self):
    # Validar datos
        proveedor = self.proveedor_combobox.get()
        tipo_producto = self.tipo_producto_combobox.get()
        descripcion = self.descripcion_compra_entry.get()  # Asegúrate que este Entry se llama así
        cantidad_str = self.cantidad_compra_entry.get()
        precio_str = self.precio_unitario_entry.get()
    
        if not all([proveedor, tipo_producto, descripcion, cantidad_str, precio_str]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
    
        try:
            proveedor_id = int(proveedor.split("-")[0].strip())
            cantidad = int(cantidad_str)
            precio_unitario = float(precio_str)
            total = cantidad * precio_unitario
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")
            return

    # Insertar en la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
            # CORRECCIÓN AQUÍ: usar descripcion en lugar de description
            cursor.execute("""
                INSERT INTO compras (fecha, proveedor_id, tipo_producto, descripcion, cantidad, precio_unitario, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (fecha, proveedor_id, tipo_producto, descripcion, cantidad, precio_unitario, total))
        
        # Resto del código para registrar en finanzas...
        
            # Registrar en finanzas (egreso)
            cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
            saldo_actual = cursor.fetchone()[0]
        
            concepto = f"Compra de {tipo_producto}: {descripcion}"
        
            cursor.execute("""
                INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
                VALUES (?, ?, ?, ?, ?)
            """, (fecha, concepto, 0, total, saldo_actual - total))
        
            # Si es autobús o computadora, agregar al inventario
            if tipo_producto == "Autobús":
                # Extraer marca y modelo de la descripción (esto es un ejemplo simplificado)
                partes = descripcion.split()
                marca = partes[0] if len(partes) > 0 else "Desconocida"
                modelo = partes[1] if len(partes) > 1 else "Desconocido"
            
                cursor.execute("""
                    INSERT INTO autobuses (marca, modelo, año, capacidad, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (marca, modelo, datetime.datetime.now().year, 24, "Nuevo"))
        
            elif tipo_producto == "Computadora":
                # Extraer marca y modelo de la descripción
                partes = descripcion.split()
                marca = partes[0] if len(partes) > 0 else "Desconocida"
                modelo = partes[1] if len(partes) > 1 else "Desconocido"
            
                cursor.execute("""
                    INSERT INTO computadoras (marca, modelo, asignado_a, departamento, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (marca, modelo, "", "", "Nuevo"))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Compra registrada correctamente")
        
            # Limpiar formulario
            self.proveedor_combobox.set("")
            self.tipo_producto_combobox.set("")
            self.descripcion_compra_entry.delete(0, tk.END)
            self.cantidad_compra_entry.delete(0, tk.END)
            self.precio_unitario_entry.delete(0, tk.END)
            self.total_compra_label.config(text="$0.00")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar compra: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def setup_tab_historial_compras(self, parent):
        # Frame principal
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Controles superiores
        controls_frame = tk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=10)
    
        # Botón para refrescar
        tk.Button(controls_frame, text="Refrescar", command=lambda: self.cargar_historial_compras(self.tree_compras)).pack(side=tk.LEFT, padx=5)
    
        # Treeview para mostrar compras
        columns = ("ID", "Fecha", "Proveedor", "Tipo", "Descripción", "Cantidad", "Precio Unitario", "Total")
        self.tree_compras = ttk.Treeview(frame, columns=columns, show="headings")
    
        # Configurar columnas
        for col in columns:
            self.tree_compras.heading(col, text=col)
            self.tree_compras.column(col, width=100)
    
        self.tree_compras.pack(fill=tk.BOTH, expand=True, pady=10)
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_compras.yview)
        self.tree_compras.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Cargar datos
        self.cargar_historial_compras(self.tree_compras)

    def cargar_historial_compras(self, tree):
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
    
        # Cargar compras de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.id, c.fecha, p.nombre, c.tipo_producto, c.descripcion, c.cantidad, c.precio_unitario, c.total 
                FROM compras c 
                JOIN proveedores p ON c.proveedor_id = p.id 
                ORDER BY c.fecha DESC 
                LIMIT 100 
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(
                    row[0], 
                    row[1], 
                    row[2], 
                    row[3], 
                    row[4], 
                    row[5], 
                    f"${row[6]:.2f}", 
                    f"${row[7]:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial de compras: {str(e)}")
        finally:
            conn.close()

# =================== MÓDULO DE PROVEEDORES ============================
    def mostrar_modulo_proveedores(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
    
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal)
        back_btn.pack(side=tk.RIGHT)
    
        # Título
        tk.Label(top_frame, text="Módulo de Proveedores", font=("Arial", 16)).pack(side=tk.LEFT)
    
        # Frame de contenido
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Controles superiores
        controls_frame = tk.Frame(content_frame)
        controls_frame.pack(fill=tk.X, pady=10)
    
        # Botón para agregar proveedor
        tk.Button(controls_frame, text="Agregar Proveedor", command=self.mostrar_formulario_proveedor).pack(side=tk.LEFT, padx=5)
    
        # Botón para refrescar
        tk.Button(controls_frame, text="Refrescar", command=lambda: self.cargar_proveedores(self.tree_proveedores)).pack(side=tk.LEFT, padx=5)
    
        # Treeview para mostrar proveedores
        columns = ("ID", "Nombre", "Tipo", "Contacto", "Teléfono", "Email")
        self.tree_proveedores = ttk.Treeview(content_frame, columns=columns, show="headings")
    
        # Configurar columnas
        for col in columns:
            self.tree_proveedores.heading(col, text=col)
            self.tree_proveedores.column(col, width=120)
    
        self.tree_proveedores.pack(fill=tk.BOTH, expand=True, pady=10)
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree_proveedores.yview)
        self.tree_proveedores.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Cargar datos
        self.cargar_proveedores(self.tree_proveedores)

    def mostrar_formulario_proveedor(self):
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Proveedor")
        popup.geometry("400x300")
    
        # Frame principal
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
    
        # Campos del formulario
        tk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        nombre_entry = tk.Entry(frame, width=30)
        nombre_entry.grid(row=0, column=1, pady=5)
    
        tk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky="w", pady=5)
        tipo_combobox = ttk.Combobox(frame, values=["Autobuses", "Computadoras", "Productos de limpieza", "Otros"], width=27)
        tipo_combobox.grid(row=1, column=1, pady=5)
    
        tk.Label(frame, text="Contacto:").grid(row=2, column=0, sticky="w", pady=5)
        contacto_entry = tk.Entry(frame, width=30)
        contacto_entry.grid(row=2, column=1, pady=5)
    
        tk.Label(frame, text="Teléfono:").grid(row=3, column=0, sticky="w", pady=5)
        telefono_entry = tk.Entry(frame, width=30)
        telefono_entry.grid(row=3, column=1, pady=5)
    
        tk.Label(frame, text="Email:").grid(row=4, column=0, sticky="w", pady=5)
        email_entry = tk.Entry(frame, width=30)
        email_entry.grid(row=4, column=1, pady=5)
    
        # Botón para guardar
        tk.Button(frame, text="Guardar", command=lambda: self.guardar_proveedor(
            nombre_entry.get(),
            tipo_combobox.get(),
            contacto_entry.get(),
            telefono_entry.get(),
            email_entry.get(),
            popup
        )).grid(row=5, columnspan=2, pady=20)

    def guardar_proveedor(self, nombre, tipo, contacto, telefono, email, popup):
        # Validar datos
        if not nombre or not tipo:
            messagebox.showwarning("Advertencia", "Nombre y tipo son obligatorios")
            return
    
        # Insertar en la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                INSERT INTO proveedores (nombre, tipo, contacto, telefono, email)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, tipo, contacto, telefono, email))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Proveedor agregado correctamente")
            popup.destroy()
            self.cargar_proveedores(self.tree_proveedores)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar proveedor: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def cargar_proveedores(self, tree):
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
    
        # Cargar proveedores de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                SELECT id, nombre, tipo, contacto, telefono, email
                FROM proveedores
                ORDER BY nombre
            """)
        
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
        finally:
            conn.close()

# =================== MÓDULO DE VENTAS =================================
    def mostrar_modulo_ventas(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
    
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal)
        back_btn.pack(side=tk.RIGHT)
        
        # Botón de clientes
        clientes_btn = tk.Button(top_frame, text="Clientes", command=self.mostrar_clientes)
        clientes_btn.pack(side=tk.RIGHT, padx=5)
    
        # Título
        tk.Label(top_frame, text="Módulo de Ventas", font=("Arial", 16)).pack(side=tk.LEFT)
    
        # Frame de contenido
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Formulario para vender boletos
        form_frame = tk.Frame(content_frame)
        form_frame.pack(fill=tk.X, pady=10)
    
        # Campos del formulario
        tk.Label(form_frame, text="Nombre Pasajero:").grid(row=0, column=0, sticky="w", pady=5)
        self.nombre_pasajero_entry = tk.Entry(form_frame, width=30)
        self.nombre_pasajero_entry.grid(row=0, column=1, pady=5)
    
        tk.Label(form_frame, text="Apellidos Pasajero:").grid(row=1, column=0, sticky="w", pady=5)
        self.apellidos_pasajero_entry = tk.Entry(form_frame, width=30)
        self.apellidos_pasajero_entry.grid(row=1, column=1, pady=5)
    
        tk.Label(form_frame, text="Ruta:").grid(row=2, column=0, sticky="w", pady=5)
        self.ruta_combobox = ttk.Combobox(form_frame, width=27)
        self.ruta_combobox.grid(row=2, column=1, pady=5)
        self.ruta_combobox.bind("<<ComboboxSelected>>", self.actualizar_horarios_disponibles)
    
        tk.Label(form_frame, text="Horario:").grid(row=3, column=0, sticky="w", pady=5)
        self.horario_combobox = ttk.Combobox(form_frame, width=27)
        self.horario_combobox.grid(row=3, column=1, pady=5)
        self.horario_combobox.bind("<<ComboboxSelected>>", self.actualizar_asientos_disponibles)
    
        tk.Label(form_frame, text="Fecha de Viaje:").grid(row=4, column=0, sticky="w", pady=5)
        self.fecha_viaje_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_viaje_entry.grid(row=4, column=1, pady=5, sticky="w")
    
        tk.Label(form_frame, text="Asientos:").grid(row=5, column=0, sticky="w", pady=5)
        self.asientos_listbox = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, width=25, height=5, exportselection=False)
        self.asientos_listbox.grid(row=5, column=1, pady=5)
        self.asientos_listbox.bind('<<ListboxSelect>>', self.actualizar_cantidad_desde_asientos)
        
        # Frame para cantidad y precio
        cantidad_frame = tk.Frame(form_frame)
        cantidad_frame.grid(row=6, column=0, columnspan=2, pady=5)
        
        tk.Label(cantidad_frame, text="Cantidad:").pack(side=tk.LEFT)
        self.cantidad_spinbox = tk.Spinbox(cantidad_frame, from_=1, to=10, width=5, command=self.actualizar_asientos_desde_cantidad)
        self.cantidad_spinbox.pack(side=tk.LEFT, padx=5)
        self.cantidad_spinbox.bind("<KeyRelease>", self.actualizar_asientos_desde_cantidad)
        
        tk.Label(cantidad_frame, text="Precio Unitario:").pack(side=tk.LEFT, padx=(10,0))
        self.precio_unitario_label = tk.Label(cantidad_frame, text="$0.00")
        self.precio_unitario_label.pack(side=tk.LEFT)
        
        tk.Label(cantidad_frame, text="Total:").pack(side=tk.LEFT, padx=(10,0))
        self.precio_total_label = tk.Label(cantidad_frame, text="$0.00", font=("Arial", 10, "bold"))
        self.precio_total_label.pack(side=tk.LEFT)
    
        # Botón para vender boleto
        tk.Button(content_frame, text="Vender Boletos", command=self.vender_boletos).pack(pady=20)
    
        # Cargar rutas en el combobox
        self.cargar_rutas_combobox()

    def cargar_rutas_combobox(self):
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, r.origen, r.destino 
                FROM rutas r
                WHERE EXISTS (
                    SELECT 1 FROM horarios h WHERE h.ruta_id = r.id
                )
                ORDER BY r.origen, r.destino
            """)
            rutas = [f"{row[0]} - {row[1]} a {row[2]}" for row in cursor.fetchall()]
            self.ruta_combobox['values'] = rutas
        
            if not rutas:
                messagebox.showwarning("Advertencia", 
                    "No hay rutas con horarios disponibles. Por favor agregue rutas y horarios primero.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar rutas: {str(e)}")
        finally:
            conn.close()

    def actualizar_horarios_disponibles(self, event=None):
        # Obtener ID de la ruta seleccionada
        seleccion = self.ruta_combobox.get()
        if not seleccion:
            return
    
        ruta_id = int(seleccion.split("-")[0].strip())
    
        # Cargar horarios disponibles para esta ruta
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            cursor.execute("""
                SELECT h.id, h.hora_salida, h.hora_llegada, h.dias_semana, a.modelo
                FROM horarios h
                JOIN autobuses a ON h.autobus_id = a.id
                WHERE h.ruta_id = ?
                ORDER BY h.hora_salida
            """, (ruta_id,))
        
            horarios = []
            for row in cursor.fetchall():
                horarios.append(f"{row[0]} - {row[1]} a {row[2]} ({row[3]}) - {row[4]}")
        
            self.horario_combobox['values'] = horarios
            self.horario_combobox.set("")
            self.asientos_listbox.delete(0, tk.END)
            self.cantidad_spinbox.delete(0, tk.END)
            self.cantidad_spinbox.insert(0, "1")
            self.precio_unitario_label.config(text="$0.00")
            self.precio_total_label.config(text="$0.00")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar horarios: {str(e)}")
        finally:
            conn.close()

    def actualizar_asientos_disponibles(self, event=None):
        """Actualiza la lista de asientos disponibles basado en horario y fecha seleccionados"""
        seleccion = self.horario_combobox.get()
        if not seleccion:
            return
    
        try:
            horario_id = int(seleccion.split("-")[0].strip())
            fecha_viaje = self.fecha_viaje_entry.get_date().strftime("%Y-%m-%d")
        
            conn = sqlite3.connect('erp_autobuses.db')
            cursor = conn.cursor()
        
            # 1. Obtener asientos ya ocupados para este horario y fecha
            cursor.execute("""
                SELECT numero_asiento 
                FROM boletos 
                WHERE horario_id = ? AND fecha_viaje = ?
                ORDER BY numero_asiento
            """, (horario_id, fecha_viaje))
            asientos_ocupados = [row[0] for row in cursor.fetchall()]
        
            # 2. Obtener capacidad del autobús asignado a este horario
            cursor.execute("""
                SELECT a.capacidad 
                FROM horarios h
                JOIN autobuses a ON h.autobus_id = a.id
                WHERE h.id = ?
            """, (horario_id,))
            capacidad = cursor.fetchone()[0]
        
            # 3. Obtener precio del boleto para esta ruta
            cursor.execute("""
                SELECT r.precio_boleto 
                FROM horarios h
                JOIN rutas r ON h.ruta_id = r.id
                WHERE h.id = ?
            """, (horario_id,))
            precio = cursor.fetchone()[0]
        
            # 4. Generar lista de asientos disponibles (1 hasta capacidad)
            asientos_disponibles = [
                str(i) for i in range(1, capacidad + 1) 
                if i not in asientos_ocupados
            ]
        
            # Actualizar interfaz
            self.asientos_listbox.delete(0, tk.END)
            for asiento in asientos_disponibles:
                self.asientos_listbox.insert(tk.END, asiento)
            
            self.precio_unitario_label.config(text=f"${precio:.2f}")
            self.actualizar_precio_total()
        
            # Mostrar advertencia si no hay asientos
            if not asientos_disponibles:
                messagebox.showwarning("Disponibilidad", 
                    "No hay asientos disponibles para este horario y fecha")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar asientos: {str(e)}")
        finally:
            conn.close()

    def actualizar_cantidad_desde_asientos(self, event=None):
        """Actualiza la cantidad basada en los asientos seleccionados"""
        seleccionados = self.asientos_listbox.curselection()
        cantidad = len(seleccionados)
        
        # Actualizar el spinbox solo si hay selección
        if seleccionados:
            self.cantidad_spinbox.delete(0, tk.END)
            self.cantidad_spinbox.insert(0, str(cantidad))
        
        self.actualizar_precio_total()

    def actualizar_asientos_desde_cantidad(self, event=None):
        """Actualiza la selección de asientos basada en la cantidad"""
        try:
            cantidad_deseada = int(self.cantidad_spinbox.get())
            seleccionados = list(self.asientos_listbox.curselection())
            total_asientos = self.asientos_listbox.size()
            
            # Si la cantidad es mayor que los asientos seleccionados
            if cantidad_deseada > len(seleccionados):
                # Limpiar selección si es necesario
                if cantidad_deseada > total_asientos:
                    cantidad_deseada = total_asientos
                    self.cantidad_spinbox.delete(0, tk.END)
                    self.cantidad_spinbox.insert(0, str(cantidad_deseada))
                
                # Seleccionar los primeros N asientos disponibles
                nuevos_seleccionados = list(range(min(cantidad_deseada, total_asientos)))
                self.asientos_listbox.selection_clear(0, tk.END)
                for i in nuevos_seleccionados:
                    self.asientos_listbox.selection_set(i)
            
            # Si la cantidad es menor que los asientos seleccionados
            elif cantidad_deseada < len(seleccionados):
                # Mantener solo los primeros N seleccionados
                nuevos_seleccionados = seleccionados[:cantidad_deseada]
                self.asientos_listbox.selection_clear(0, tk.END)
                for i in nuevos_seleccionados:
                    self.asientos_listbox.selection_set(i)
            
            self.actualizar_precio_total()
        except ValueError:
            pass

    def actualizar_precio_total(self, event=None):
        """Calcula el precio total basado en la cantidad de boletos seleccionados"""
        try:
            precio_texto = self.precio_unitario_label.cget("text")
            precio_unitario = float(precio_texto.replace("$", ""))
            cantidad = len(self.asientos_listbox.curselection())
            
            # Asegurar que el spinbox refleje la cantidad correcta
            if cantidad != int(self.cantidad_spinbox.get()):
                self.cantidad_spinbox.delete(0, tk.END)
                self.cantidad_spinbox.insert(0, str(cantidad))
            
            total = precio_unitario * cantidad
            self.precio_total_label.config(text=f"${total:.2f}")
        except:
            self.precio_total_label.config(text="$0.00")

    def vender_boletos(self):
        # Validar datos
        nombre = self.nombre_pasajero_entry.get()
        apellidos = self.apellidos_pasajero_entry.get()
        ruta = self.ruta_combobox.get()
        horario = self.horario_combobox.get()
        asientos_seleccionados = self.asientos_listbox.curselection()
        fecha_viaje = self.fecha_viaje_entry.get_date().strftime("%Y-%m-%d")

        if not nombre or not apellidos or not ruta or not horario or not asientos_seleccionados:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        try:
            horario_id = int(horario.split("-")[0].strip())
            cantidad = len(asientos_seleccionados)
            
            # Obtener precio del boleto
            precio_texto = self.precio_unitario_label.cget("text")
            precio_unitario = float(precio_texto.replace("$", ""))
            precio_total = precio_unitario * cantidad

            # Verificar que los asientos aún estén disponibles
            conn = sqlite3.connect('erp_autobuses.db')
            cursor = conn.cursor()
            
            try:
                asientos_numeros = []
                for index in asientos_seleccionados:
                    numero_asiento = int(self.asientos_listbox.get(index))
                    asientos_numeros.append(numero_asiento)
                    
                    # Verificar si el asiento ya está ocupado
                    cursor.execute("""
                        SELECT 1 FROM boletos 
                        WHERE horario_id = ? AND fecha_viaje = ? AND numero_asiento = ?
                    """, (horario_id, fecha_viaje, numero_asiento))
            
                    if cursor.fetchone():
                        messagebox.showerror("Error", 
                            f"El asiento {numero_asiento} ya está ocupado. Por favor seleccione otros asientos.")
                        return

                fecha_compra = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Registrar cada boleto
                for numero_asiento in asientos_numeros:
                    cursor.execute("""
                        INSERT INTO boletos (nombre_pasajero, apellidos_pasajero, horario_id, 
                                            numero_asiento, fecha_viaje, fecha_compra, precio)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (nombre, apellidos, horario_id, numero_asiento, fecha_viaje, fecha_compra, precio_unitario))

                # Registrar ingreso en finanzas (solo una vez por la transacción completa)
                cursor.execute("SELECT saldo_actual FROM finanzas ORDER BY id DESC LIMIT 1")
                saldo_actual = cursor.fetchone()[0]
                concepto = f"Venta de {cantidad} boletos a {nombre} {apellidos}"
        
                cursor.execute("""
                    INSERT INTO finanzas (fecha, concepto, ingreso, egreso, saldo_actual)
                    VALUES (?, ?, ?, ?, ?)
                """, (fecha_compra, concepto, precio_total, 0, saldo_actual + precio_total))

                conn.commit()
                messagebox.showinfo("Éxito", f"{cantidad} boletos vendidos exitosamente")

                # Limpiar formulario
                self.nombre_pasajero_entry.delete(0, tk.END)
                self.apellidos_pasajero_entry.delete(0, tk.END)
                self.ruta_combobox.set("")
                self.horario_combobox.set("")
                self.fecha_viaje_entry.set_date(datetime.datetime.now())
                self.asientos_listbox.delete(0, tk.END)
                self.cantidad_spinbox.delete(0, tk.END)
                self.cantidad_spinbox.insert(0, "1")
                self.precio_unitario_label.config(text="$0.00")
                self.precio_total_label.config(text="$0.00")

                # Actualizar lista de asientos disponibles inmediatamente
                if ruta:
                    # Primero cargar horarios para la ruta seleccionada
                    self.actualizar_horarios_disponibles()
                
                    # Si había un horario seleccionado, cargar asientos para ese horario
                    if horario:
                        # Esperar un momento para que se actualice el combobox de horarios
                        self.root.after(100, lambda: self.horario_combobox.set(horario))
                        self.root.after(150, lambda: self.actualizar_asientos_disponibles())

            except Exception as e:
                messagebox.showerror("Error", f"Error al vender boletos: {str(e)}")
                conn.rollback()
            finally:
                conn.close()

        except ValueError:
            messagebox.showerror("Error", "Debe seleccionar al menos un asiento")
            return

    # ============ MÉTODOS PARA MANEJO DE CLIENTES ==============
    def mostrar_clientes(self):
        """Muestra una ventana con la lista de clientes y sus boletos comprados"""
        clientes_window = tk.Toplevel(self.root)
        clientes_window.title("Clientes")
        clientes_window.geometry("800x600")
        
        # Frame principal
        main_frame = tk.Frame(clientes_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de búsqueda
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Buscar cliente:").pack(side=tk.LEFT)
        self.busqueda_cliente_entry = tk.Entry(search_frame, width=40)
        self.busqueda_cliente_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Buscar", command=self.buscar_clientes).pack(side=tk.LEFT)
        
        # Treeview para mostrar clientes
        columns = ("ID", "Nombre", "Apellidos", "Boletos Comprados", "Última Compra", "Total Gastado")
        self.clientes_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.clientes_tree.heading(col, text=col)
            self.clientes_tree.column(col, width=120, anchor=tk.W)
        
        self.clientes_tree.column("Nombre", width=150)
        self.clientes_tree.column("Apellidos", width=150)
        self.clientes_tree.column("Boletos Comprados", width=120)
        self.clientes_tree.column("Última Compra", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.clientes_tree.yview)
        self.clientes_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clientes_tree.pack(fill=tk.BOTH, expand=True)
        
        # Botón para ver detalles
        detail_frame = tk.Frame(main_frame)
        detail_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(detail_frame, text="Ver Detalles", command=self.mostrar_detalle_cliente).pack(side=tk.LEFT)
        
        # Cargar todos los clientes inicialmente
        self.cargar_todos_clientes()
    
    def cargar_todos_clientes(self):
        """Carga todos los clientes que han comprado boletos"""
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            
            # Consulta para obtener información agregada de clientes
            cursor.execute("""
                SELECT 
                    MIN(b.id) as sample_id,
                    b.nombre_pasajero,
                    b.apellidos_pasajero,
                    COUNT(*) as boletos_comprados,
                    MAX(b.fecha_compra) as ultima_compra,
                    SUM(b.precio) as total_gastado
                FROM boletos b
                GROUP BY b.nombre_pasajero, b.apellidos_pasajero
                ORDER BY ultima_compra DESC
            """)
            
            # Limpiar treeview
            for item in self.clientes_tree.get_children():
                self.clientes_tree.delete(item)
                
            # Insertar datos
            for row in cursor.fetchall():
                self.clientes_tree.insert("", tk.END, values=(
                    row[0],  # sample_id
                    row[1],  # nombre
                    row[2],  # apellidos
                    row[3],  # boletos comprados
                    row[4],  # última compra
                    f"${row[5]:.2f}"  # total gastado
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {str(e)}")
        finally:
            conn.close()
    
    def buscar_clientes(self):
        """Busca clientes según el texto ingresado"""
        busqueda = self.busqueda_cliente_entry.get().strip()
        
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            
            if busqueda:
                # Búsqueda con filtro
                cursor.execute("""
                    SELECT 
                        MIN(b.id) as sample_id,
                        b.nombre_pasajero,
                        b.apellidos_pasajero,
                        COUNT(*) as boletos_comprados,
                        MAX(b.fecha_compra) as ultima_compra,
                        SUM(b.precio) as total_gastado
                    FROM boletos b
                    WHERE b.nombre_pasajero LIKE ? OR b.apellidos_pasajero LIKE ?
                    GROUP BY b.nombre_pasajero, b.apellidos_pasajero
                    ORDER BY ultima_compra DESC
                """, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                # Si no hay búsqueda, cargar todos
                return self.cargar_todos_clientes()
            
            # Limpiar treeview
            for item in self.clientes_tree.get_children():
                self.clientes_tree.delete(item)
                
            # Insertar datos
            for row in cursor.fetchall():
                self.clientes_tree.insert("", tk.END, values=(
                    row[0],  # sample_id
                    row[1],  # nombre
                    row[2],  # apellidos
                    row[3],  # boletos comprados
                    row[4],  # última compra
                    f"${row[5]:.2f}"  # total gastado
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar clientes: {str(e)}")
        finally:
            conn.close()
    
    def mostrar_detalle_cliente(self):
        """Muestra los detalles de los boletos comprados por un cliente"""
        selected_item = self.clientes_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
            return
            
        item_data = self.clientes_tree.item(selected_item[0], 'values')
        nombre = item_data[1]
        apellidos = item_data[2]
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Boletos de {nombre} {apellidos}")
        detail_window.geometry("900x600")
        
        # Frame principal
        main_frame = tk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Información resumen del cliente
        summary_frame = tk.Frame(main_frame, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        summary_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(summary_frame, text=f"Cliente: {nombre} {apellidos}", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        tk.Label(summary_frame, text=f"Total de boletos comprados: {item_data[3]}").pack(anchor=tk.W)
        tk.Label(summary_frame, text=f"Última compra: {item_data[4]}").pack(anchor=tk.W)
        tk.Label(summary_frame, text=f"Total gastado: {item_data[5]}").pack(anchor=tk.W)
        
        # Treeview para mostrar los boletos del cliente
        columns = ("ID", "Ruta", "Fecha Viaje", "Horario", "Asiento", "Precio", "Fecha Compra")
        boletos_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            boletos_tree.heading(col, text=col)
            boletos_tree.column(col, width=100, anchor=tk.W)
        
        boletos_tree.column("Ruta", width=200)
        boletos_tree.column("Fecha Viaje", width=100)
        boletos_tree.column("Horario", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=boletos_tree.yview)
        boletos_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        boletos_tree.pack(fill=tk.BOTH, expand=True)
        
        # Cargar los boletos del cliente
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    b.id,
                    r.origen || ' a ' || r.destino as ruta,
                    b.fecha_viaje,
                    h.hora_salida || ' a ' || h.hora_llegada as horario,
                    b.numero_asiento,
                    b.precio,
                    b.fecha_compra
                FROM boletos b
                JOIN horarios h ON b.horario_id = h.id
                JOIN rutas r ON h.ruta_id = r.id
                WHERE b.nombre_pasajero = ? AND b.apellidos_pasajero = ?
                ORDER BY b.fecha_compra DESC
            """, (nombre, apellidos))
            
            # Insertar datos
            for row in cursor.fetchall():
                boletos_tree.insert("", tk.END, values=(
                    row[0],  # ID
                    row[1],  # Ruta
                    row[2],  # Fecha Viaje
                    row[3],  # Horario
                    row[4],  # Asiento
                    f"${row[5]:.2f}",  # Precio
                    row[6]   # Fecha Compra
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar boletos del cliente: {str(e)}")
        finally:
            conn.close()

# =================== MÓDULO DE LOGÍSTICA ==============================
    def mostrar_modulo_logistica(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
    
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal)
        back_btn.pack(side=tk.RIGHT)
    
        # Título
        tk.Label(top_frame, text="Módulo de Logística", font=("Arial", 16)).pack(side=tk.LEFT)
    
        # Frame de pestañas
        tab_control = ttk.Notebook(main_frame)
    
        # Pestaña Rutas
        tab_rutas = tk.Frame(tab_control)
        tab_control.add(tab_rutas, text="Rutas")
        self.setup_tab_rutas(tab_rutas)
    
        # Pestaña Horarios
        tab_horarios = tk.Frame(tab_control)
        tab_control.add(tab_horarios, text="Horarios")
        self.setup_tab_horarios(tab_horarios)
    
        tab_control.pack(expand=1, fill="both")

    def setup_tab_rutas(self, parent):
        # Frame principal
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Controles superiores
        controls_frame = tk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=10)
    
        # Botones
        tk.Button(controls_frame, text="Agregar Ruta", command=self.mostrar_formulario_ruta).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Editar Ruta", command=self.mostrar_editar_ruta).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Eliminar Ruta", command=self.eliminar_ruta).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Refrescar", command=lambda: self.cargar_rutas(self.tree_rutas)).pack(side=tk.LEFT, padx=5)
    
        # Treeview para mostrar rutas
        columns = ("ID", "Origen", "Destino", "Distancia (km)", "Tiempo Estimado (minutos)", "Precio Boleto")
        self.tree_rutas = ttk.Treeview(frame, columns=columns, show="headings")
    
        # Configurar columnas
        for col in columns:
            self.tree_rutas.heading(col, text=col)
            self.tree_rutas.column(col, width=120)
    
        self.tree_rutas.pack(fill=tk.BOTH, expand=True, pady=10)
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_rutas.yview)
        self.tree_rutas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Cargar datos
        self.cargar_rutas(self.tree_rutas)

    def eliminar_ruta(self):
        # Obtener ruta seleccionada
        seleccion = self.tree_rutas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una ruta")
            return
    
        ruta_id = self.tree_rutas.item(seleccion[0], "values")[0]
    
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta ruta?\nEsta acción no se puede deshacer."):
            return
    
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
        
            # Verificar si la ruta tiene horarios asociados
            cursor.execute("SELECT COUNT(*) FROM horarios WHERE ruta_id = ?", (ruta_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "No se puede eliminar: Esta ruta tiene horarios asociados")
                return
        
            # Eliminar la ruta
            cursor.execute("DELETE FROM rutas WHERE id = ?", (ruta_id,))
            conn.commit()
            messagebox.showinfo("Éxito", "Ruta eliminada correctamente")
            self.cargar_rutas(self.tree_rutas)
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la ruta: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def mostrar_formulario_ruta(self):
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Ruta")
        popup.geometry("400x300")
    
        # Frame principal
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
    
        # Campos del formulario
        tk.Label(frame, text="Origen:").grid(row=0, column=0, sticky="w", pady=5)
        origen_entry = tk.Entry(frame, width=30)
        origen_entry.grid(row=0, column=1, pady=5)
    
        tk.Label(frame, text="Destino:").grid(row=1, column=0, sticky="w", pady=5)
        destino_entry = tk.Entry(frame, width=30)
        destino_entry.grid(row=1, column=1, pady=5)
    
        tk.Label(frame, text="Distancia (km):").grid(row=2, column=0, sticky="w", pady=5)
        distancia_entry = tk.Entry(frame, width=30)
        distancia_entry.grid(row=2, column=1, pady=5)
    
        tk.Label(frame, text="Tiempo Estimado:").grid(row=3, column=0, sticky="w", pady=5)
        tiempo_entry = tk.Entry(frame, width=30)
        tiempo_entry.grid(row=3, column=1, pady=5)
    
        tk.Label(frame, text="Precio Boleto:").grid(row=4, column=0, sticky="w", pady=5)
        precio_entry = tk.Entry(frame, width=30)
        precio_entry.grid(row=4, column=1, pady=5)
    
        # Botón para guardar
        tk.Button(frame, text="Guardar", command=lambda: self.guardar_ruta(
            origen_entry.get(),
            destino_entry.get(),
            distancia_entry.get(),
            tiempo_entry.get(),
            precio_entry.get(),
            popup
        )).grid(row=5, columnspan=2, pady=20)

    def guardar_ruta(self, origen, destino, distancia, tiempo, precio, popup):
        # Validación mejorada
        if not all([origen, destino, distancia, tiempo, precio]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
    
        try:
            distancia_float = float(distancia)
            precio_float = float(precio)
            if distancia_float <= 0 or precio_float <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Distancia y precio deben ser números válidos mayores a 0")
            return

        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rutas (origen, destino, distancia, tiempo_estimado, precio_boleto)
                VALUES (?, ?, ?, ?, ?)
            """, (origen.strip(), destino.strip(), distancia_float, tiempo.strip(), precio_float))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Ruta agregada correctamente")
            popup.destroy()
            self.cargar_rutas(self.tree_rutas)  # Actualizar la lista visible
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar ruta: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def mostrar_editar_ruta(self):
        # Obtener ruta seleccionada
        seleccion = self.tree_rutas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una ruta")
            return
    
        datos_ruta = self.tree_rutas.item(seleccion[0], "values")
        ruta_id = datos_ruta[0]
    
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Editar Ruta")
        popup.geometry("400x300")
    
        # Frame principal
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
    
        # Campos del formulario con los valores actuales
        tk.Label(frame, text="Origen:").grid(row=0, column=0, sticky="w", pady=5)
        origen_entry = tk.Entry(frame, width=30)
        origen_entry.grid(row=0, column=1, pady=5)
        origen_entry.insert(0, datos_ruta[1])
    
        tk.Label(frame, text="Destino:").grid(row=1, column=0, sticky="w", pady=5)
        destino_entry = tk.Entry(frame, width=30)
        destino_entry.grid(row=1, column=1, pady=5)
        destino_entry.insert(0, datos_ruta[2])
    
        tk.Label(frame, text="Distancia (km):").grid(row=2, column=0, sticky="w", pady=5)
        distancia_entry = tk.Entry(frame, width=30)
        distancia_entry.grid(row=2, column=1, pady=5)
        distancia_entry.insert(0, datos_ruta[3].replace(" km", ""))
    
        tk.Label(frame, text="Tiempo Estimado:").grid(row=3, column=0, sticky="w", pady=5)
        tiempo_entry = tk.Entry(frame, width=30)
        tiempo_entry.grid(row=3, column=1, pady=5)
        tiempo_entry.insert(0, datos_ruta[4])
    
        tk.Label(frame, text="Precio Boleto:").grid(row=4, column=0, sticky="w", pady=5)
        precio_entry = tk.Entry(frame, width=30)
        precio_entry.grid(row=4, column=1, pady=5)
        precio_entry.insert(0, datos_ruta[5].replace("$", ""))
    
        # Botón para guardar
        tk.Button(frame, text="Guardar Cambios", 
                command=lambda: self.guardar_edicion_ruta(
                    ruta_id,
                    origen_entry.get(),
                    destino_entry.get(),
                    distancia_entry.get(),
                    tiempo_entry.get(),
                    precio_entry.get(),
                    popup
                )).grid(row=5, columnspan=2, pady=20)
    
    def guardar_edicion_ruta(self, ruta_id, origen, destino, distancia, tiempo, precio, popup):
        # Validación
        if not all([origen, destino, distancia, tiempo, precio]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
    
        try:
            distancia_float = float(distancia)
            precio_float = float(precio)
            if distancia_float <= 0 or precio_float <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Distancia y precio deben ser números válidos mayores a 0")
            return
    
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rutas 
                SET origen = ?, destino = ?, distancia = ?, tiempo_estimado = ?, precio_boleto = ?
                WHERE id = ?
            """, (origen.strip(), destino.strip(), distancia_float, tiempo.strip(), precio_float, ruta_id))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Ruta actualizada correctamente")
            popup.destroy()
            self.cargar_rutas(self.tree_rutas)
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la ruta: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def cargar_rutas(self, tree):
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
    
        # Cargar rutas de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, origen, destino, distancia, tiempo_estimado, precio_boleto 
                FROM rutas 
                ORDER BY origen, destino
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=(
                    row[0],  # ID
                    row[1],  # Origen
                    row[2],  # Destino
                    f"{row[3]:.1f} km",  # Distancia
                    row[4],  # Tiempo estimado
                    f"${row[5]:.2f}"  # Precio
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar rutas: {str(e)}")
        finally:
            conn.close()

    def setup_tab_horarios(self, parent):
        # Frame principal
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Controles superiores
        controls_frame = tk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=10)
    
        # Botones
        tk.Button(controls_frame, text="Agregar Horario", command=self.mostrar_formulario_horario).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Eliminar Horario", command=self.eliminar_horario).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Refrescar", command=lambda: self.cargar_horarios(self.tree_horarios)).pack(side=tk.LEFT, padx=5)
    
        # Treeview para mostrar horarios
        columns = ("ID", "Ruta", "Autobús", "Hora Salida", "Hora Llegada", "Días")
        self.tree_horarios = ttk.Treeview(frame, columns=columns, show="headings")
    
        # Configurar columnas
        for col in columns:
            self.tree_horarios.heading(col, text=col)
            self.tree_horarios.column(col, width=120)
    
        self.tree_horarios.pack(fill=tk.BOTH, expand=True, pady=10)
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_horarios.yview)
        self.tree_horarios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Cargar datos
        self.cargar_horarios(self.tree_horarios)

    def eliminar_horario(self):
        # Obtener horario seleccionado
        seleccion = self.tree_horarios.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un horario")
            return
    
        horario_id = self.tree_horarios.item(seleccion[0], "values")[0]
    
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", 
                                "¿Está seguro de eliminar este horario?\n"
                                "Esta acción también eliminará todos los boletos asociados."):
            return
    
        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
        
            # Verificar si hay boletos vendidos para este horario
            cursor.execute("SELECT COUNT(*) FROM boletos WHERE horario_id = ?", (horario_id,))
            num_boletos = cursor.fetchone()[0]
        
            if num_boletos > 0:
                # Preguntar confirmación adicional si hay boletos vendidos
                if not messagebox.askyesno("Confirmar", 
                                        f"Este horario tiene {num_boletos} boletos vendidos.\n"
                                        "¿Desea continuar con la eliminación?"):
                    return
        
            # Eliminar en cascada (primero boletos, luego el horario)
            cursor.execute("DELETE FROM boletos WHERE horario_id = ?", (horario_id,))
            cursor.execute("DELETE FROM horarios WHERE id = ?", (horario_id,))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Horario eliminado correctamente")
            self.cargar_horarios(self.tree_horarios)
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el horario: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def mostrar_formulario_horario(self):
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Agregar Horario")
        popup.geometry("500x300")
    
        # Frame principal
        frame = tk.Frame(popup)
        frame.pack(padx=20, pady=20)
    
        # Campos del formulario
        tk.Label(frame, text="Ruta:").grid(row=0, column=0, sticky="w", pady=5)
        ruta_combobox = ttk.Combobox(frame, width=30)
        ruta_combobox.grid(row=0, column=1, pady=5)
    
        tk.Label(frame, text="Autobús:").grid(row=1, column=0, sticky="w", pady=5)
        autobus_combobox = ttk.Combobox(frame, width=30)
        autobus_combobox.grid(row=1, column=1, pady=5)
    
        tk.Label(frame, text="Hora Salida:").grid(row=2, column=0, sticky="w", pady=5)
        hora_salida_entry = tk.Entry(frame, width=30)
        hora_salida_entry.grid(row=2, column=1, pady=5)
        hora_salida_entry.insert(0, "HH:MM")
    
        tk.Label(frame, text="Hora Llegada:").grid(row=3, column=0, sticky="w", pady=5)
        hora_llegada_entry = tk.Entry(frame, width=30)
        hora_llegada_entry.grid(row=3, column=1, pady=5)
        hora_llegada_entry.insert(0, "HH:MM")
    
        tk.Label(frame, text="Días de Operación:").grid(row=4, column=0, sticky="w", pady=5)
        dias_entry = tk.Entry(frame, width=30)
        dias_entry.grid(row=4, column=1, pady=5)
        dias_entry.insert(0, "Lunes-Viernes")
    
        # Cargar rutas y autobuses en los combobox
        self.cargar_rutas_autobuses_combobox(ruta_combobox, autobus_combobox)
    
        # Botón para guardar
        tk.Button(frame, text="Guardar", command=lambda: self.guardar_horario(
            ruta_combobox.get(),
            autobus_combobox.get(),
            hora_salida_entry.get(),
            hora_llegada_entry.get(),
            dias_entry.get(),
            popup
        )).grid(row=5, columnspan=2, pady=20)

    def cargar_rutas_autobuses_combobox(self, ruta_combobox, autobus_combobox):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            # Cargar rutas
            cursor.execute("SELECT id, origen, destino FROM rutas ORDER BY origen, destino")
            rutas = [f"{row[0]} - {row[1]} a {row[2]}" for row in cursor.fetchall()]
            ruta_combobox['values'] = rutas
        
            # Cargar autobuses
            cursor.execute("SELECT id, marca, modelo FROM autobuses WHERE estado != 'Inactivo' ORDER BY marca, modelo")
            autobuses = [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
            autobus_combobox['values'] = autobuses
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
        finally:
            conn.close()

    def guardar_horario(self, ruta, autobus, hora_salida, hora_llegada, dias, popup):
        # Validación mejorada
        if not all([ruta, autobus, hora_salida, hora_llegada, dias]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
    
        # Validar formato de horas (HH:MM)
        if not (re.match(r'^[0-2][0-9]:[0-5][0-9]$', hora_salida) and 
                re.match(r'^[0-2][0-9]:[0-5][0-9]$', hora_llegada)):
            messagebox.showerror("Error", "Formato de hora debe ser HH:MM (24 horas)")
            return

        try:
            ruta_id = int(ruta.split("-")[0].strip())
            autobus_id = int(autobus.split("-")[0].strip())
        except (ValueError, AttributeError):
            messagebox.showerror("Error", "Selección de ruta o autobús no válida")
            return

        conn = sqlite3.connect('erp_autobuses.db')
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO horarios (ruta_id, autobus_id, hora_salida, hora_llegada, dias_semana)
                VALUES (?, ?, ?, ?, ?)
            """, (ruta_id, autobus_id, hora_salida, hora_llegada, dias))
        
            conn.commit()
            messagebox.showinfo("Éxito", "Horario agregado correctamente")
            popup.destroy()
            self.cargar_horarios(self.tree_horarios)  # Actualizar la lista
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar horario: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def cargar_horarios(self, tree):
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
    
        # Cargar horarios de la base de datos
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT h.id, 
                    r.origen || ' - ' || r.destino as ruta,
                    a.marca || ' ' || a.modelo as autobus,
                    h.hora_salida,
                    h.hora_llegada,
                    h.dias_semana
                FROM horarios h
                JOIN rutas r ON h.ruta_id = r.id
                JOIN autobuses a ON h.autobus_id = a.id
                ORDER BY h.hora_salida
            """)
        
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar horarios: {str(e)}")
        finally:
            conn.close()

# =================== MÓDULO DE REPORTES GENERALES =====================
    def mostrar_reportes_generales(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Barra superior
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
    
        # Botón de regreso
        back_btn = tk.Button(top_frame, text="Volver al Menú", command=self.mostrar_menu_principal)
        back_btn.pack(side=tk.RIGHT)
    
        # Título
        tk.Label(top_frame, text="Reportes Generales", font=("Arial", 16)).pack(side=tk.LEFT)
    
        # Frame de contenido
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Opciones para generar reportes
        options_frame = tk.Frame(content_frame)
        options_frame.pack(fill=tk.X, pady=10)
    
        # Selector de tipo de reporte
        tk.Label(options_frame, text="Tipo de Reporte:").pack(side=tk.LEFT, padx=5)
        self.tipo_reporte = ttk.Combobox(options_frame, values=[
            "Empleados por Departamento", 
            "Estado de Autobuses",
            "Ventas Totales",
            "Gastos Totales"
        ], width=20)
        self.tipo_reporte.pack(side=tk.LEFT, padx=5)
    
        # Botón para generar
        tk.Button(options_frame, text="Generar Reporte", command=self.generar_reporte_general).pack(side=tk.LEFT, padx=10)
    
        # Frame para resultado
        self.resultado_reporte_frame = tk.Frame(content_frame)
        self.resultado_reporte_frame.pack(fill=tk.BOTH, expand=True, pady=20)

    def generar_reporte_general(self):
        # Limpiar frame de resultados
        for widget in self.resultado_reporte_frame.winfo_children():
            widget.destroy()
    
        tipo_reporte = self.tipo_reporte.get()
    
        if not tipo_reporte:
            messagebox.showwarning("Advertencia", "Debe seleccionar un tipo de reporte")
            return
    
        if tipo_reporte == "Empleados por Departamento":
            self.generar_reporte_empleados_departamento()
        elif tipo_reporte == "Estado de Autobuses":
            self.generar_reporte_estado_autobuses()
        elif tipo_reporte == "Ventas Totales":
            self.generar_reporte_ventas_totales()
        elif tipo_reporte == "Gastos Totales":
            self.generar_reporte_gastos_totales()

    def generar_reporte_empleados_departamento(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            # Obtener empleados por departamento
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN puesto = 'Conductor' THEN 'Conductores'
                        WHEN puesto LIKE 'Agente%' THEN SUBSTR(puesto, 8)
                        ELSE 'Otros'
                    END as departamento,
                    COUNT(*) as cantidad,
                    SUM(salario) as total_salarios
                FROM empleados
                WHERE activo = 1
                GROUP BY departamento
                ORDER BY cantidad DESC
            """)
        
            resultados = cursor.fetchall()
        
            if not resultados:
                tk.Label(self.resultado_reporte_frame, text="No hay empleados registrados").pack(pady=20)
                return
        
            # Crear tabla
            tk.Label(self.resultado_reporte_frame, text="Empleados por Departamento", font=("Arial", 14, "bold")).pack(pady=10)
        
            tree = ttk.Treeview(self.resultado_reporte_frame, columns=("Departamento", "Cantidad", "Total Salarios"), show="headings")
            tree.heading("Departamento", text="Departamento")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total Salarios", text="Total Salarios ($)")
        
            tree.column("Departamento", width=150)
            tree.column("Cantidad", width=100)
            tree.column("Total Salarios", width=150)
        
            for row in resultados:
                tree.insert("", tk.END, values=(row[0], row[1], f"${row[2]:,.2f}"))
        
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
            # Crear gráfico
            figure = plt.Figure(figsize=(6, 4), dpi=100)
            ax = figure.add_subplot(111)
        
            departamentos = [row[0] for row in resultados]
            cantidades = [row[1] for row in resultados]
        
            ax.bar(departamentos, cantidades)
            ax.set_title('Empleados por Departamento')
            ax.set_ylabel('Cantidad de Empleados')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
            canvas = FigureCanvasTkAgg(figure, self.resultado_reporte_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
        finally:
            conn.close()

    def generar_reporte_estado_autobuses(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            # Obtener estado de autobuses
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM autobuses
                GROUP BY estado
                ORDER BY cantidad DESC
            """)
        
            resultados = cursor.fetchall()
        
            if not resultados:
                tk.Label(self.resultado_reporte_frame, text="No hay autobuses registrados").pack(pady=20)
                return
        
            # Crear tabla
            tk.Label(self.resultado_reporte_frame, text="Estado de Autobuses", font=("Arial", 14, "bold")).pack(pady=10)
        
            tree = ttk.Treeview(self.resultado_reporte_frame, columns=("Estado", "Cantidad"), show="headings")
            tree.heading("Estado", text="Estado")
            tree.heading("Cantidad", text="Cantidad")
        
            tree.column("Estado", width=150)
            tree.column("Cantidad", width=100)
        
            for row in resultados:
                tree.insert("", tk.END, values=row)
        
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
            # Crear gráfico circular
            figure = plt.Figure(figsize=(6, 6), dpi=100)
            ax = figure.add_subplot(111)
        
            estados = [row[0] for row in resultados]
            cantidades = [row[1] for row in resultados]
        
            ax.pie(cantidades, labels=estados, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribución de Autobuses por Estado')
            ax.axis('equal')
        
            canvas = FigureCanvasTkAgg(figure, self.resultado_reporte_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
        finally:
            conn.close()

    def generar_reporte_ventas_totales(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            # Obtener ventas totales por mes
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', fecha_compra) as mes,
                    COUNT(*) as boletos,
                    SUM(precio) as total
                FROM boletos
                GROUP BY mes
                ORDER BY mes
            """)
        
            resultados = cursor.fetchall()
        
            if not resultados:
                tk.Label(self.resultado_reporte_frame, text="No hay ventas registradas").pack(pady=20)
                return
        
            # Crear tabla
            tk.Label(self.resultado_reporte_frame, text="Ventas Totales por Mes", font=("Arial", 14, "bold")).pack(pady=10)
        
            tree = ttk.Treeview(self.resultado_reporte_frame, columns=("Mes", "Boletos", "Total"), show="headings")
            tree.heading("Mes", text="Mes")
            tree.heading("Boletos", text="Boletos")
            tree.heading("Total", text="Total ($)")
        
            tree.column("Mes", width=100)
            tree.column("Boletos", width=100)
            tree.column("Total", width=150)
        
            for row in resultados:
                tree.insert("", tk.END, values=(row[0], row[1], f"${row[2]:,.2f}"))
        
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
            # Crear gráfico de líneas
            figure = plt.Figure(figsize=(6, 4), dpi=100)
            ax = figure.add_subplot(111)
        
            meses = [row[0] for row in resultados]
            totales = [row[2] for row in resultados]
        
            ax.plot(meses, totales, 'o-')
            ax.set_title('Ventas Totales por Mes')
            ax.set_ylabel('Ventas ($)')
            ax.set_xlabel('Mes')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
            # Agregar etiquetas con valores
            for i, v in enumerate(totales):
                ax.text(i, v + 1000, f"${v:,.0f}", ha='center')
        
            canvas = FigureCanvasTkAgg(figure, self.resultado_reporte_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
        finally:
            conn.close()

    def generar_reporte_gastos_totales(self):
        conn = sqlite3.connect('erp_autobuses.db')
        cursor = conn.cursor()
    
        try:
            # Obtener gastos totales por mes
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', fecha) as mes,
                    SUM(egreso) as total
                FROM finanzas
                GROUP BY mes
                ORDER BY mes
            """)
        
            resultados = cursor.fetchall()
        
            if not resultados:
                tk.Label(self.resultado_reporte_frame, text="No hay gastos registrados").pack(pady=20)
                return
        
            # Crear tabla
            tk.Label(self.resultado_reporte_frame, text="Gastos Totales por Mes", font=("Arial", 14, "bold")).pack(pady=10)
        
            tree = ttk.Treeview(self.resultado_reporte_frame, columns=("Mes", "Total"), show="headings")
            tree.heading("Mes", text="Mes")
            tree.heading("Total", text="Total ($)")
        
            tree.column("Mes", width=100)
            tree.column("Total", width=150)
        
            for row in resultados:
                tree.insert("", tk.END, values=(row[0], f"${row[1]:,.2f}"))
        
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
            # Crear gráfico de barras
            figure = plt.Figure(figsize=(6, 4), dpi=100)
            ax = figure.add_subplot(111)
        
            meses = [row[0] for row in resultados]
            totales = [row[1] for row in resultados]
        
            bars = ax.bar(meses, totales, color='red')
            ax.set_title('Gastos Totales por Mes')
            ax.set_ylabel('Gastos ($)')
            ax.set_xlabel('Mes')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
            # Agregar etiquetas con valores
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom')
        
            canvas = FigureCanvasTkAgg(figure, self.resultado_reporte_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
        finally:
            conn.close()

# =================== FUNCIÓN PRINCIPAL ================================
def main():
    root = tk.Tk()
    app = SistemaERP(root)
    root.mainloop()

if __name__ == "__main__":
    main()