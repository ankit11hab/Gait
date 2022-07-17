from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_thumbnails import Thumbnail
# from flask_mail import Mail

# from dotenv import load_dotenv
# load_dotenv()



app = Flask(__name__)
app.config['SECRET_KEY'] = '25ee72345d734f45985acb78f8114c37'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
thumb = Thumbnail(app)

from flask_restful import Api, Resource


login_manager.login_view='login'
login_manager.login_message_category='info'
from application import routes
from application.models import Module, Pdf, Image, Video
api = Api(app)
class AddPdf(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        module_id = json_data['module_id']
        url = json_data['url']
        print(module_id, url)
        module = Module.query.get(module_id)
        pdf = Pdf(title="New PDF", pdf="-1", module=module, sharable_link=url)
        db.session.add(pdf)
        db.session.commit()
        return {"data":"fine"}

class AddImage(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        module_id = json_data['module_id']
        url = json_data['url']
        print(module_id, url)
        module = Module.query.get(module_id)
        image = Image(title="New Image", image="-1", module=module, sharable_link=url)
        db.session.add(image)
        db.session.commit()
        return {"data":"fine"}

class AddVideo(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        module_id = json_data['module_id']
        url = json_data['url']
        print(module_id, url)
        module = Module.query.get(module_id)
        video = Video(title="New Video", video="-1", module=module, sharable_link=url)
        db.session.add(video)
        db.session.commit()
        return {"data":"fine"}

api.add_resource(AddPdf, '/api/pdf')
api.add_resource(AddImage, '/api/image')