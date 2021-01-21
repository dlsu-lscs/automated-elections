CREATE TABLE vote_pollset (
    id          SERIAL      PRIMARY KEY,
    answer      VARCHAR(7)  NOT NULL,
    poll_id     INT,
    vote_id     INT         NOT NULL
);

CREATE TABLE vote_vote (
    id              SERIAL      PRIMARY KEY,
    voter_id_number VARCHAR(8)  NOT NULL UNIQUE,
    serial_number   VARCHAR(10) NOT NULL UNIQUE,
    voter_college   VARCHAR(3)  NOT NULL,
    timestamp       TIMESTAMP   NOT NULL
);

CREATE TABLE vote_voteset (
    id              SERIAL  PRIMARY KEY,
    candidate_id    INT,
    vote_id         INT     NOT NULL,
    position_id     INT
);

DROP TABLE vote_voteset;
DROP TABLE vote_pollset;
DROP TABLE vote_vote;
