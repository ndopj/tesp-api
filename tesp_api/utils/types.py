from pydantic.networks import AnyUrl


class FtpUrl(AnyUrl):
    allowed_schemes = {'ftp'}
    host_required = True
