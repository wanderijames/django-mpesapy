import hashlib
import base64
import datetime


def plain2JSON(text, delimeter="|"):
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
    kvs = filter(lambda x: x is not None, kvs)
    kvs = [x.split(":", 1) for x in kvs]
    for [key, value] in kvs:
        result[key] = value if value != "None" else ""
    return result


def json2PLAIN(json, delimeter="|"):
    """Transforms JSON into a plain text

    :param json: JSON object that needs to be converted to plain text
    :param delimeter: Delimeter to be used in the plain text
    :type json: dict
    :type delimeter: str
    :return: Plain text from JSON
    :rtype: str

    """
    kvs = []
    for key, value in json.items():
        kvs.append("{}:{}".format(key, value))
    return delimeter.join(kvs)


def kenya_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=3)


def encrypt_password(merchant_id, passkey):
    timestamp = kenya_time().strftime("%Y%m%d%H%M%S")
    hash = hashlib.sha256("{} {} {}".format(
                                            merchant_id,
                                            passkey,
                                            timestamp)).upper()
    return timestamp, base64.b64encode(hash)
