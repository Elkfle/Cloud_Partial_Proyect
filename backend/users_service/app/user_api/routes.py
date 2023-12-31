import os;
import re;
import shutil;
from . import user_api_blueprint;
from .. import db, bcrypt;
from ..models import User;
from flask_bcrypt import Bcrypt;
from PIL import Image;
from werkzeug.utils import secure_filename;
from flask import (
    request,
    jsonify,
    current_app,
    send_file
);
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required
);
from flask_mail import (
    Mail,
    Message,
);

mail = Mail(current_app);

#===: Handle CORS ===:
@user_api_blueprint.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '15')
    return response


#===: Handle current user ===:
@user_api_blueprint.route("/api/current_user", methods=["GET"])
@jwt_required()
def current_user_route():
    current_user_id = get_jwt_identity();
    
    print(current_user_id);

    if current_user_id is not None:
        current_user = User.query.get(current_user_id);
        return jsonify({
            "status": "authenticated",
            "user": {
                "id": current_user.id,
                "username": current_user.nickname,
                "email": current_user.email,
                "imageProfile": current_user.imageProfile,
                "bank": current_user.bank,
            }
        });
    else: return jsonify({"status": "not authenticated"}), 401;


#===: Handle register ===:
@user_api_blueprint.route("/api/register", methods=["POST"])
def register():
    data = request.get_json();
    
    # handle errors for incomplete data
    if not data: return jsonify({"message": "No se proporcionó información."}), 400;
    username = data.get("username");
    password = data.get("password");
    email = data.get("email");
    
    if (not username): return jsonify({"message": "No se proporcionó nombre de usuario."}), 400;
    if (not password): return jsonify({"message": "No se proporcionó contraseña."}), 400;
    
    # validate data
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email): return jsonify({"message": "El correo electrónico es inválido."}), 400;
    if len(password) < 5: return jsonify({"message": "La contraseña debe tener como mínimo 5 carácteres."}), 400;
    
    # check if user exists
    user = User.query.filter_by(nickname=username).first();
    if user: return jsonify({"message": "El usuario ya existe. Inténtelo de nuevo."}), 400;
    
    user = User.query.filter_by(email=email).first();
    if user: return jsonify({"message": "El correo electrónico está asociado con otra cuenta."}), 400;
    
    # encrypt password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8');
    new_user = User(nickname=username, password=hashed_password, email=email, bank=1000);
    db.session.add(new_user);
    db.session.commit();
    return jsonify(message="User created successfully"), 201;


#===: Handle login ===:
@user_api_blueprint.route("/api/login", methods=["POST"])
def login():
    data = request.get_json();
    
    # handle errors if no data provided
    if not data: return jsonify({"message": "No se proporcionó información"}), 400;
    username = data.get("username");
    password = data.get("password");
    
    if (not username): return jsonify({"message": "No se proporcionó nombre de usuario."}), 400;
    if (not password): return jsonify({"message": "No se proporcionó contraseña."}), 400;
    
    #check if user exits
    user = User.query.filter_by(nickname=username).first();
    if (not user): return jsonify({"message": "El usuario no existe."}), 404;  

    # check user pass & return access_token
    if user and bcrypt.check_password_hash(user.password, password): 
        access_token = create_access_token(identity=user.id);
        return jsonify({
            "message": "Logged successfully",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.nickname,
                "email": user.email,
                "image": user.imageProfile,
                "bank": user.bank,
            }}), 200;
    else:
        return jsonify({ "message": "La contraseña no es correcta. Inténtelo de nuevo." }), 401;


#===: Handle forgot password ===:
@user_api_blueprint.route("/api/reset_password", methods=["POST"])
def reset_password_request():
    
    data = request.get_json();
    email = data.get("email");
    user = User.query.filter_by(email=email).first();
    
    if user: 
        token = user.get_reset_password_token();
        print(token);
        send_reset_email(user, token);
        return jsonify(message="Petición enviada correctamente. Revisa el código de confirmación que enviamos a tu correo electrónico."), 200;
    else:
        return jsonify(message="El correo electrónico ingresado no existe."), 400;       
    
def send_reset_email(user, token):
    msg = Message(
            'Restablecer contraseña | TumiPalace',
            sender='tumipalace@gmail.com',
            recipients=[user.email]);
    msg.html = f'''
    <h1>Restablecimiento de contraseña</h1>
    <p>Hola,</p>
    <p>Recibimos una solicitud para restablecer tu contraseña. Si tú hiciste esta solicitud, haz clic en el siguiente enlace para restablecer tu contraseña:</p>
    <p><a target="_BLANK" href="http://127.0.0.1:8080/reset_password/{token}">Cambiar contraseña</a></p>
    <p>El token expira en 10 minutos. Si tú no realizaste la solicitud de cambio de contraseña, ignora este correo electrónico.</p>
    <p>Saludos,</p>
    <p>El equipo de TumiPalace Perú.</p>
    '''
    mail.send(msg);

#===: Handle password reset as email link ===:
@user_api_blueprint.route("/api/reset_password/<token>", methods=["POST"])
def reset_password(token):
    user = User.verify_reset_password_token(token);
    if not user: return jsonify(message="El token es inválido o ya expiró."), 400
    
    data = request.get_json();
    password = data.get("password");
    
    # si la contraseña es la misma que la anterior no se actualiza
    if bcrypt.check_password_hash(user.password, password): return jsonify(message="La contraseña es la misma que la anterior."), 400;
    
    # encrypt password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8');
    user.password = hashed_password;
    user.reset_password_token = None
    user.reset_password_token_expires_at = None
    db.session.commit();
    return jsonify(message="La contraseña se actualizó exitosamente."), 200;

#===: Handle static image ===:
@user_api_blueprint.route("/api/<path:path>")
def serve_file(path):
    absolute_path = os.path.join(os.getcwd(), path)
    if path.endswith(".png"):
        return send_file(absolute_path, mimetype='image/png')
    if path.endswith(".jpg"):
        return send_file(absolute_path, mimetype='image/jpg')
    elif path.endswith(".mp3"):
        return send_file(absolute_path, mimetype='audio/mpeg')
    else:
        return "File type not supported", 400

#===: Handle update account ===:
@user_api_blueprint.route("/api/users/<user_id>", methods=["PUT", "GET"])
def update_user(user_id):
    user = User.query.get(user_id);
    if not user: return jsonify({"message": "El usuario no fue encontrado."}), 404

    if 'username' in request.form:
        new_username = request.form['username']
        
        if " " in new_username: return jsonify({"message": "El nombre de usuario no puede contener espacios."}), 400
        if (new_username == user.nickname): return jsonify({"message": "El nombre de usuario debe ser distinto al actual."}), 400
        if (User.query.filter_by(nickname=new_username).first()): return jsonify({"message": "El nombre de usuario ya se encuentra asociado a otra cuenta."}), 400
        user.nickname = new_username if new_username else user.nickname

    if 'email' in request.form:
        new_email = request.form['email']
        if (new_email == user.email): return jsonify({"message": "El correo electrónico debe ser distinto al actual."}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email): return jsonify({"message": "El correo electrónico es inválido."}), 400;
        if (User.query.filter_by(email=new_email).first()): return jsonify({"message": "El correo electrónico ya se encuentra asociado a otra cuenta."}), 400
        user.email = new_email if new_email else user.email

    if 'imageProfile' in request.files:
        new_image = request.files['imageProfile']
        
        user_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], user_id) 
        if not os.path.exists(user_dir): os.makedirs(user_dir);
        
        filename = secure_filename(new_image.filename);
        current_image_path = user.imageProfile;
        
        if current_image_path and os.path.isfile(current_image_path): os.remove(current_image_path)
                    
        # convertir a png y guardar
        img = Image.open(new_image)
        user_image_path = os.path.join(user_dir, filename)
        img.convert('RGBA').save(user_image_path, "PNG")
        
        user.imageProfile = user_image_path;

    db.session.commit()

    return jsonify(user.serialize()), 200;


#===: Handle delete account ===:
@user_api_blueprint.route("/api/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id);
    if not user: return jsonify({"message": "El usuario no fue encontrado."}), 404

    # verificar contraseña
    data = request.get_json();
    password = data.get("password");
    
    if not bcrypt.check_password_hash(user.password, password): return jsonify(message="La contraseña es incorrecta."), 401;

    # eliminar media del usuario
    user_folder = os.path.join(current_app.static_folder, 'user', user_id)
    if os.path.exists(user_folder): shutil.rmtree(user_folder)

    db.session.delete(user);
    db.session.commit();

    return jsonify({"message": "El usuario fue eliminado exitosamente. Redirigiéndote al inicio en 3 segundos..."}), 200


#===: Handle change password ===:
@user_api_blueprint.route("/api/users/<user_id>/change_password", methods=["POST"])
@jwt_required()
def change_password(user_id):
    user = User.query.get(user_id)
    if not user: return jsonify({"message": "El usuario no fue encontrado."}), 404

    data = request.get_json();
    password = data.get("password");
    new_password = data.get("new_password");
    
    if (not password): return jsonify({"message": "No se proporcionó contraseña actual."}), 400;
    if not bcrypt.check_password_hash(user.password, password): return jsonify({"message": "Contraseña actual incorrecta."}), 401
    if bcrypt.check_password_hash(user.password, new_password): return jsonify({"message": "La nueva contraseña debe ser diferente de la actual."}), 400

    if (not new_password): return jsonify({"message": "No se proporcionó nueva contraseña."}), 400;
    if len(new_password) < 5: return jsonify({"message": "La contraseña debe tener como mínimo 5 carácteres."}), 400;
    if " " in new_password: return jsonify({"message": "La contraseña no puede contener espacios."}), 400;
    
    # Cambiar la contraseña
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8');
    user.password = hashed_password;
    db.session.commit()

    return jsonify({"message": "La contraseña ha sido cambiada exitosamente."}), 200


#===: Update user bank :===
@user_api_blueprint.route('/api/users/<user_id>/update_balance', methods=['POST'])
@jwt_required()
def update_balance(user_id):
    data = request.get_json()
    new_balance = data.get('balance')

    user = User.query.get(user_id)
    print(user);
    if not user: return jsonify({"message": "Usuario no encontrado"}), 404
    if not new_balance: return jsonify({"message": "No se proporcionó un nuevo balance"}), 400
    if new_balance < 0: return jsonify({"message": "El balance no puede ser negativo"}), 400

    user.bank = new_balance;
    db.session.commit();
    return jsonify({"message": "Balance actualizado exitosamente"}), 200


#===: Handle transactions ===:
@user_api_blueprint.route('/api/add_funds', methods=['POST'])
@jwt_required()
def add_funds():
    try:
        user_id = get_jwt_identity();
        amount = request.json.get('amount')

        if not user_id: return jsonify({"message": "Usuario no encontrado."}), 404
        if not amount: return jsonify({"message": "No se proporcionó una cantidad."}), 400
        if amount <= 0: return jsonify({"message": "La cantidad no puede ser igual o menor que 0."}), 400
        if not isinstance(amount, (int, float)) or amount < 0.50: return jsonify({'error': 'La cantidad debe ser un número mayor o igual a 0.50'}), 400

        # intencion de pago
        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency='pen',
            description='Abono de tokens | TumiPalace',
            metadata={'user_id': user_id}
        );
        return jsonify({'clientSecret': intent['client_secret']})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 403;


#===: Handle example protected ===:
@user_api_blueprint.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200;

