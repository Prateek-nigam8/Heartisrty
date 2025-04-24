import argparse
import subprocess
from db import get_db_connection
from create_admin import create_admin_user


def install_dependencies():
    print("📦 Installing required packages from requirements.txt...")
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please check requirements.txt and your environment.")


def setup_database(force=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    if force:
        print("⚠️ Dropping existing database 'heartistry'...")
        cursor.execute("DROP DATABASE IF EXISTS heartistry")

    print("✅ Creating database...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS heartistry")
    cursor.execute("USE heartistry")

    print("✅ Creating 'users' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin TINYINT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("✅ Creating 'heart_patient_data' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heart_patient_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Age INT NOT NULL,
            Sex ENUM('Male','Female') NOT NULL,
            ChestPainType ENUM('Typical Angina','Atypical Angina','Non-Anginal Pain','Asymptomatic') NOT NULL,
            RestingBP INT NOT NULL,
            Cholesterol INT NOT NULL,
            FastingBS FLOAT NOT NULL,
            RestingECG ENUM('Normal','ST-T Wave Abnormality','Left Ventricular Hypertrophy') NOT NULL,
            MaxHR INT NOT NULL,
            ExerciseAngina ENUM('Yes','No') NOT NULL,
            Oldpeak FLOAT NOT NULL,
            ST_Slope ENUM('Upsloping','Flat','Downsloping') NOT NULL,
            sos_emergency_mail VARCHAR(255) NOT NULL,
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("🎉 Database and tables created successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up the heartistry database and tables.")
    parser.add_argument("--force", action="store_true", help="Drop and recreate database and tables.")
    args = parser.parse_args()

    install_dependencies()
    setup_database(force=args.force)
    create_admin_user()
