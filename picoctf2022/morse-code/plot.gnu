set datafile separator ','
plot "<(head --lines 10000 morse_chal.csv)" using 1:2 with dots
