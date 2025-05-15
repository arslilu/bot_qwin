import requests
import json
from . import config

OSAGO_API_URL = "https://service.api-assist.com/parser/osago_api/"
FINES_API_URL = "https://service.api-assist.com/parser/fines_api/"

def check_osago_vin(vin_number):
    """Checks OSAGO by VIN number."""
    params = {
        "key": config.OSAGO_API_KEY,
        "vin": vin_number
    }
    try:
        response = requests.get(OSAGO_API_URL, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        if data.get("success") == 1:
            return {"status": "success", "data": data.get("policies", [])}
        else:
            return {"status": "error", "message": data.get("error", "Unknown API error")}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode API response."}

def check_osago_reg_number(reg_number):
    """Checks OSAGO by registration number."""
    params = {
        "key": config.OSAGO_API_KEY,
        "regNumber": reg_number
    }
    try:
        response = requests.get(OSAGO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("success") == 1:
            return {"status": "success", "data": data.get("policies", [])}
        else:
            return {"status": "error", "message": data.get("error", "Unknown API error")}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode API response."}

def check_fines(reg_number, sts_number):
    """Checks fines by registration number and STS number."""
    params = {
        "key": config.FINES_API_KEY,
        "regNumber": reg_number,
        "sts": sts_number
    }
    try:
        response = requests.get(FINES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("fines_done") is True:
            return {"status": "success", "data": data.get("fines", []), "message": data.get("message")}
        else:
            # The fines API might return fines_done: false with a message, or an error structure
            error_message = data.get("message", data.get("error", "Unknown API error"))
            return {"status": "error", "message": error_message}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode API response."}

def get_fine_photo(photo_token, reg_number, num_post, division_id):
    """Gets a photo for a specific fine."""
    params = {
        "key": config.FINES_API_KEY,
        "getPhoto": 1,
        "photoToken": photo_token,
        "regNumber": reg_number,
        "numPost": num_post,
        "divisionId": division_id
    }
    try:
        response = requests.get(FINES_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("image_done") == 1:
            return {"status": "success", "image_base64": data.get("image_base64"), "additional_images_base64": data.get("additional_images_base64", [])}
        else:
            return {"status": "error", "message": data.get("error", "Failed to retrieve photo")}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to decode API response."}

