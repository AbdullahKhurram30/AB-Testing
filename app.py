from app import app, db, login_manager
from app.routes import User, Donation

if __name__ == '__main__':
    app.run(debug=True)