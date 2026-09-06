select * from users;
insert into users(username,email,password_hash,role,created_at)
values
('tirth', 'tirth@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('riya', 'riya@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('kavya', 'kavya@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('dhruv', 'dhruv@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('neha', 'neha@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('raj', 'raj@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('priya', 'priya@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('anuj', 'anuj@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW()),
('divya', 'divya@student.edu', 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc', 'student', NOW());


-- Add 50 students
DO $$
DECLARE
    names TEXT[] := ARRAY[
        'vivaan', 'aditya', 'vihaan', 'arjun', 'sai', 'pranav', 'krishna', 'shaurya',
        'aadhya', 'ananya', 'diya', 'ishita', 'jiya', 'navya', 'pari', 'sara', 'tanvi',
        'riyansh', 'anvi', 'myra', 'yash', 'ved', 'anay', 'isha', 'rajan',
        'kunal', 'simran', 'rohan', 'meera', 'varun', 'shreya', 'nikhil', 'shivani',
        'tarun', 'ridhima', 'mohit', 'sakshi', 'gaurav', 'ishani', 'abhishek',
        'shruti', 'vikram', 'pallavi', 'karan', 'rajat', 'poonam', 'manish'
    ];
    name_text TEXT;
    student_hash TEXT := 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc';
BEGIN
    FOREACH name_text IN ARRAY names
    LOOP
        -- Only insert if username does NOT exist
        IF NOT EXISTS (SELECT 1 FROM users WHERE username = name_text) THEN
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (
                name_text,
                name_text || '@student.edu',
                student_hash,
                'student',
                NOW() - (random() * INTERVAL '60 days')
            );
        ELSE
            RAISE NOTICE 'Skipping % - already exists', name_text;
        END IF;
    END LOOP;
    RAISE NOTICE 'Finished adding new students!';
END $$;



-- Add 50 more students, 
DO $$
DECLARE
    more_names TEXT[] := ARRAY[
        'rekha', 'sanjay', 'kiran', 'amit', 'sunita', 'vijay', 'anita', 'rohit', 'jyoti',
        'pankaj', 'mamta', 'sachin', 'geeta', 'ravi', 'komal', 'sumit', 'arti', 'deepak',
        'neelam', 'rajesh', 'nisha', 'suresh', 'kajal', 'mahesh', 'sonali', 'dinesh',
        'ashish', 'monika', 'vivek', 'swati', 'amresh', 'anjali', 'mukesh', 'rani',
        'brijesh', 'seema', 'rahul', 'pooja', 'nitin', 'kirti', 'alok', 'sneha',
        'manoj', 'preeti', 'anil', 'vandana', 'chetan', 'gopal', 'nidhi'
    ];
    name_text TEXT;
    student_hash TEXT := 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc';
    added_count INTEGER := 0;
    skipped_count INTEGER := 0;
BEGIN
    FOREACH name_text IN ARRAY more_names
    LOOP
        IF NOT EXISTS (SELECT 1 FROM users WHERE username = name_text) THEN
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (
                name_text,
                name_text || '@student.edu',
                student_hash,
                'student',
                NOW() - (random() * INTERVAL '45 days')
            );
            added_count := added_count + 1;
        ELSE
            skipped_count := skipped_count + 1;
        END IF;
    END LOOP;
    RAISE NOTICE 'Added % new students, Skipped % existing students', added_count, skipped_count;
END $$;

select*from users;
-- Create a temporary sequence
CREATE SEQUENCE temp_id_seq;

-- Update IDs sequentially
UPDATE users 
SET id = nextval('temp_id_seq');

-- Drop the sequence
DROP SEQUENCE temp_id_seq;

select count(*)as total_student from users 
where role ='student';

UPDATE users 
SET password_hash = 'scrypt:32768:8:1$cZrjvkKeKlCtMga7$dd58cfaceaf18e6798435157b8ad449b4d5cd19dfc7ff688cea39350860a3a6194db59fd8048aa604d6685cb418e33f0b0ac9d523ea3204050e8a4c16ba2e1cc'
WHERE username = 'trupal';