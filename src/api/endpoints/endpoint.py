from fastapi import APIRouter

router = APIRouter()

descriptions = {
    "service-info": "Provides information about the service"
                    ", this structure is based on the standardized GA4GH"
                    " service info structure. In addition, this endpoint"
                    " will also provide information about customized storage"
                    " endpoints offered by the TES server."
}


@router.get("/service-info",
            responses={200: {"description": "Ok"}},
            description=descriptions["service-info"],
            name="GetServiceInfo")
async def get_service_info() -> dict:
    return {"Hello": "World"}
