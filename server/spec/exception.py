''' Exception hierarchy

ServerException

    RequestServerException - bad request

    RequestFileServerException - bad request file format

    InputDataServerException - bad input data

    DataBaseServerException - request is not accommodated with database

    InnerServerException - inner server exception

'''

class ServerException(Exception):
    "Base server exeption"
    pass

class RequestServerException(ServerException):
    "Bad request"
    pass

class RequestFileServerException(ServerException):
    "Bad request file format"
    pass

class InputDataServerException(ServerException):
    "Bad input data"
    pass

class DatabaseServerException(ServerException):
    "Request is not accommodated with database"
    pass

class InnerServerException(ServerException):
    "Inner server error"
    pass
