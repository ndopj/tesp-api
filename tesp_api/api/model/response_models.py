from typing import List

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from tesp_api.repository.model.task import RegisteredTesTask


class ErrorResponseModel(BaseModel):
    timestamp: int = Field(...)
    error: str = Field(...)
    status: int = Field(...)
    message: str = Field(...)


class TesCreateTaskResponseModel(BaseModel):
    id: str = Field(..., description='Task identifier assigned by the server.')


class RegisteredTesTaskSchema(RegisteredTesTask):
    id: str = Field(None, example="job-0012345", description="Task identifier assigned by the server", alias=None)


class TesGetAllTasksResponseSchema(BaseModel):
    tasks: List[RegisteredTesTaskSchema] = Field(..., description='List of tasks. These tasks will be based on the'
                                                                  ' original submitted task document, but with other'
                                                                  ' fields, such as the job state and logging info,'
                                                                  ' added/changed as the job progresses.')
    next_page_token: str = Field(None, description='Token used to return the next page of results. This value can be'
                                                   ' used in the page_token field of the next ListTasks request.')


class TesGetAllTasksResponseModel(BaseModel):
    tasks: List[dict] = Field(...)
    next_page_token: str = Field(None)

    class Config:
        json_encoders = {ObjectId: str}
