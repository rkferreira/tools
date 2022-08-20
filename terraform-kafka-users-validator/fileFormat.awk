#!/usr/bin/awk -f

BEGIN {
  print "- Begining file validation..."
  FS="="
  RS="(\}|\},)"
}
{ 
  print "=========== START =========================="
  print "-- Processing: " $0" "
  print "-- Object name is the first field"
  objName = $1
  gsub(/([[:space:]]|\")/, "", objName)
  username = $3
  gsub(/([[:space:]]|\")/, "", username)
  gsub(/,[[:alpha:]].*/, "", username)
  if ($2 ~ /username/) {
    print "--- checking if username is equal to object name"
    #DEBUG print "--- username: "username
    #DEBUG print "--- objName: "objName
    if (username == objName) {
      print "---- its valid, proceed"
    } else {
      print "---- Error: "username" "objName
      if (objName != "myexception") {
        arrErr[NR] = objName
      }
    }
    print "=========== END =========================="
  } else {
    print "not username" $2
  }
}
END {
  print "Finalizing..."
  if (length(arrErr) > 0) {
    print "=========== E R R O R  ==================="
    for (i in arrErr) {
      print "error at: " arrErr[i]
    }
    print ""
    exit 1
  }
  print ""
}
