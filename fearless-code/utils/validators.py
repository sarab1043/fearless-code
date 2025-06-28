# Format Validation Errors
def format_validation_errors(serializer):
    try:
        error_messages = []
        for field, errors in serializer.errors.items():
            field = field.replace('_', ' ')
            for error in errors:
                error_messages.append(f"{field.upper()}: {str(error)}")
        errors = " ".join(error_messages)
        return errors
    except Exception as ex:
        return None
