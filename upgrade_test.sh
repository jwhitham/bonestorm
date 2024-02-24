#!/bin/bash -xe

test_db_file=/tmp/test-file-$$
ref_file=/tmp/test-file-$$-1
check_file=/tmp/test-file-$$-2

for i in database/*/*
do
    cp $i $test_db_file
    python bonestorm --upgrade-database --database $test_db_file
    sqlite3 $test_db_file 'SELECT dbv FROM version' > $check_file
done

echo 2 > $ref_file
cmp $ref_file $check_file
rm -f $test_db_file
rm -f $ref_file
rm -f $check_file

echo "OK"

