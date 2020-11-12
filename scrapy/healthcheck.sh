#! /bin/bash
groc_file=/tmp/groceries

if [ -f $groc_file ] ; then
  source $groc_file
fi

if [[ "$grocery_count" == "" ]] ; then
  old_grocery_count=0
else
  old_grocery_count=$grocery_count
fi

db_cmd="mysql --host=db --user=root --password=example --database=groceries"
store_name="harris-teeter"

store_id=$($db_cmd --execute "SELECT id FROM storeTable WHERE name = '$store_name'" | sed 's/[^0-9]*//g')
grocery_count=$($db_cmd --execute "SELECT COUNT(*) FROM groceryTable WHERE store_id = '$store_id'" | sed 's/[^0-9]*//g' | awk '{printf("%s", $0)}')

echo "export grocery_count=$grocery_count" > $groc_file
if [[ $grocery_count -gt $old_grocery_count ]] ; then
  kill 1
fi
#[[ $grocery_count -gt $old_grocery_count ]]
