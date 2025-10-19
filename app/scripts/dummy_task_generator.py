
from datetime import UTC, datetime, timezone, tzinfo
from enum import Enum
import random
import string
from faker import Faker


class DummyTaskPeriority(Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class DummyTaskGenerator:
    'A class to genarate dummy tasks for initialization of database records for testing application processes'

    def __init__(self, total_tasks: int, total_users: int, start_time: datetime, end_time: datetime):
        self.number_of_tasks = total_tasks
        self.number_of_users = total_users
        self.start_datetime = start_time
        self.end_datetime = end_time
        self.faker = Faker()
        self.utc = timezone.utc

    def generate_title(self):
        """Generate a short random title for a task"""
        return self.faker.sentence(nb_words=4).strip('.')

    def generate_description(self):
        """Generate a realistic paragraph description"""
        return self.faker.paragraph(nb_sentences=3)

    def generate_user_id(self):
        """Randomly assign a user_id from available users"""
        return random.randint(1, self.number_of_users)

    def generate_created_and_due_dates(self):
        """Generate realistic created_at and due_date timestamps"""
        created_at = self.faker.date_time_between(
            start_date=self.start_datetime, end_date=self.end_datetime, tzinfo=self.utc
        )
        # Make sure due_date is after created_at
        due_date = self.faker.date_time_between(
            start_date=created_at, end_date=self.end_datetime, tzinfo=self.utc
        )
        return created_at, due_date

    def generate_is_completed(self):
        """Randomly mark task as completed or not"""
        return random.choice([True, False])

    def generate_priority(self):
        """Assign random priority"""
        return random.choice(["URGENT", "HIGH", "NORMAL", "LOW"])

    def generate_task(self):
        """Generate a single dummy task"""
        created_at, due_date = self.generate_created_and_due_dates()
        return {
            "user_id": self.generate_user_id(),
            "title": self.generate_title(),
            "description": self.generate_description(),
            "priority": self.generate_priority(),
            "is_completed": self.generate_is_completed(),
            "created_at": created_at,
            "due_date": due_date,
        }

    def generate_all_tasks(self):
        """Generate a list of dummy tasks"""
        return [self.generate_task() for _ in range(self.number_of_tasks)]
