import motor.motor_asyncio
from typing import List
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

from src.model.task import TesTask, RegisteredTesTask

MONGO_DETAILS = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)


class TaskRepository:

    def __init__(self, mongodb_client):
        self.client = mongodb_client
        self.tasks = self.client.tesp["tasks"]

    async def create_task(self, task: TesTask) -> str:
        task = jsonable_encoder(RegisteredTesTask(**task.dict()), by_alias=True, exclude={"id"})
        created_task = await self.tasks.insert_one(task)
        return str(created_task.inserted_id)

    async def get_task(self, id: str) -> RegisteredTesTask:
        if (found_task := await self.tasks.find_one({'_id': ObjectId(id)})) is not None:
            return RegisteredTesTask(**found_task)
        raise HTTPException(status_code=404, detail=f"Task[{id}] not found")

    async def get_tasks(self) -> List[RegisteredTesTask]:
        found_tasks = await self.tasks.find({}).to_list(1000)
        return list(map(lambda task: RegisteredTesTask(**task), found_tasks))


task_repository = TaskRepository(client)
