select* from attendances;

-- Simple attendance insertion (One student at a time)
-- First, check if attendance already exists for today
DO $$
DECLARE
    student_record RECORD;
    day_offset INTEGER;
    current_date_val DATE;
    random_status TEXT;
BEGIN
    FOR student_record IN SELECT id FROM users WHERE role = 'student' LIMIT 10 LOOP
        FOR day_offset IN 0..29 LOOP
            current_date_val := CURRENT_DATE - day_offset;
            
            -- Only insert if attendance doesn't already exist
            IF NOT EXISTS (
                SELECT 1 FROM attendances 
                WHERE student_id = student_record.id AND date = current_date_val
            ) THEN
                IF EXTRACT(DOW FROM current_date_val) NOT IN (0, 6) THEN
                    -- Random status (80% Present, 10% Absent, 10% Late)
                    IF random() < 0.8 THEN
                        random_status := 'Present';
                    ELSIF random() < 0.9 THEN
                        random_status := 'Absent';
                    ELSE
                        random_status := 'Late';
                    END IF;
                    
                    INSERT INTO attendances (student_id, date, status, check_in_time, created_at)
                    VALUES (
                        student_record.id,
                        current_date_val,
                        random_status,
                        TIME '09:00:00' + (random() * INTERVAL '2 hours'),
                        NOW()
                    );
                END IF;
            END IF;
        END LOOP;
    END LOOP;
    RAISE NOTICE 'Attendance added for sample students';
END $$;