#! /bin/bash
if [[ "$#" -ne "2"  ]]; then
  echo "Usage: $0 <storename> <url|[grocery]>"
  exit
fi

store_name=$1
mode=grocery
[[ "$2" == "url" ]] && mode=url

file=/tmp/$mode

if [ -f $file ] ; then
  source $file
fi

if [[ "$count" == "" ]] ; then
  old_count=0
else
  old_count=$count
fi

db_cmd="mysql --host=db --user=root --password=example --database=groceries"

store_id=$($db_cmd --execute "SELECT id FROM storeTable WHERE name = '$store_name'" | sed 's/[^0-9]*//g')

sql="SELECT COUNT(*) FROM groceryTable WHERE store_id = '$store_id' "
if [[ $mode == "url" ]] ; then
	sql="SELECT COUNT(*) FROM urlTable WHERE store_id AND Scraped_Urls = '1' "
fi

count=$($db_cmd --execute "$sql" | sed 's/[^0-9]*//g' | awk '{printf("%s", $0)}')

echo "export count=$count" > $file
echo "current : $count, old: $old_count" > /tmp/$0.log
if [[ ! $count -gt $old_count ]] ; then
  pkill -f "firefox"
  pkill -f "geckodriver"
  kill 1
fi
[[ $count -gt $old_count ]]
