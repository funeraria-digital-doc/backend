from django.core.exceptions import ValidationError

def required_or_override(data_keys, key, is_optional, is_field_custom, errors):
    if key not in data_keys and (not is_optional and is_field_custom):
        errors[key] = "the field " + key + " is required"
    if key in data_keys and not is_field_custom:
        errors[key] = "You can not override the field " + key

def check_for_not_acceptable_keys(data_keys,validation_keys,errors):
    for data_key in data_keys:
        if data_key not in validation_keys:
            errors[data_key] = "Key not acceptable"

def validate_text_fields(data_key, errors, key, is_optional,min,max):
    if ((is_optional and data_key) or not is_optional) and min is not None and min > 0 and len(data_key.strip()) < min:
        if key not in errors:
            errors[key] = {}
        errors[key]['min'] = "Text too short"
    if max is not None and max > 0 and len(data_key.strip()) > max:
        if key not in errors:
            errors[key] = {}
        errors[key]['max'] = "Text too long"
    
def validate_email_field(data_key, errors, key):
    from django.core.validators import validate_email 
    try:
        validate_email(data_key)
    except ValidationError as e:
        errors[key] = e
        print("bad email, details:", e)

def validate_select_field(data_key, errors, key, options_json):
    options = dict(options_json)
    list_options = options.get('options')
    if list_options is None or len(list_options) == 0:
        errors[key] = "Template options not provided. Please Contact an administrator"
    else:
        has_key = False
        for option in list_options:
            if data_key == option.get('value'):
                has_key = True
        if not has_key:
            errors[key] = "Option " + data_key + " is not valid"

def validate_multiselect_field(data_key, errors, key, options_json, min, max):
    options = dict(options_json)
    list_options = options.get('options')
    if list_options is None or len(list_options) == 0:
        errors[key] = "Template options not provided. Please Contact an administrator"
    else:
        selected_options = list(set(data_key))
        valid_selected_options = 0
        if len(data_key) > len(selected_options):
            if key not in errors:
                errors[key] = {}
            errors[key]['duplicated'] = "Duplicated options selected"
        for selected_option in selected_options:
            has_key = False
            for option in list_options:
                if selected_option == option.get('value') :
                    has_key = True
            if not has_key:
                if key not in errors:
                    errors[key] = {}
                errors[key][selected_option] = "Option " + selected_option + " is not valid"
            else:
                valid_selected_options = valid_selected_options + 1
        if min is not None and min > 0 and valid_selected_options < min:
            if key not in errors:
                    errors[key] = {}
            errors[key]['min'] = "Not enough options selected"
        if max is not None and max > 0 and valid_selected_options > max:
            if key not in errors:
                errors[key] = {}
            errors[key]['max'] = "Too many options selected"

def validate_date_fields(data_key, errors, key, date_format):
    from datetime import datetime
    if date_format == "DAY_MONTH_YEAR_HOUR_MINUTE_SECOND":
        try:
            datetime.strptime(data_key, "%d/%m/%Y %H:%M:%S")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH/YEAR HOURS:MINUTES:SECONDS format. Example: 20/03/2023 23:59:59"
    if date_format == "DAY_MONTH_YEAR_HOUR_MINUTE":
        try:
            datetime.strptime(data_key, "%d/%m/%Y %H:%M")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH/YEAR HOURS:MINUTES format. Example: 20/03/2023 23:59"
    if date_format == "DAY_MONTH_YEAR_HOUR":
        try:
            datetime.strptime(data_key, "%d/%m/%Y %H")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH/YEAR HOURS format. Example: 20/03/2023 23"

    if date_format == "DAY_MONTH_HOUR_MINUTE_SECOND":
        try:
            datetime.strptime(data_key, "%d/%m %H:%M:%S")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH HOURS:MINUTES:SECONDS format. Example: 20/03 23:59:59"
    if date_format == "DAY_MONTH_HOUR_MINUTE":
        try:
            datetime.strptime(data_key, "%d/%m %H:%M")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH HOURS:MINUTES format. Example: 20/03 23:59"
    if date_format == "DAY_MONTH_HOUR":
        try:
            datetime.strptime(data_key, "%d/%m %H")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH HOURS format. Example: 20/03 23"
    if date_format == "MONTH_YEAR_HOUR_MINUTE_SECOND":
        try:
            datetime.strptime(data_key, "%m/%Y %H:%M:%S")
        except ValueError as e:
            errors[key] = "Given data is not in a valid MONTH/YEAR HOURS:MINUTES:SECONDS format. Example: 03/2023 23:59:59"
    if date_format == "MONTH_YEAR_HOUR_MINUTE":
        try:
            datetime.strptime(data_key, "%m/%Y %H:%M")
        except ValueError as e:
            errors[key] = "Given data is not in a valid MONTH/YEAR HOURS:MINUTES format. Example: 03/2023 23:59"
    if date_format == "MONTH_YEAR_HOUR":
        try:
            datetime.strptime(data_key, "%m/%Y %H")
        except ValueError as e:
            errors[key] = "Given data is not in a valid MONTH/YEAR HOURS format. Example: 03/2023 23"
    if date_format == "HOURS_ONLY":
        try:
            if int(data_key) < 0 or int(data_key) > 23:
                errors[key] = "Invalid Hour. Must be between 0 and 23"
        except ValueError as e:
            errors[key] = "Value must be between 0 and 23"
    if date_format == "MINUTES_ONLY":
        try:
            if int(data_key) < 0 or int(data_key) > 23:
                errors[key] = "Invalid Minutes. Must be between 0 and 59"
        except ValueError as e:
            errors[key] = "Value must be between 0 and 59"
    if date_format == "SECONDS_ONLY":
        try:
            if int(data_key) < 0 or int(data_key) > 23:
                errors[key] = "Invalid Seconds. Must be between 0 and 59"
        except ValueError as e:
            errors[key] = "Value must be between 0 and 59"
    if date_format == "HOURS_MINUTES_SECONDS":
        try:
            datetime.strptime(data_key, "%H:%M:%S")
        except ValueError as e:
            errors[key] = "Given time is not in a valid HOURS:MINUTES:SECONDS format. Example: 23:59:59"
    if date_format == "HOURS_MINUTES":
        try:
            datetime.strptime(data_key, "%H:%M")
        except ValueError as e:
            errors[key] = "Given time is not in a valid HOURS:MINUTES format. Example: 23:59"
    if date_format == "MINUTES_SECONDS":
        try:
            datetime.strptime(data_key, "%M:%S")
        except ValueError as e:
            errors[key] = "Given time is not in a valid MINUTES:SECONDS format. Example: 59:59"
    if date_format == "DAY_MONTH":
        try:
            datetime.strptime(data_key, "%d/%m")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH format. Example: 20/03"
    if date_format == "MONTH_YEAR":
        try:
            datetime.strptime(data_key, "%m/%Y")
        except ValueError as e:
            errors[key] = "Given data is not in a valid MONTH/YEAR format. Example: 03/2023"
    if date_format == "DAY_MONTH_YEAR":
        try:
            datetime.strptime(data_key, "%d/%m/%Y")
        except ValueError as e:
            errors[key] = "Given data is not in a valid DAY/MONTH/YEAR format. Example: 20/03/2023"

def validate_year_field(data_key, errors, key):
    import datetime
    now_year = datetime.date.today().year
    try:
        if int(data_key) < (now_year - 100) or int(data_key) > (now_year + 100):
            errors[key] = "Invalid Year. Must be between %s and %s" % (str(now_year - 100), str(now_year + 100))
    except ValueError as e:
        errors[key] = "Value must be between "+str(now_year - 100)+" and " + str(now_year + 100)

def validate_month_field(data_key, errors, key):
    try:
        if int(data_key) < 1 or int(data_key) > 12:
            errors[key] = "Invalid Month. Must be between 1 and 12"
    except ValueError as e:
        errors[key] = "Value must be between 1 and 12"

def validate_day_field(data_key, errors, key):
    try:
        if int(data_key) < 1 or int(data_key) > 31:
            errors[key] = "Invalid Year. Must be between 1 and 31"
    except ValueError as e:
        errors[key] = "Value must be between 1 and 31"

def validate_boolean_field(data_key, errors, key):
    if not isinstance(data_key, 'bool'):
        errors[key] = "Value must be true or false"

def validate_integer_fields(data_key, errors, key, is_optional,min,max):
    try:
        int(data_key)
        if ((is_optional and data_key) or not is_optional) and min is not None and min > 0 and int(data_key) < min:
            if key not in errors:
                errors[key] = {}
                errors[key]['min'] = "Value is lesser than %s" % max
        if max is not None and max > 0 and int(data_key) > max:
            if key not in errors:
                errors[key] = {}
                errors[key]['max'] = "Value is greater than %s" % max
    except ValueError as e:
        errors[key] = "Value must be an integer"

def run_template_validations(template_validations, data):
    errors = {}
    data_keys = data.keys()    
    if template_validations[0] and 'validations' in template_validations[0].keys():
        validations = dict(template_validations[0].get('validations'))
        validation_keys = validations.keys()
        check_for_not_acceptable_keys(data_keys,validation_keys,errors)
        for key,validation in validations.items():
            is_optional = validation.get('optional')
            is_field_custom = validation.get('is_field_custom')
            field_type = validation.get('field_type')
            required_or_override(data_keys, key, is_optional, is_field_custom, errors)            
            if key in data_keys and is_field_custom:
                data_key = data[key]
                if field_type in ["TEXT", "TEXTAREA"]:
                    validate_text_fields(data_key, errors, key, is_optional,validation.get('min'),validation.get('max'))
                if field_type == "EMAIL":
                    validate_email_field(data_key, errors, key)
                if field_type == "SELECT":
                    validate_select_field(data_key, errors, key, validation.get('options'))
                if field_type in ["MULTISELECT", "RADIO"]:
                    validate_multiselect_field(data_key, errors, key, validation.get('options'), validation.get('min'), validation.get('max'))
                if field_type in ["DATE", "DATETIME","TIME"]:  
                    validate_date_fields(data_key, errors, key, validation.get('format')) 
                if field_type == "YEAR":
                    validate_year_field(data_key, errors, key)
                if field_type == "MONTH":
                    validate_month_field(data_key, errors, key)
                if field_type == "DAY":
                    validate_day_field(data_key, errors, key)
                if field_type in ["BOOLEAN", "CHECKBOX"]:
                    validate_boolean_field(data_key, errors, key)
                if field_type == "INTEGER":
                    validate_integer_fields(data_key, errors, key, is_optional,validation.get('min'),validation.get('max'))
                    
                    
    if errors:
        return {"valid": False, "errors": errors}
    else:
        return {"valid": True, "errors": errors}