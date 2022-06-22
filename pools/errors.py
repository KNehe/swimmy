booking_error_text = (
    "You have already booked this pool." + "Request an update if required"
)
BOOKING_INTEGRITY_ERROR = {"Integrity error": booking_error_text}

UNKOWN_USER_ERROR = {"detail": "Request for unknown user"}
USER_FOR_EMAIL_NOT_FOUND_ERROR = "User for email not found"

rating_error_text = "Already rated! request update to make changes"
RATING_INTEGRITY_ERROR = {"Integrity Error": rating_error_text}

REQUEST_PASSWORD_RESET_ERROR = {
    "message": "An error occurred while\
                                    sending email, try again later"
}

START_DATE_PAST_ERROR = "Start date can not be past"
END_DATE_PAST_ERROR = "End date can not be past"
START_DATE_ERROR = "Start date must be less than or equal to end date"

INVALID_REQUEST_ERROR = {"detail": "Invalid request"}
INVALID_RESET_LINK = {"detail": "Reset link is now invalid"}
