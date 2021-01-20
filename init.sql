CREATE DATABASE election_db1;
CREATE ROLE election_user WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE election_db1 TO election_user;

/* psql -h localhost -p 5432 -U election_user -W -d election_db1 */
