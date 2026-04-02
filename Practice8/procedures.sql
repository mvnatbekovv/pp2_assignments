-- Procedure 1:
-- insert a new user by name and phone; if the user already exists, update their phone

CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;


-- Procedure 2:
-- insert many new users from a list of names and phones
-- use a loop and IF inside the procedure
-- validate phone correctness
-- return all incorrect data using NOTICE

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    invalid_data TEXT := '';
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have the same length';
    END IF;

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9+() -]+$' THEN
            IF EXISTS (SELECT 1 FROM contacts WHERE name = p_names[i]) THEN
                UPDATE contacts
                SET phone = p_phones[i]
                WHERE name = p_names[i];
            ELSE
                INSERT INTO contacts(name, phone)
                VALUES (p_names[i], p_phones[i]);
            END IF;
        ELSE
            invalid_data := invalid_data || '(' || p_names[i] || ', ' || p_phones[i] || '); ';
        END IF;
    END LOOP;

    IF invalid_data <> '' THEN
        RAISE NOTICE 'Incorrect data: %', invalid_data;
    END IF;
END;
$$;


-- Procedure 3:
-- delete data from the table by username or phone

CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value OR phone = p_value;
END;
$$;