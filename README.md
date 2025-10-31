# ClasesYa - Registro y login para alumnos y profesores

Aplicacion web construida con Django y Bootstrap que permite gestionar el registro e inicio de sesion de dos tipos de usuarios: alumnos y profesores. El proyecto actua como base para la plataforma **ClasesYa**, donde los alumnos pueden contactar profesores y coordinar clases en linea.

## Caracteristicas principales

- Modelo de usuario personalizado (`accounts.User`) con roles diferenciados para alumnos y profesores.
- Formularios de registro separados que guardan informacion extra en perfiles (`StudentProfile` y `TeacherProfile`).
- Autenticacion con vistas de Django (`LoginView` / `LogoutView`) y formularios adaptados a Bootstrap.
- Plantillas base y componentes reutilizables con Bootstrap 5 para mantener un diseno consistente.
- Arquitectura Django siguiendo el patron MTV (analogo a MVC) separando modelos, vistas y plantillas.

## Requisitos previos

- Python 3.10 o superior.
- Pip para instalar dependencias.
- (Opcional) Un entorno virtual para aislar paquetes.

## Configuracion rapida

```bash
# 1. Clonar el repositorio (si aun no lo tienes)
git clone <url-del-repositorio>
cd clasesya

# 2. Crear y activar un entorno virtual (opcional pero recomendado)
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. (Opcional) Crear un superusuario para acceder al admin
python manage.py createsuperuser

# 6. Ejecutar el servidor de desarrollo
python manage.py runserver
```

Visita `http://127.0.0.1:8000/` para ver la pagina de inicio. Desde alli podras registrarte como alumno o profesor y acceder al panel privado una vez autenticado.

## Estructura de carpetas relevante

- `clasesya/accounts/`: modelos, formularios, vistas y rutas de autenticacion.
- `clasesya/templates/base.html`: layout principal con navegacion Bootstrap.
- `clasesya/templates/landing.html`: pagina publica de bienvenida.
- `clasesya/templates/home.html`: panel para usuarios autenticados.
- `clasesya/templates/accounts/`: formularios de registro para alumno y profesor.
- `clasesya/templates/registration/`: formulario de inicio de sesion.
- `clasesya/static/`: carpeta lista para recursos estaticos personalizados.
- `clasesya/requirements.txt`: dependencias del proyecto.

## Proximos pasos sugeridos

- Integrar la busqueda de profesores por asignatura y disponibilidad.
- Anadir flujo de solicitud y confirmacion de clases (incluyendo la primera gratis).
- Incorporar pasarela de pago para las clases posteriores.
- Crear tests unitarios y funcionales que cubran los flujos de registro y autenticacion.

Con esta base ya tienes la autenticacion diferenciada para alumnos y profesores lista para extender el resto de la plataforma ClasesYa.
