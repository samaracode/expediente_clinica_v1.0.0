from app.db.session import SessionLocal
from app.models.user import User, TreatmentArea, UserRole
from app.core.security import get_password_hash


def seed():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@zoe.clinica").first():
            admin = User(
                full_name="Administrador ZOE",
                email="admin@zoe.clinica",
                hashed_password=get_password_hash("Admin1234!"),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(admin)
            print("✓ Usuario admin creado: admin@zoe.clinica / Admin1234!")
        else:
            print("  Usuario admin ya existe, omitiendo.")

        areas = [
            ("medicine", "Área Médica"),
            ("therapeutic", "Área Terapéutica"),
            ("social_work", "Trabajo Social"),
            ("psychology", "Psicología"),
            ("occupational_therapy", "Terapia Ocupacional"),
        ]
        created = 0
        for name, description in areas:
            if not db.query(TreatmentArea).filter(TreatmentArea.name == name).first():
                db.add(TreatmentArea(name=name, description=description))
                created += 1
        if created:
            print(f"✓ {created} áreas de tratamiento creadas.")
        else:
            print("  Áreas de tratamiento ya existen, omitiendo.")

        db.commit()
        print("\nSeed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
