from django.utils.translation import gettext_lazy as _


SUCCESS = "success"
STATUS = "status"
MESSAGE = "message"
ERROR = "error"
ERROR_MESSAGE = "error_message"
ERROR_OCCURED = "Error Occurred"
DATA = "data"
COUNT = "cpunt"
EMAIL = "email"
FORM = "form"
POST = "POST"
INVALID_REQUEST_METHOD = "Invalid request method."
INVALID_FORM_DATA = "Invalid form data."
TOKEN = "token"
USER = "user"
USER_ID = "user_id"
NEXT = "next"
PREVIOUS = "previous"
COUNT = "count"
IS_VERIFIED = "is_verified"
USER_NOT_REGISTERED = "You are not registered."
ACCESS_RESTRICTON = "Access restricted."
TOKEN_REQUIRED = "Token is required."
ACTIVE="active"
COMPLETE="complete"
PDF = "pdf"
DOC = "doc"
LINK = "link"
IMAGE = "mage"
VIDEO = "video"
TRUE = True
FALSE = False
AGENT = "agent"
ADVISIOR = "advisior"

# Auth
USER_NOT_FOUND = _("User not found.")
USER_NOT_ACTIVE = _("User not active.")
LOGIN_SUCCESS = _("You are logged in successfully.")
LOGOUT_SUCCESS = _("Logged out successfully.")
INVALID_LOGIN_DETAILS = _("Invalid login details.")
VERIFY_ACCOUNT_EMAIL_ADDRESS = _("Verify your email address to reset your password.")

# Superadmin Login
PROFILE_UPDATED_SUCCESS = _("Profile updated successfully.")
INVALID_PASSWORD = _("Invalid password.")
INVALID_OLD_PASSWORD = _("Invalid old password.")
LOGIN_ACCOUNT = _("Please log in to your account")
USER_CREATED_SUCCESS = _("User created successfully.")
USER_DELETED_SUCCESS = _("User deleted successfully.")
USER_STATUS_CHANGED_SUCCESS = _("User status updated successfully.")

# Email
EMAIL_SENT = _("Emails are being sent.")
EMAIL_AND_PASSWORD_REQUIRED = _("Email and password are required.")

# Success Messages
LOGIN_SUCCESS = _("You are logged in successfully.")
PASSWORD_CHANGED_SUCCESS = _("Password changed successfully.")
PASSWORD_NOT_CHANGED = _("Password not changed.")
PASSWORD_NOT_MATCHED = _("Password not matched.")
PASSWORD_RESET_SUCCESS = _("Password has been reset successfully.")
OLD_PASSWORD_INCORRECT = _("Old password is incorrect.")
NEW_CONFIRM_PASSWORD_INCORRECT = _("New password and confirm password do not match.")
PASSWORD_REQUIRED_FIELDS = _("All fields (old_password, new_password, confirm_password) are required.")
INCORRECT_BIOMETRIC_ID = _("Found error")
PROFILE_DATA_SUCCESS = _("Fetched profile data.")
PROFILE_DELETED_SUCCESS = _("Profile Deleted Successfully.")
PROFILE_CHANGED_SUCCESS = _("Profile updated successfully.")
PROFILE_NOT_UPDATED = _("Profile not updated.")
USER_CREATED_SUCCESS = _("User registered successfully.")
BLOCKED_USERS_LIST_SUCCESS = _("Fetched Blocked user list.")
EMAIL_SENT_SUCCESS = _("Email sent successfully.")
EMAIL_VERIFIED_SUCCESS = _("Email verified.")
EMAIL_ALREADY_VERIFIED_SUCCESS = _("Email Already verified.")
USER_LIST_SUCCESS = _("Fetched user list.")
USER_STATUS_CHANGED_SUCCESS = _("User status updated.")
LIST_FETCHED_SUCCESS = _("List fetched successfully.")
USER_REGISTERED_SUCCESS = _("User registered successfully.")
USER_DELETE_SUCCESS = _("User deleted successfully.")
USER_RATINGS_SUCCESS = _("Fetched user ratings.")
RATING_CREATED_SUCCESS = _("Added user rating.")
USER_BLOCKED_SUCCESS = _("User blocked successfully.")
USER_FOLLOWED_SUCCESS = _("User followed successfully.")
USER_VERIFICATION_SUCCESS = _("User verified successfully.")
TOKEN_SEND_EMAIL_SUCCESS = _("Password reset link sent successfully.")
REGISTER_EMAIL_ALREADY_EXISTS = _("Email already Exists.")
EMAIL_ALREADY_SENT_TO_VERIFY = _("Email already sent. Please check your email address.")
EMAIL_ALREADY_SENT = _("An OTP has already been sent to your email for account verification.")
IS_FOLLOWED = _("is_followed")
IS_LIKED = _("is_liked")
LOGOUT_SUCCESSFULLY = _("User logged out successfully.")
EMAIL_IS_AVAILABLE = _("Email is available to use.")
USERNAME_IS_AVAILABLE = _("Username is available to use.")
OTP_SEND_SUCCESS = _("Otp has been sent on your email.")
OTP_NOT_VALID = _("Invalid otp")
CONTACT_EMAIL_SENT_SUCCESS = _("Your message has been received.")
SEND_OTP = _("send_otp")
VERIFY_OTP = _("verify_otp")
RESET_PASSWORD = _("reset_password")
RESEND_OTP = _("resend_otp")
OTP_VERIFIED = _("OTP verifed successfully.")
INVALID_OTP = _("Invalid OTP")
OTP_SENT_SUCCESS = _("An OTP has been sent on your email.")
ACCOUNT_EXISTS_OTP_SENT_SUCCESS = _("Email already exists. An OTP has been sent on your email.")

# Error Messages
INVALID_LOGIN_CREDENTIALS = _("Invalid login details.")
INCORRECT_OLD_PASSWORD = _("Incorrect old password.")
EMAIL_SEND_SUCCESS = _("Email sent successfully.")
EMAIL_OTP_RESEND_SUCCESS = _("OTP sent successfully.")
USER_CREATED_SUCCESS = _("Account Created Successfully! We've sent a confirmation email. Please check your inbox.")
EMAIL_SEND_FAILED = _("Email not sent.")
EMAIL_VERIFIED_FAILED = _("Email not verified.")
EMAIL_REQUIRED = _("Email is required.")
TOKEN_EXPIRED = _("Token has expired.")
INVALID_TOKEN = _("Invalid token.")
VALID_TOKEN = _("Token is valid.")
FAILED_FIREBASE_AUTHENTICATION = _("Unable to authenticate token.")
USER_UNBLOCKED_SUCCESS = _("User unblocked successfully.")
USER_UNFOLLOWED_SUCCESS = _("User unfollowed successfully.")
USER_NOT_FOUND = _("User not found.")
EMAIL_NOT_AVAILABLE = _("Email is already taken.")
EMAIL_ALREADY_EXISTS = _("Account is already exist. Need to verify your account.")
USERNAME_NOT_AVAILABLE = _("Username is already taken.")
EMAIL_GENERATION_FAILED = _("Otp generation failed.")
EMAIL_SENT_FAILED = _("There was an error sending Email. Please try again.")
INCORRECT_USERNAME_EMAIL_PASSWORD = _("Incorrect username/email or password.")
USER_IS_INACTIVE = _("User is inactive.")
USER_IS_UNVERIFIED = _("User is not verified.")
TOKEN_SEND_EMAIL_FAILED = _("An error occurred while sending email. Please try again.")
ACCESS_DENIED = _("You do not have permission to access this resource.")
INVALID_ATTACHMENT = _("Attachment file not found.")
INVALID_SELLER_BUYER_ID = _("Invalid seller & buyer id.")
PASSWORD_REQUIRED_FIELDS = _("Please enter both password fields.")
PASSWORD_NOT_MATCHED = _("Passwords do not match.")
PASSWORD_CHANGED_SUCCESS = _("Your password has been changed successfully.")

# Validation Messages
INVALID_EMAIL = _("Invalid email.")
OTP_EXPIRED = _("OTP has expired.")
INVALID_PHONE_NUMBER = _("Invalid phone number.")
USER_ALREADY_EXISTS = _("User with this phone number already exists.")
INVALID_EMAIL_PASSWORD = _("Invalid Email & Password.")
EMAIL_DOES_NOT_EXIST = _("Email does not exists.")
INVALID_USERNAME = _("Invalid Username.")
INVALID_PASSWORD = _("Invalid Password.")
INVALID_STATUS = _("Invalid Status.")
INVALID_FIREBASE_TOKEN = _("Firebase token is required.")
INVALID_SOCIAL_TYPE = _("Social type can be facebook or google.")
INVALID_RATED_USER = _("Invalid rated user id.")
INVALID_RATING_USER = _("Invalid rating.")
INVALID_REVIEW_USER = _("Invalid review.")
INVALID_MESSAGE = _("Invalid message.")
PASSWORD_CODE_SEND_SUCCESS = _("Verification code has been sent to your email account.")
TOKEN_SEND_EMAIL_FAILED = _("An error occurred while sending email. Please try again.")

# Other Messages
DATA_INFO_SUCCESS = _("Data fetched successfully.")

# Setting
SETTING_CREATED_SUCCESS = _("Setting Created successfully.")
SETTING_NOT_CREATED = _("Setting not Created Successfully.")

# Resources
RESOURCES_CREATED_SUCCESS = _("Resource Created successfully.")
RESOURCES_NOT_CREATED = _("Resource not Created Successfully.")
RESOURCES_DELETED_SUCCESS = _("Resource deleted successfully.")
RESOURCES_NOT_DELETED = _("Resource not deleted.")
RESOURCES_UPDATED_SUCCESS = _("Resource updated successfully.")
RESOURCES_NOT_UPDATED = _("Resource not updated.")
RESOURCES_NOT_FOUND = _("Resource not found.")
RESOURCES_LIST_SUCESS = _("Resources retrieved successfully.")

# Languages
LANGUAGE_CREATED_SUCCESS = _("Language Created successfully.")
LANGUAGE_NOT_CREATED = _("Language not Created Successfully.")
LANGUAGE_DELETED_SUCCESS = _("Language deleted successfully.")
LANGUAGE_NOT_DELETED = _("Language not deleted.")
LANGUAGE_UPDATED_SUCCESS = _("Language updated successfully.")
LANGUAGE_NOT_UPDATED = _("Language not updated.")
LANGUAGE_NOT_FOUND = _("Language not found.")
LANGUAGE_LIST_SUCESS = _("Language retrieved successfully.")

# Rooms
ROOMS_CREATED_SUCCESS = _("Room Created successfully.")
ROOMS_NOT_CREATED = _("Room not Created Successfully.")
ROOMS_DELETED_SUCCESS = _("Room deleted successfully.")
ROOMS_NOT_DELETED = _("Room not deleted.")
ROOMS_UPDATED_SUCCESS = _("Room updated successfully.")
ROOMS_NOT_UPDATED = _("Room not updated.")
ROOMS_NOT_FOUND = _("Room not found.")
ROOMS_LIST_SUCESS = _("Rooms retrieved successfully.")

# Messages
MESSAGES_NOT_FOUND = _("Messages not found.")
MESSAGES_LIST_SUCESS = _("Messages retrieved successfully.")