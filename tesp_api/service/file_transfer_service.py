import aioftp

from tesp_api.utils.functional import maybe_of
from tesp_api.utils.types import FtpUrl


# TODO: Error handling
class FileTransferService:

    def __init__(self):
        self.ftp_client = aioftp.Client()

    @staticmethod
    async def ftp_download_file(ftp_url: FtpUrl):
        async with aioftp.Client.context(
                host=ftp_url.host, port=maybe_of(ftp_url.port).maybe(aioftp.DEFAULT_PORT, lambda x: int(x)),
                user=maybe_of(ftp_url.user).maybe(aioftp.DEFAULT_USER, lambda x: x),
                password=maybe_of(ftp_url.password).maybe(aioftp.DEFAULT_PASSWORD, lambda x: x)) as client:
            async with client.download_stream(ftp_url.path) as stream:
                return await stream.read()

    @staticmethod
    async def ftp_upload_file(ftp_url: FtpUrl, file_content: bytes):
        async with aioftp.Client.context(
                host=ftp_url.host, port=maybe_of(ftp_url.port).maybe(aioftp.DEFAULT_PORT, lambda x: int(x)),
                user=maybe_of(ftp_url.user).maybe(aioftp.DEFAULT_USER, lambda x: x),
                password=maybe_of(ftp_url.password).maybe(aioftp.DEFAULT_PASSWORD, lambda x: x)) as client:
            async with client.upload_stream(ftp_url.path) as stream:
                await stream.write(file_content)


file_transfer_service = FileTransferService()
