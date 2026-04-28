__title__ = "pocketbase"
__description__ = "PocketBase client SDK for python."
__version__ = "0.10.1"


from .client import Client


class PocketBase(Client):
    """
    Proxy class for `Client`

    This is for cosmetic reasons only as you can use the
    `Client` class just the same
    """

    pass
