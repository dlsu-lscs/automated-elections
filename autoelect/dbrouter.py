import random

class PrimaryReplicaRouter:
    # route_app_labels = [ 'vote' ]
    route_meta = [
        'vote.vote',
        'vote.voteset',
        'vote.pollset',
        'vote.issueset'
    ]

    def db_for_read(self, model, **hints):
        if model._meta in self.route_meta:
            return random.choice(['vote1', 'vote2', 'vote3'])
        return 'default'

    def db_for_write(self, model=None, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_set = { 'default', 'vote1', 'vote2', 'vote3' }

        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
