from app import app,socketio
from app.models import User, Checkup, Kidney, Liver

if __name__=="__main__":
    with app.app_context():
        users=User.query.all()
        checkups=Checkup.query.all()
        kidney=Kidney.query.all()
        liver=Liver.query.all()
        print(users)
        print(checkups)
        print(kidney)
        print(liver)
    socketio.run(app=app,debug=True)