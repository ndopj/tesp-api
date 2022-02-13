from loguru import logger
from pymongo.errors import PyMongoError


class CustomDataLayerError(Exception):

    def __init__(self):
        self.message = "Database error occurred, contact system administrator"
        super().__init__(self.message)

    def __repr__(self):
        return f'DataLayerError [message: {self.message}]'


def handle_data_layer_error(error: Exception):
    match error:
        case PyMongoError() as py_mongo_error:
            logger.error(f'Mongo data layer error occurred [error: {str(py_mongo_error)}]')
        case _ as unknown_error:
            logger.error(f'Unknown data layer error occurred [error: {str(unknown_error)}]')
    raise CustomDataLayerError()
