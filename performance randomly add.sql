-- Add quiz scores for all students
DO $$
DECLARE
    student_record RECORD;
    module_record RECORD;
    random_score DECIMAL;
    random_date DATE;
    score_count INTEGER := 0;
BEGIN
    FOR student_record IN SELECT id FROM users WHERE role = 'student' LOOP
        FOR module_record IN SELECT id FROM modules ORDER BY RANDOM() LIMIT (3 + (random() * 5))::INT LOOP
            random_score := 40 + (random() * 60);
            random_date := CURRENT_DATE - (random() * 90)::INT;
            
            INSERT INTO performances (student_id, module_id, score, time_spent_minutes, completed_at, week_number, month_number, year)
            VALUES (
                student_record.id,
                module_record.id,
                ROUND(random_score, 2),
                30 + (random() * 150)::INT,
                random_date,
                EXTRACT(WEEK FROM random_date),
                EXTRACT(MONTH FROM random_date),
                EXTRACT(YEAR FROM random_date)
            );
            score_count := score_count + 1;
        END LOOP;
    END LOOP;
    RAISE NOTICE 'Added % performance records', score_count;
END $$;

select * from performances;
