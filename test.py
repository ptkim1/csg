from Attendees import BaseAttendees
from Seating import BaseSeating

seating = BaseSeating.from_regular_blocks((5, 5), (3, 3))
attendees = BaseAttendees.from_uniform(seating.unfilled / 2, 6)

solver = 


print(seating)
print(seating.seating)

