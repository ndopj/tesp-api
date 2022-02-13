from fastapi import FastAPI, APIRouter
from starlette.responses import RedirectResponse
from uvicorn.config import LOGGING_CONFIG

from src.api.api import api_router


root_router = APIRouter()
app = FastAPI(title="Tesp API", docs_url="/swagger-ui.html")


@root_router.get("/", status_code=307, include_in_schema=False)
async def get_root() -> RedirectResponse:
    return RedirectResponse(url="swagger-ui.html")


app.include_router(root_router)
app.include_router(api_router)


def main():
    import uvicorn
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s'\
                                                    ' - "%(request_line)s" %(status_code)s'
    uvicorn.run("src.tesp_api:app",
                host="0.0.0.0", port=8081, reload=True, workers=2, log_level="debug")


if __name__ == "__main__":
    main()
