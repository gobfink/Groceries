#! /bin/bash
function usage() {
  echo "Usage: $0 -s <storename> -l {location} -m <url|[grocery]>"
}
mode=grocery
while getopts ":h:s:l:m:" opt; do
  case ${opt} in
    h)
      usage
      exit
      ;;
    s)
      store=${OPTARG}
      ;;
    l)
      location=${OPTARG}
      ;;
    m)
      mode=${OPTARG}
      ;;
    *)
      usage
      exit
      ;;
  esac
done

if [ -z "$store" ] ; then
  usage
  echo "Store must be set"
  exit
fi

file=/tmp/$mode
echo "Running $0 $@ " > /tmp/healthcheck.log
if [ -f $file ] ; then
  source $file
fi

if [[ "$count" == "" ]] ; then
  old_count=0
else
  old_count=$count
fi

db_cmd="mysql --host=db --user=root --password=example --database=groceries"

store_id_query="SELECT id FROM storeTable WHERE name = '$store'"
[ "$location" ] && store_id_query="$store_id_query AND location = '$location'"

store_id=$($db_cmd --execute "$store_id_query" | sed 's/[^0-9]*//g' | awk '{printf("%s", $0)}')
echo "attempt 1 - store_id: $store_id, with store_id_query: $store_id_query" >> /tmp/healthcheck.log
# If we don't have any results, substitute out the _'s for space's and try again
if [ -z "$store_id" ] ; then
  store_id_query="${store_id_query//_/ }"
  store_id=$($db_cmd --execute "$store_id_query" | sed 's/[^0-9]*//g' | awk '{printf("%s", $0)}')
  echo "attempt 2 - store_id: $store_id, with store_id_query: $store_id_query" >> /tmp/healthcheck.log
fi

sql="SELECT COUNT(*) FROM groceryTable WHERE store_id = '$store_id' "
if [[ $mode == "url" ]] ; then
  sql=${sql/groceryTable/urlTable}
  sql="$sql AND Scraped_Urls = AND Scraped_Urls = '1' "
fi

count=$($db_cmd --execute "$sql" | sed 's/[^0-9]*//g' | awk '{printf("%s", $0)}')

echo "export count=$count" > $file
echo "current : $count, old: $old_count" >> /tmp/healthcheck.log
echo "sql: $sql" >> /tmp/healthcheck.log
if [[ ! $count -gt $old_count ]] ; then
  pkill -f "firefox"
  pkill -f "geckodriver"
  pkill -f "chrom"
  kill 1
fi
[[ $count -gt $old_count ]]
