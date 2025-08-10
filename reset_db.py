from app import app, db, User

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username='admin', password='adminpass', role='admin')
    emp1 = User(username='employee1', password='pass123', role='employee')
    emp2 = User(username='employee2', password='pass456', role='employee')

    db.session.add_all([admin, emp1, emp2])
    db.session.commit()

    print("✅ Test users created successfully.")
