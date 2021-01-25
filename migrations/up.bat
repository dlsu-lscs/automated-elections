psql -h localhost -p 5432 -U election_voter1 -W -d election_vote1 < up.sql

psql -h localhost -p 5432 -U election_voter2 -W -d election_vote2 < up.sql

psql -h localhost -p 5432 -U election_voter3 -W -d election_vote3 < up.sql
