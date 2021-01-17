import re
USERNAME_REGEX = r'^[a-z]{3,12}$'
PASSWORD_REGEX = r'^.{8,}$'
NAME_REGEX = r'^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$'
EMAIL_REGEX = r'^[a-z0-9]+([\._]?[a-z0-9])+[@]\w+([.]\w+)+$'
ADDRESS_REGEX = r'^[\wĄĆĘŁŃÓŚŹŻąćęłńóśźż\/.\-, ]+$'
def username_validation(username):
    return (re.fullmatch(USERNAME_REGEX, username) is not None)
def password_validation(password):
    return (re.fullmatch(PASSWORD_REGEX, password) is not None)
def name_validation(name):
    return (re.fullmatch(NAME_REGEX, name) is not None)
def email_validation(email):
    return (re.fullmatch(EMAIL_REGEX, email) is not None)
def address_validation(address):
    return (re.fullmatch(ADDRESS_REGEX, address) is not None)
def label_name_validation(name):
    return (re.fullmatch(ADDRESS_REGEX, name) is not None)