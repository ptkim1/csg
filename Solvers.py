from Seating import BaseSeating
from Attendees import BaseAttendees


class BaseSolver:
    def __init__(self, seating: BaseSeating, attendees: BaseAttendees):
        self.seating = seating
        self.attendees = attendees

    @abstractmethod
    