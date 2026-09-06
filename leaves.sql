-- Add leave applications for 20% of students (CORRECTED)
DO $$
DECLARE
    student_record RECORD;
    leave_start DATE;
    leave_end DATE;
    leave_types TEXT[] := ARRAY['Sick', 'Vacation', 'Emergency', 'Personal'];
    leave_statuses TEXT[] := ARRAY['Approved', 'Approved', 'Pending', 'Approved', 'Rejected'];
    leave_count INTEGER := 0;
    type_index INTEGER;
    status_index INTEGER;
BEGIN
    FOR student_record IN 
        SELECT id FROM users 
        WHERE role = 'student' 
        ORDER BY RANDOM() 
        LIMIT (SELECT COUNT(*) * 0.2 FROM users WHERE role = 'student')
    LOOP
        -- Calculate random indices correctly
        type_index := 1 + floor(random() * array_length(leave_types, 1));
        status_index := 1 + floor(random() * array_length(leave_statuses, 1));
        
        leave_start := CURRENT_DATE + (floor(random() * 30) + 1)::INT;
        leave_end := leave_start + (floor(random() * 3) + 1)::INT;
        
        INSERT INTO leaves (student_id, start_date, end_date, leave_type, reason, status, applied_on)
        VALUES (
            student_record.id,
            leave_start,
            leave_end,
            leave_types[type_index],
            'Personal reasons for leave',
            leave_statuses[status_index],
            NOW() - (random() * INTERVAL '10 days')
        );
        leave_count := leave_count + 1;
    END LOOP;
    RAISE NOTICE 'Added % leave applications', leave_count;
END $$;

select * from leaves;]
select *from quizzes;