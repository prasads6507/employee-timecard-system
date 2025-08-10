from app import app, db, User

def add_user():
    with app.app_context():
        username = input("Enter new username: ")
        password = input("Enter password: ")
        role = input("Enter role (employee/admin): ").strip().lower()

        # Validate role
        if role not in ['employee', 'admin']:
            print("❌ Invalid role. Use 'employee' or 'admin'.")
            return

        # Check if username already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print("❌ User already exists.")
            return

        # Add user
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        print(f"✅ User '{username}' added successfully with role '{role}'.")

if __name__ == '__main__':
    add_user()
