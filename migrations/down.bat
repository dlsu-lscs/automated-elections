psql -h localhost -p 5432 -U election_voter1 -W -d election_vote1 < down.sql

psql -h localhost -p 5432 -U election_voter2 -W -d election_vote2 < down.sql

psql -h localhost -p 5432 -U election_voter3 -W -d election_vote3 < down.sql