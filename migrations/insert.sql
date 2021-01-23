INSERT INTO auth_group(name) VALUES
    ('sysadmin'),
    ('comelec'),
    ('voter');

INSERT INTO vote_authuser_groups(authuser_id, group_id)
    VALUES (1, 1);

INSERT INTO vote_college(name) VALUES
    ('CCS'),
    ('COS'),
    ('CLA'),
    ('GCOE'),
    ('RVR-COB'),
    ('BAGCED'),
    ('SOE');

INSERT INTO vote_campus(name) VALUES
    ('MNL'),
    ('LAG');

INSERT INTO vote_party(name) VALUES
    ('Alyansang Tapat sa Lasallista'),
    ('Santugon sa Tawag ng Panahon');

-- Executive    - Everyone can vote
-- Campus       - Certain campus is needed
-- College      - Certain college, campus is needed
-- Batch        - Certain batch, college, campus is needed
INSERT INTO vote_baseposition(name, type) VALUES
    ('USG President', 'Executive'),
    ('Vice President for Internal Affairs', 'Executive'),
    ('Vice President for External Affairs', 'Executive'),
    ('USG Secretary', 'Executive'),
    ('USG Treasurer', 'Executive'),
    ('Batch President', 'Batch'),
    ('Batch Vice President', 'Batch'),
    ('LA Representative', 'Batch'),
    ('College President', 'College'),
    -- LAGUNA
    ('Campus President', 'Campus'),
    ('Campus Secretary', 'Campus'),
    ('GCOE Representative', 'College'),
    ('LA Representative', 'Campus');

INSERT INTO vote_unit(batch, name, college_id, campus_id) VALUES
    ('117', 'CATCH2T21', 1, 1),
    ('118', 'CATCH2T22', 1, 1),
    ('119', 'CATCH2T23', 1, 1),
    ('120', 'CATCH2T24', 1, 1),
    ('117', 'FOCUS17', 2, 1),
    ('118', 'FOCUS18', 2, 1),
    ('119', 'FOCUS19', 2, 1),
    ('120', 'FOCUS20', 2, 1),
    ('117', 'FAST2017', 3, 1),
    ('118', 'FAST2018', 3, 1),
    ('119', 'FAST2019', 3, 1),
    ('120', 'FAST2020', 3, 1),
    ('117', '72nd ENG', 4, 1),
    ('118', '73rd ENG', 4, 1),
    ('119', '74th ENG', 4, 1),
    ('120', '75th ENG', 4, 1),
    ('117', 'BLAZE2020', 5, 1),
    ('118', 'BLAZE2021', 5, 1),
    ('119', 'BLAZE2022', 5, 1),
    ('120', 'BLAZE2023', 5, 1),
    ('117', 'EDGE2017', 6, 1),
    ('118', 'EDGE2018', 6, 1),
    ('119', 'EDGE2019', 6, 1),
    ('120', 'EDGE2020', 6, 1),
    ('117', 'EXCEL2020', 7, 1),
    ('118', 'EXCEL2021', 7, 1),
    ('119', 'EXCEL2022', 7, 1),
    ('120', 'EXCEL2023', 7, 1),
    (NULL, 'CSG', 1, 1),
    (NULL, 'SCG', 2, 1),
    (NULL, 'ACG', 3, 1),
    (NULL, 'ECG', 4, 1),
    (NULL, 'BSG', 5, 1),
    (NULL, 'CGE', 6, 1),
    (NULL, 'SEG', 7, 1),
    (NULL, 'GCOE-LAG', 4, 2),
    (NULL, 'LAGUNA', NULL, 2),
    (NULL, 'Executive Board', NULL, NULL);