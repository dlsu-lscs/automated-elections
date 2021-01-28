# Register your models here.
from django.contrib import admin

from vote.models import AuthUser, College, Unit, Position, Voter, Candidate, Issue, Take, Vote, VoteSet, Party, Poll, PollSet

@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    ordering = ['username']
    search_fields = ['username']

admin.site.register(College)
admin.site.register(Unit)
admin.site.register(Position)
admin.site.register(Party)
admin.site.register(Candidate)
admin.site.register(Issue)
admin.site.register(Take)
admin.site.register(Poll)

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    ordering = ['user__username']
    search_fields = ['user__username']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    ordering = ['serial_number']
    search_fields = ['serial_number']

@admin.register(PollSet)
class PollSetAdmin(admin.ModelAdmin):
    ordering = ['vote__serial_number']
    search_fields = ['vote__serial_number']

@admin.register(VoteSet)
class VoteSetAdmin(admin.ModelAdmin):
    ordering = ['vote__serial_number']
    search_fields = ['vote__serial_number']
