import streamlit as st
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_db_connection

def send_reset_email(email, reset_code):
    # Email credentials
    sender_email = "patrick8200402@gmail.com"
    password = "dulg zfxo qebd thbe"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Heartistry - Password Reset"
    
    # Create HTML body with the reset code
    body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #e63946;">Heartistry Password Reset</h2>
            <p>You requested a password reset for your Heartistry account.</p>
            <p>Your password reset code is: <strong style="font-size: 18px; background-color: #f8f9fa; padding: 5px 10px; border-radius: 3px;">{reset_code}</strong></p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>Best regards,<br>The Heartistry Team</p>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def generate_reset_code():
    """Generate a random 6-digit reset code"""
    return ''.join(random.choices(string.digits, k=6))

def check_email_exists(email):
    """Check if email exists in the database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user

def update_password(email, new_password):
    """Update user password in database"""
    import bcrypt  # Import here to avoid circular import
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    
    # Update the user's password
    query = "UPDATE users SET password=%s WHERE email=%s"
    cursor.execute(query, (hashed_password.decode(), email))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return True


if "user" in st.session_state:
    st.session_state["notices"] = ["You are already logged in"]
    st.switch_page("views/dashboard.py")

st.title("🔑 Forgot Password")

# Check if we're in reset code verification mode
if "reset_email" in st.session_state and "reset_code" in st.session_state:
    st.info(f"Enter the verification code sent to {st.session_state['reset_email']}")
    
    verification_code = st.text_input("Verification Code", key="verification_input")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button("Reset Password"):
        if verification_code != st.session_state["reset_code"]:
            st.error("❌ Invalid verification code!")
        elif new_password != confirm_password:
            st.error("❌ Passwords do not match!")
        elif len(new_password) < 6:
            st.error("❌ Password must be at least 6 characters long")
        else:
            # Update password in database
            if update_password(st.session_state["reset_email"], new_password):
                st.success("✅ Password reset successful!")
                # Clear reset state
                del st.session_state["reset_email"]
                del st.session_state["reset_code"]
                
                # Redirect to login after displaying success message
                st.info("Redirecting to login page...")
                st.rerun()  # Using st.rerun() instead of experimental_rerun
                st.switch_page("views/login.py")
            else:
                st.error("❌ Error updating password")
                
    if st.button("Back to Login"):
        # Clear reset state
        if "reset_email" in st.session_state:
            del st.session_state["reset_email"]
        if "reset_code" in st.session_state:
            del st.session_state["reset_code"]
        st.switch_page("views/login.py")
        
else:
    # Normal forgot password flow
    email = st.text_input("Enter your Email")
    
    if st.button("Send Reset Code"):
        if email.strip() == "":
            st.error("❌ Please enter your email address")
        else:
            user = check_email_exists(email)
            if user:
                # Generate reset code and store in session
                reset_code = generate_reset_code()
                st.session_state["reset_email"] = email
                st.session_state["reset_code"] = reset_code
                
                # Send email with reset code
                if send_reset_email(email, reset_code):
                    st.success("✅ Reset code sent to your email!")
                    st.rerun()  # Using st.rerun() instead of experimental_rerun
                else:
                    st.error("❌ Error sending reset code")
            else:
                st.error("❌ Email not found in our records")
                
    if st.button("Back to Login"):
        st.switch_page("views/login.py")