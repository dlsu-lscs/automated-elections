CREATE TABLE vote_pollset (
    id          SERIAL      PRIMARY KEY,
    answer      VARCHAR(7)  NOT NULL,
    poll_id     INT,
    vote_id     INT         NOT NULL
);

CREATE TABLE vote_vote (
    id                  SERIAL      PRIMARY KEY,
    serial_number       UUID        NOT NULL UNIQUE,
    voter_id            INT         NOT NULL,
    voter_campus_id     INT         NOT NULL,
    voter_college_id    INT         NOT NULL,
    voter_batch         VARCHAR(3)  NOT NULL,
    -- voter_id_number VARCHAR(8)  NOT NULL UNIQUE,
    timestamp       TIMESTAMP   NOT NULL
);

CREATE TABLE vote_voteset (
    id              SERIAL  PRIMARY KEY,
    candidate_id    INT,
    vote_id         INT     NOT NULL,
    position_id     INT
);
