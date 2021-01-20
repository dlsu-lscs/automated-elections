CREATE ROLE election_user WITH LOGIN PASSWORD 'password';

CREATE DATABASE election_primary;
GRANT ALL PRIVILEGES ON DATABASE election_primary TO election_user;

CREATE DATABASE election_replica1;
GRANT ALL PRIVILEGES ON DATABASE election_replica1 TO election_user;

CREATE DATABASE election_replica2;
GRANT ALL PRIVILEGES ON DATABASE election_replica2 TO election_user;

/* psql -h localhost -p 5432 -U election_user -W -d election_primary */
/* psql -h localhost -p 5432 -U election_user -W -d election_replica1 */
/* psql -h localhost -p 5432 -U election_user -W -d election_replica2 */
