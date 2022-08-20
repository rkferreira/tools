#!/usr/bin/awk -f

BEGIN {
  print "Starting..."
}
/username/ {
  username = $3
  gsub(/[[:space:]\"]/, "", username)
  #DEBUG print username
  if (arr[username]++) {
    print "Duplicated: "username
    arrErr[username] = username
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
