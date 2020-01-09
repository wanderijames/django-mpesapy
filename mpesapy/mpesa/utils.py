"""App utilities"""
import hashlib
import base64
import datetime


def to_json(text: str, delimeter: str = "|") -> dict:
    """Transforms a plain text into JSON

    The plain text should have key:value separated by a pipe.
    An example of a plain text::

        api:sdsfe3ss|username:343343

    The example above would be transformed to::

        {"api": "sdsfe3ss", "username": "343343"}

    :param text: Text that is being transformed
    :param delimeter: Key-Value delimeter. Optional
    :type text: str
    :type delimter: str
    :return: JSON object from the text
    :rtype: dict

    """
    result = {}
    kvs = text.strip().split(delimeter)
    kvs = [x.split(":", 1) for x in kvs if x is not None]
    for [key, value] in kvs:
        result[key] = value if value != "None" else ""
    return result


def from_json(json_data: dict, delimeter: str = "|") -> str:
    """Transforms JSON into a plain text

    :param json_data: JSON object that needs to be converted to plain text
    :param delimeter: Delimeter to be used in the plain text
    :type json_data: dict
    :type delimeter: str
    :return: Plain text from JSON
    :rtype: str

    """
    kvs = []
    for key, value in json_data.items():
        kvs.append("{}:{}".format(key, value))
    return delimeter.join(kvs)


def kenya_time() -> datetime.datetime:
    """Get local time for mpesa"""
    return datetime.datetime.utcnow() + datetime.timedelta(hours=3)


def encrypt_password(merchant_id: str, passkey: str) -> (str, ):
    """Encrypted hash for mpesa apis"""
    timestamp = kenya_time().strftime("%Y%m%d%H%M%S")
    plain_text = "{} {} {}".format(merchant_id, passkey, timestamp)
    hashed_text = hashlib.sha256(plain_text.encode()).hexdigest().upper()
    return timestamp, base64.b64encode(hashed_text)
