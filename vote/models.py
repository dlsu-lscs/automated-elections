# Create your models here.
import uuid

from django.contrib.auth.models import User
from django.db import models
from audit_trail.history import AuditTrail, AuditManager
from enum import Enum

# College Campus: MNL, LAG
class Campus(models.Model):
    name = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name

# College Names: CCS, COS
class College(models.Model):
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.name


"""
    ongoing:    When the election is currently ongoing
        -> (next state) paused or blocked
    paused:     When the election is on paused, (during the night) to stop
                    students voting at this time
        -> (next state) ongoing
    blocked:    When the election is stopped and the results are still
                    hidden to the comelec officer until the sysadmin unblocks
                    the results
        -> (next state) finished
    finished:   Unblocked and the results can be viewed by the comelec officers
        -> (next state) archived
    archived:   The results have been archived to a csv file and the data will
                    be removed from the database
"""
class ElectionState(Enum):
    ONGOING = "ongoing"
    PAUSED = "paused"
    BLOCKED = "blocked"
    FINISHED = "finished"   
    ARCHIVED = "archived"   

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Election(models.Model):
    state = models.CharField(max_length=20, choices=ElectionState.choices())
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.timestamp) + " elections is currently " + self.state


class ElectionStatus(models.Model):
    batch = models.CharField(max_length=4)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return self.college.name + "," + self.batch


class Unit(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.CharField(max_length=4, null=True, blank=True)
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        college_batch = (self.college.name if self.college is not None else "") + (
            (", " + self.batch) if self.batch is not None else "")

        return self.name + ((" (" + college_batch + ")") if college_batch != "" else "")


class BasePosition(models.Model):
    EXECUTIVE = 'Executive'
    CAMPUS = 'Campus'
    BATCH = 'Batch'
    COLLEGE = 'College'

    POSITION_TYPES = (
        (EXECUTIVE, 'Executive'),
        (CAMPUS, 'Campus'),
        (BATCH, 'Batch'),
        (COLLEGE, 'College'),
    )

    name = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=POSITION_TYPES)

    def __str__(self):
        return self.name + ' (' + self.type + ')'


class Position(models.Model):
    base_position = models.ForeignKey(BasePosition, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    priority = models.IntegerField(default=100)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ('base_position', 'unit')
        ordering = ['priority']

    def __str__(self):
        return ((self.unit.name + " ")
                if self.base_position.type != BasePosition.EXECUTIVE else "") + self.base_position.name


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    batch = models.CharField(max_length=3)
    voting_status = models.BooleanField(default=True)
    eligibility_status = models.BooleanField(default=True)

    def __str__(self):
        return "(" + self.user.username + ") " + self.user.first_name + " " + self.user.last_name


class Party(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE, unique=True)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, default=None, null=True, blank=True)

    class Meta:
        unique_together = ('position', 'party')
        ordering = ['position__priority']

    def __str__(self):
        return self.voter.user.first_name + " " + self.voter.user.last_name \
               + " (" + (
                   self.party.name if self.party is not None else "Independent") + ") - " + self.position.__str__()


class Issue(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Take(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    response = models.TextField()

    def __str__(self):
        return self.response + \
               " (" + self.candidate.voter.user.first_name + " " + self.candidate.voter.user.last_name + ")"


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    # voter_id_number = models.CharField(max_length=8, unique=True)

    serial_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    voter_campus    = models.ForeignKey(Campus, on_delete=models.CASCADE)
    voter_college   = models.ForeignKey(College, on_delete=models.CASCADE)
    voter_batch     = models.CharField(max_length=3)

    timestamp = models.DateTimeField(auto_now_add=True)

    history = AuditTrail()
    objects = AuditManager.as_manager()

    class Meta:
        display_format = 'Vote'

    def __str__(self):
        return "(" + str(self.serial_number) + ") " + str(self.voter) + " voted on " + repr(self.timestamp)


class VoteSet(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)

    history = AuditTrail()
    objects = AuditManager.as_manager()
    
    class Meta:
        display_format = 'VoteSet'

    def __str__(self):
        return str(self.vote.voter) + " voted for " \
               + self.candidate.voter.user.first_name + " " + self.candidate.voter.user.last_name


class Poll(models.Model):
    name = models.CharField(max_length=64, unique=True)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name


class PollAnswerType(Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class PollSet(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    answer = models.CharField(max_length=7, choices=PollAnswerType.choices())

    history = AuditTrail()
    objects = AuditManager.as_manager()

    class Meta:
        display_format = 'PollSet'

    def __str__(self):
        return self.vote.voter_id_number + " voted for " \
               + self.answer + " in " + self.poll.name
