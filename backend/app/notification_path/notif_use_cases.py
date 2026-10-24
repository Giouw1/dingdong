from app.domain.abstract_usecases import AbstractNotificatorUseCases
from app.domain.storage_interfaces import AbstractOwnerRepository,AbstractMailboxRepository
from app.domain.entities import Nickname, NotificationPayload, PayloadBuildError
from app.domain.event_bus import EventBusInterface

from typing import Union
from datetime import datetime


class DomainException(Exception): pass
class ResourceNotFoundError(DomainException): pass
class InvalidPayloadError(DomainException): pass




class Notificator_UseCases(AbstractNotificatorUseCases):
    def __init__(self, ownermailbox: AbstractOwnerRepository, notifmailbox: AbstractMailboxRepository, event_bus: EventBusInterface|None):
        self.ownermailbox = ownermailbox
        self.notifmailbox = notifmailbox
        self.event_bus = event_bus
    def notificate(self, nickname: Nickname, payload: str | None = None) -> bool:
        """
        Inserts a notification in a mailbox.
        Constructs the NotificationPayload internally with metadata.
        """
            
        nickname = Nickname(nickname=nickname)
        owner_id = self.ownermailbox.get_user_id_by_nickname(nickname=nickname)
        if owner_id is None:
            raise ResourceNotFoundError("There is no User with such Nickname")

        conteudo = payload if payload is not None else f"Notif at {datetime.now()}"
        try:
            notification = NotificationPayload(
                conteudo=conteudo,
                lida=False,
                timestamp=datetime.now(),
            )
        except PayloadBuildError:
            raise InvalidPayloadError("Invalid data for the payload")
        saved = self.notifmailbox.save(target_id=owner_id, payload=notification)
        if not saved:
            raise ResourceNotFoundError("Mailbox does not exist for this user")
        self.event_bus.publish(topic=owner_id,data=notification)
        return True
def get_notifier_use_cases()->Notificator_UseCases:
    raise NotImplementedError("This dependency must be overridden by the main application.")