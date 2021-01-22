/* TODO: Change the passwords */
CREATE ROLE election_user WITH LOGIN PASSWORD 'password';
CREATE ROLE election_voter1 WITH LOGIN PASSWORD 'password';
CREATE ROLE election_voter2 WITH LOGIN PASSWORD 'password';
CREATE ROLE election_voter3  WITH LOGIN PASSWORD 'password';

/*
    WRITE DATA HERE
*/
CREATE DATABASE election_primary;
GRANT ALL PRIVILEGES ON DATABASE election_primary TO election_user;

-- For Validation Purposes
/*
    TABLES IN USE(META):
        vote_vote(vote.vote)
        vote_voteset(vote.voteset)
        vote_pollset(vote.pollset)
        vote_issueset(vote.issueset)
*/
CREATE DATABASE election_vote1;
GRANT ALL PRIVILEGES ON DATABASE election_vote1 TO election_voter1;
CREATE DATABASE election_vote2;
GRANT ALL PRIVILEGES ON DATABASE election_vote2 TO election_voter2;
CREATE DATABASE election_vote3;
GRANT ALL PRIVILEGES ON DATABASE election_vote3 TO election_voter3;

-- psql -h localhost -p 5432 -U election_user -W -d election_primary
-- psql -h localhost -p 5432 -U election_voter1 -W -d election_vote1
-- psql -h localhost -p 5432 -U election_voter2 -W -d election_vote2
-- psql -h localhost -p 5432 -U election_voter3 -W -d election_vote3
