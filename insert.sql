INSERT INTO auth_group(name) VALUES
    ('sysadmin'),
    ('comelec'),
    ('voter');

INSERT INTO auth_user_groups(user_id, group_id)
    VALUES (1, 1);

/*
INSERT INTO auth_group_permissions(group_id, permission_id) VALUES
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
    (1, 10),
    (1, 11),
    (1, 12),
    (1, 13),
    (1, 14),
    (1, 15),
    (1, 16),
    (1, 17),
    (1, 18),
    (1, 19),
    (1, 20),
    (1, 21),
*/


INSERT INTO vote_college(name) VALUES
    ('CCS'),
    ('COS'),
    ('CLA'),
    ('GCOE'),
    ('RVR-COB'),
    ('BAGCED'),
    ('SOE'),
    ('LAG');

INSERT INTO vote_party(name) VALUES
    ('Alyansang Tapat sa Lasallista'),
    ('Santugon sa Tawag ng Panahon');

INSERT INTO vote_baseposition(name, type) VALUES
    ('USG President', 'Executive'),
    ('Vice President for Internal Affairs', 'Executive'),
    ('Vice President for External Affairs', 'Executive'),
    ('USG Treasurer', 'Executive'),
    ('USG Secretary', 'Executive'),
    ('Batch President', 'Batch'),
    ('Batch Vice President', 'Batch'),
    ('LA Representative', 'Batch'),
    ('College President', 'College');

INSERT INTO vote_unit(batch, name, college_id) VALUES
    ('117', 'CATCH2T21', 1),
    ('118', 'CATCH2T22', 1),
    ('119', 'CATCH2T23', 1),
    ('120', 'CATCH2T24', 1),
    ('117', 'FOCUS17', 2),
    ('118', 'FOCUS18', 2),
    ('119', 'FOCUS19', 2),
    ('120', 'FOCUS20', 2),
    ('117', 'FAST2017', 3),
    ('118', 'FAST2018', 3),
    ('119', 'FAST2019', 3),
    ('120', 'FAST2020', 3),
    ('117', '72nd ENG', 4),
    ('118', '73rd ENG', 4),
    ('119', '74th ENG', 4),
    ('120', '75th ENG', 4),
    ('117', 'BLAZE2020', 5),
    ('118', 'BLAZE2021', 5),
    ('119', 'BLAZE2022', 5),
    ('120', 'BLAZE2023', 5),
    ('117', 'EDGE2017', 6),
    ('118', 'EDGE2018', 6),
    ('119', 'EDGE2019', 6),
    ('120', 'EDGE2020', 6),
    ('117', 'EXCEL2020', 7),
    ('118', 'EXCEL2021', 7),
    ('119', 'EXCEL2022', 7),
    ('120', 'EXCEL2023', 7),
    (NULL, 'CSG', 1),
    (NULL, 'SCG', 2),
    (NULL, 'ACG', 3),
    (NULL, 'ECG', 4),
    (NULL, 'BSG', 5),
    (NULL, 'CGE', 6),
    (NULL, 'SEG', 7),
    (NULL, 'Executive Board', NULL);