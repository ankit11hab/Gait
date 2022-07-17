from application import app, bcrypt, db
from .models import Pdf, User, Module, Image, Video
from flask import flash, redirect, render_template, request, abort
from .forms import ImageForm, ModuleForm, PdfForm, RegistrationForm, LoginForm, VideoForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import secrets, os
from werkzeug.utils import secure_filename
import uuid


# Registration Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account has been successfully created', 'success')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect('login')
    return render_template('form.html', legend='Sign Up', title = 'Register', type='register', form=form)

# Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('form.html', legend='Sign In', title = 'Login', type='login', form=form)


# API Login
@app.route("/api/login/<string:username>/<string:password>", methods=['GET', 'POST'])
def api_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return {
            "id":user.id
        }
    return {
        "id":-1
    }


# Logout Page
@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


# Modules Page
@app.route("/")
@login_required
def module():
    return render_template('main/modules.html', title = 'Modules')


# Modules API
@app.route("/api/modules/<int:user_id>")
@login_required
def api_module(user_id):
    user = User.query.get(user_id)
    options = []
    for module in user.modules:
        options.append({
            "module_title": module.title,
            "module_id": module.id
        })
    return {"data": options}


# Add New Module
@app.route("/module/new", methods=['GET', 'POST'])
@login_required
def new_module():
    form = ModuleForm()
    if form.validate_on_submit():
        module_uuid = str(uuid.uuid4())
        link = request.url_root+'shared/module/'+module_uuid
        module = Module(title=form.title.data, module_uuid=module_uuid, sharable_link=link, user=current_user)
        db.session.add(module)
        db.session.commit()
        return redirect('/')
    return render_template('form.html', title = 'New Module', legend="Add New Module", type='crud', form = form)


# Add New Module
@app.route("/module/<module_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    module = Module.query.get(module_id)
    form = ModuleForm()
    if form.validate_on_submit():
        module.title = form.title.data
        db.session.commit()
        return redirect('/')
    form.title.data = module.title
    return render_template('form.html', title = 'Edit Module', legend="Edit Module", type='crud', form = form)


# Delete Module
@app.route("/module/<int:module_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_module_del(module_id):
    module = Module.query.get_or_404(module_id)
    if module.user != current_user:
        abort(403)
    pdfs = Pdf.query.filter_by(module=module).all()
    images = Image.query.filter_by(module=module).all()
    videos = Video.query.filter_by(module=module).all()
    for pdf in pdfs:
        db.session.delete(pdf)
    for image in images:
        db.session.delete(image)
    for video in videos:
        db.session.delete(video)
    db.session.delete(module)
    db.session.commit()
    return redirect('/')


# Modules Page
@app.route("/module/<int:module_id>")
@login_required
def module_details(module_id):
    module = Module.query.get(module_id)
    return render_template('main/module_details.html', title = module.title, module=module, type='crud')


# Shared Modules Page
@app.route("/shared/module/<module_uuid>")
def shared_module_details(module_uuid):
    module = Module.query.filter_by(module_uuid=module_uuid).first()
    return render_template('main/module_details.html', title = module.title, module=module, type='view')


# Add New PDF
@app.route("/module/<int:module_id>/pdf/new", methods=['GET', 'POST'])
@login_required
def new_pdf(module_id):
    module = Module.query.get(module_id)
    form = PdfForm()
    if form.validate_on_submit():
        if form.pdf.data:
            uploads_dir = os.path.join(app.root_path , 'static/pdfs')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.pdf.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            pdf = Pdf(title=form.title.data, pdf=filename, module=module, sharable_link=request.url_root + 'static/pdfs/'+filename)
            db.session.add(pdf)
            db.session.commit()
            return redirect('/module/'+str(module_id))
    return render_template('form.html', title = 'New PDF', legend="Add New PDF", type='crud', form = form)


# Add PDF API
# @app.route("/api/pdf/<int:module_id>/<string:link>", methods=['GET', 'POST'])
# @login_required
# def api_new_pdf(module_id, link):
#     module = Module.query.get(module_id)
#     pdf = Pdf(title="New PDF", pdf="-1", module=module, sharable_link=link)
#     db.session.add(pdf)
#     db.session.commit()
#     return "Added"


# Edit PDF
@app.route("/pdf/<int:pdf_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_pdf(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    if pdf.module.user != current_user:
        abort(403)
    form = PdfForm()
    if form.validate_on_submit():
        pdf.title = form.title.data
        if form.pdf.data:
            uploads_dir = os.path.join(app.root_path , 'static/pdfs')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.pdf.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            pdf.pdf = filename
            pdf.sharable_link = request.url_root + 'static/pdfs/'+filename
        db.session.commit()
        return redirect('/module/'+str(pdf.module.id))
    form.title.data = pdf.title
    form.pdf.data = pdf.pdf
    return render_template('form.html', title = 'Edit Pdf', legend="Edit PDF", type='crud', form = form)

# Delete PDF
@app.route("/pdf/<int:pdf_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_pdf_del(pdf_id):
    pdf = Pdf.query.get_or_404(pdf_id)
    if pdf.module.user != current_user:
        abort(403)
    db.session.delete(pdf)
    db.session.commit()
    return redirect('/module/'+str(pdf.module.id))


# Add New Image
@app.route("/module/<int:module_id>/image/new", methods=['GET', 'POST'])
@login_required
def new_image(module_id):
    module = Module.query.get(module_id)
    form = ImageForm()
    if form.validate_on_submit():
        if form.image.data:
            uploads_dir = os.path.join(app.root_path , 'static/images')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.image.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            image = Image(title=form.title.data, image=filename, module=module, sharable_link=request.url_root + 'static/images/'+filename)
            db.session.add(image)
            db.session.commit()
            return redirect('/module/'+str(module_id))
    return render_template('form.html', title = 'New Image', legend="Add New Image", type='crud', form = form)


# Edit Image
@app.route("/image/<int:image_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_image(image_id):
    image = Image.query.get_or_404(image_id)
    if image.module.user != current_user:
        abort(403)
    form = ImageForm()
    if form.validate_on_submit():
        image.title = form.title.data
        if form.image.data:
            uploads_dir = os.path.join(app.root_path , 'static/images')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.image.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            image.image = filename
            image.sharable_link = request.url_root + 'static/images/'+filename
        db.session.commit()
        return redirect('/module/'+str(image.module.id))
    form.title.data = image.title
    form.image.data = image.image
    return render_template('form.html', title = 'Edit Image', legend="Edit Image", type='crud', form = form)

# Delete Image
@app.route("/image/<int:image_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_image_del(image_id):
    image = Image.query.get_or_404(image_id)
    if image.module.user != current_user:
        abort(403)
    db.session.delete(image)
    db.session.commit()
    return redirect('/module/'+str(image.module.id))


# Add New Video
@app.route("/module/<int:module_id>/video/new", methods=['GET', 'POST'])
@login_required
def new_video(module_id):
    module = Module.query.get(module_id)
    form = VideoForm()
    if form.validate_on_submit():
        if form.video.data:
            uploads_dir = os.path.join(app.root_path , 'static/videos')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.video.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            video = Video(title=form.title.data, video=filename, module=module, sharable_link=request.url_root + 'static/videos/'+filename)
            db.session.add(video)
            db.session.commit()
            return redirect('/module/'+str(module_id))
    return render_template('form.html', title = 'New Video', legend="Add New Video", type='crud', form = form)


# Edit Video
@app.route("/video/<int:video_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.module.user != current_user:
        abort(403)
    form = VideoForm()
    if form.validate_on_submit():
        video.title = form.title.data
        if form.video.data:
            uploads_dir = os.path.join(app.root_path , 'static/videos')
            os.makedirs(uploads_dir, exist_ok=True)
            file = form.video.data
            filename = secure_filename(str(uuid.uuid4())+file.filename)
            file.save(os.path.join(uploads_dir, filename))
            video.video = filename
            video.sharable_link = request.url_root + 'static/videos/'+filename
        db.session.commit()
        return redirect('/module/'+str(video.module.id))
    form.title.data = video.title
    form.video.data = video.video
    return render_template('form.html', title = 'Edit Video', legend="Edit Video", type='crud', form = form)

# Delete Video
@app.route("/video/<int:video_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_video_del(video_id):
    video = Image.query.get_or_404(video_id)
    if video.module.user != current_user:
        abort(403)
    db.session.delete(video)
    db.session.commit()
    return redirect('/module/'+str(video.module.id))