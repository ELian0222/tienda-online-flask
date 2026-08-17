import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.utils import secure_filename

from config import Config

from models import (
    db,
    Producto,
    ProductoFisico,
    ProductoDigital,
    ProductoPerecible,
    Usuario
)

from auth import login_requerido, rol_requerido


# ============================================================
# CONFIGURACIÓN DE FLASK
# ============================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# ============================================================
# CONFIGURACIÓN DE IMÁGENES
# ============================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crear la carpeta automáticamente si no existe
os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# ============================================================
# FUNCIÓN PARA VALIDAR IMÁGENES
# ============================================================

def archivo_permitido(nombre_archivo):

    return (
        "." in nombre_archivo
        and
        nombre_archivo.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# FUNCIÓN PARA GUARDAR IMAGEN
# ============================================================

def guardar_imagen(archivo):

    if not archivo:
        return None

    if archivo.filename == "":
        return None

    if not archivo_permitido(archivo.filename):

        raise ValueError(
            "Formato de imagen no permitido. "
            "Usa PNG, JPG, JPEG o WEBP."
        )

    nombre_seguro = secure_filename(
        archivo.filename
    )

    extension = nombre_seguro.rsplit(
        ".",
        1
    )[1].lower()

    nombre_unico = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    ruta = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nombre_unico
    )

    archivo.save(ruta)

    return nombre_unico


# ============================================================
# CATÁLOGO
# ============================================================

@app.route("/")
def inicio():

    productos = Producto.query.filter_by(
        activo=True
    ).all()

    return render_template(
        "index.html",
        productos=productos
    )


# ============================================================
# DETALLE
# ============================================================

@app.route("/producto/<int:producto_id>")
def detalle_producto(producto_id):

    producto = Producto.query.get_or_404(
        producto_id
    )

    return render_template(
        "detalle.html",
        producto=producto
    )


# ============================================================
# CREAR PRODUCTO FÍSICO
# SOLO ADMIN
# ============================================================

@app.route(
    "/productos/nuevo/fisico",
    methods=["GET", "POST"]
)
@rol_requerido("admin")
def nuevo_producto_fisico():

    if request.method == "POST":

        try:

            imagen = guardar_imagen(
                request.files.get("imagen")
            )

            producto = ProductoFisico(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(
                    request.form["precio_base"]
                ),
                stock=int(
                    request.form["stock"]
                ),
                peso_kg=float(
                    request.form["peso_kg"]
                ),
                costo_envio_por_kg=float(
                    request.form[
                        "costo_envio_por_kg"
                    ]
                ),
                imagen=imagen
            )

            db.session.add(producto)
            db.session.commit()

            flash(
                f"Producto físico "
                f"'{producto.nombre}' "
                f"creado correctamente.",
                "success"
            )

            return redirect(
                url_for("inicio")
            )

        except ValueError as error:

            flash(
                str(error),
                "danger"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Ocurrió un error. "
                "Verifica que el código "
                "no esté repetido.",
                "danger"
            )

    return render_template(
        "nuevo_fisico.html"
    )


# ============================================================
# CREAR PRODUCTO DIGITAL
# SOLO ADMIN
# ============================================================

@app.route(
    "/productos/nuevo/digital",
    methods=["GET", "POST"]
)
@rol_requerido("admin")
def nuevo_producto_digital():

    if request.method == "POST":

        try:

            imagen = guardar_imagen(
                request.files.get("imagen")
            )

            producto = ProductoDigital(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(
                    request.form["precio_base"]
                ),
                stock=int(
                    request.form["stock"]
                ),
                licencia=request.form[
                    "licencia"
                ],
                imagen=imagen
            )

            db.session.add(producto)
            db.session.commit()

            flash(
                f"Producto digital "
                f"'{producto.nombre}' "
                f"creado correctamente.",
                "success"
            )

            return redirect(
                url_for("inicio")
            )

        except ValueError as error:

            flash(
                str(error),
                "danger"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Ocurrió un error. "
                "Verifica que el código "
                "no esté repetido.",
                "danger"
            )

    return render_template(
        "nuevo_digital.html"
    )


# ============================================================
# CREAR PRODUCTO PERECIBLE
# SOLO ADMIN
# ============================================================

@app.route(
    "/productos/nuevo/perecible",
    methods=["GET", "POST"]
)
@rol_requerido("admin")
def nuevo_producto_perecible():

    if request.method == "POST":

        try:

            imagen = guardar_imagen(
                request.files.get("imagen")
            )

            producto = ProductoPerecible(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(
                    request.form["precio_base"]
                ),
                stock=int(
                    request.form["stock"]
                ),
                dias_para_vencer=int(
                    request.form[
                        "dias_para_vencer"
                    ]
                ),
                imagen=imagen
            )

            db.session.add(producto)
            db.session.commit()

            flash(
                f"Producto perecible "
                f"'{producto.nombre}' "
                f"creado correctamente.",
                "success"
            )

            return redirect(
                url_for("inicio")
            )

        except ValueError as error:

            flash(
                str(error),
                "danger"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Ocurrió un error. "
                "Verifica que el código "
                "no esté repetido.",
                "danger"
            )

    return render_template(
        "nuevo_perecible.html"
    )


# ============================================================
# EDITAR PRODUCTO
# SOLO ADMIN
# ============================================================

@app.route(
    "/productos/<int:producto_id>/editar",
    methods=["GET", "POST"]
)
@rol_requerido("admin")
def editar_producto(producto_id):

    producto = Producto.query.get_or_404(
        producto_id
    )

    if request.method == "POST":

        try:

            producto.nombre = request.form[
                "nombre"
            ]

            producto.precio_base = float(
                request.form["precio_base"]
            )

            producto.stock = int(
                request.form["stock"]
            )

            # Si el usuario selecciona una
            # imagen nueva, reemplazamos el nombre
            nueva_imagen = request.files.get(
                "imagen"
            )

            if (
                nueva_imagen
                and
                nueva_imagen.filename != ""
            ):

                nombre_imagen = guardar_imagen(
                    nueva_imagen
                )

                producto.imagen = nombre_imagen

            db.session.commit()

            flash(
                f"Producto "
                f"'{producto.nombre}' "
                f"actualizado correctamente.",
                "success"
            )

            return redirect(
                url_for(
                    "detalle_producto",
                    producto_id=producto.id
                )
            )

        except ValueError as error:

            flash(
                str(error),
                "danger"
            )

        except Exception:

            db.session.rollback()

            flash(
                "Ocurrió un error "
                "al actualizar el producto.",
                "danger"
            )

    return render_template(
        "editar.html",
        producto=producto
    )


# ============================================================
# DESACTIVAR PRODUCTO
# SOLO ADMIN
# ============================================================

@app.route(
    "/productos/<int:producto_id>/eliminar",
    methods=["POST"]
)
@rol_requerido("admin")
def eliminar_producto(producto_id):

    producto = Producto.query.get_or_404(
        producto_id
    )

    producto.activo = False

    db.session.commit()

    flash(
        f"Producto "
        f"'{producto.nombre}' "
        f"desactivado del catálogo.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )


# ============================================================
# REGISTRO
# ============================================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        usuario_existente = (
            Usuario.query.filter_by(
                email=email
            ).first()
        )

        if usuario_existente:

            flash(
                "Ya existe una cuenta "
                "con ese correo.",
                "danger"
            )

            return render_template(
                "registro.html"
            )

        usuario = Usuario(
            nombre=request.form["nombre"],
            email=email,
            rol="cliente"
        )

        usuario.set_password(
            request.form["password"]
        )

        db.session.add(usuario)
        db.session.commit()

        flash(
            "Cuenta creada correctamente. "
            "Ya puedes iniciar sesión.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "registro.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if (
            usuario
            and
            usuario.check_password(password)
        ):

            session["usuario_id"] = (
                usuario.id
            )

            session["usuario_nombre"] = (
                usuario.nombre
            )

            session["usuario_rol"] = (
                usuario.rol
            )

            flash(
                f"¡Bienvenido, "
                f"{usuario.nombre}!",
                "success"
            )

            return redirect(
                url_for("inicio")
            )

        flash(
            "Correo o contraseña "
            "incorrectos.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )


# ============================================================
# AGREGAR PRODUCTO AL CARRITO
# ============================================================

@app.route(
    "/carrito/agregar/<int:producto_id>",
    methods=["POST"]
)
@login_requerido
def agregar_carrito(producto_id):

    producto = Producto.query.get_or_404(
        producto_id
    )

    carrito = session.get(
        "carrito",
        {}
    )

    clave = str(producto_id)

    carrito[clave] = (
        carrito.get(clave, 0) + 1
    )

    session["carrito"] = carrito

    flash(
        f"'{producto.nombre}' "
        f"agregado al carrito.",
        "success"
    )

    return redirect(
        request.referrer
        or
        url_for("inicio")
    )


# ============================================================
# VER CARRITO
# ============================================================

@app.route("/carrito")
@login_requerido
def ver_carrito():

    carrito = session.get(
        "carrito",
        {}
    )

    items = []
    total = 0.0

    for clave, cantidad in carrito.items():

        producto = Producto.query.get(
            int(clave)
        )

        if producto:

            subtotal = (
                producto.precio_final()
                * cantidad
            )

            total += subtotal

            items.append(
                {
                    "producto": producto,
                    "cantidad": cantidad,
                    "subtotal": subtotal
                }
            )

    return render_template(
        "carrito.html",
        items=items,
        total=total
    )


# ============================================================
# QUITAR PRODUCTO DEL CARRITO
# ============================================================

@app.route(
    "/carrito/eliminar/<int:producto_id>",
    methods=["POST"]
)
@login_requerido
def eliminar_carrito(producto_id):

    carrito = session.get(
        "carrito",
        {}
    )

    clave = str(producto_id)

    if clave in carrito:

        del carrito[clave]

        session["carrito"] = carrito

        flash(
            "Producto quitado "
            "del carrito.",
            "success"
        )

    return redirect(
        url_for("ver_carrito")
    )


# ============================================================
# EJECUTAR APLICACIÓN
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)