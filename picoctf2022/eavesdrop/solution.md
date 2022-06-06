# Solution

Let's have a look at the most common source-\>destination pairs:

``` console
$ tshark \
    -r capture.flag.pcap \
    -T fields \
    -e ip.src -e ip.dst \
    | grep --invert-match $'^\t$' \
    | sort | uniq -c | sort -nr
     22 10.0.2.15	10.0.2.4
     21 10.0.2.4	10.0.2.15
      5 35.224.170.84	10.0.2.15
      5 10.0.2.15	35.224.170.84
      2 10.0.2.15	10.0.2.1
      2 10.0.2.1	10.0.2.15
      1 10.0.2.3	10.0.2.15
      1 10.0.2.15	10.0.2.3
```

So it looks like there's a lot of chatter between `10.0.2.15` and `10.0.2.4`
Further inspecting, it appears there are only two pairs of ports used in the
exchanges between these hosts:

``` console
$ tshark \
    -r capture.flag.pcap \
    -T fields \
    -e ip.src -e ip.dst -e tcp.port \
    -- ip.dst == 10.0.2.4 \
    | sort | uniq 
10.0.2.15	10.0.2.4	56370,9002
10.0.2.15	10.0.2.4	57876,9001
```

Inspecting the exchange on port `9001`:

``` console
$ tshark \
    -r capture.flag.pcap \
    -T tabs \
    -- ip.dst == 10.0.2.4 and ip.src == 10.0.2.15 and tcp.port == 9001
    5	 15.175413	   10.0.2.15	→	10.0.2.4    	TCP	74	57876 → 9001 [SYN] Seq=0 Win=64240 Len=0 MSS=1460 SACK_PERM=1 TSval=3517230404 TSecr=0 WS=128
    7	 15.176456	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=1 Ack=1 Win=64256 Len=0 TSval=3517230405 TSecr=1765680570
   13	 31.182202	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=1 Ack=42 Win=64256 Len=0 TSval=3517246411 TSecr=1765696576
   14	 38.502063	   10.0.2.15	→	10.0.2.4    	TCP	82	57876 → 9001 [PSH, ACK] Seq=1 Ack=42 Win=64256 Len=16 TSval=3517253731 TSecr=1765696576
   17	 48.150305	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=17 Ack=60 Win=64256 Len=0 TSval=3517263379 TSecr=1765713544
   18	 97.822725	   10.0.2.15	→	10.0.2.4    	TCP	149	57876 → 9001 [PSH, ACK] Seq=17 Ack=60 Win=64256 Len=83 TSval=3517313052 TSecr=1765713544
   25	107.903169	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=100 Ack=79 Win=64256 Len=0 TSval=3517323132 TSecr=1765773297
   26	121.932953	   10.0.2.15	→	10.0.2.4    	TCP	113	57876 → 9001 [PSH, ACK] Seq=100 Ack=79 Win=64256 Len=47 TSval=3517337162 TSecr=1765773297
   29	134.662230	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=147 Ack=130 Win=64256 Len=0 TSval=3517349891 TSecr=1765800056
   30	141.449380	   10.0.2.15	→	10.0.2.4    	TCP	76	57876 → 9001 [PSH, ACK] Seq=147 Ack=130 Win=64256 Len=10 TSval=3517356678 TSecr=1765800056
   33	145.480560	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=157 Ack=135 Win=64256 Len=0 TSval=3517360710 TSecr=1765810874
   34	149.866335	   10.0.2.15	→	10.0.2.4    	TCP	72	57876 → 9001 [PSH, ACK] Seq=157 Ack=135 Win=64256 Len=6 TSval=3517365095 TSecr=1765810874
   37	163.189875	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=163 Ack=176 Win=64256 Len=0 TSval=3517378419 TSecr=1765828583
   48	182.468120	   10.0.2.15	→	10.0.2.4    	TCP	91	57876 → 9001 [PSH, ACK] Seq=163 Ack=176 Win=64256 Len=25 TSval=3517397697 TSecr=1765828583
   53	197.944369	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=188 Ack=193 Win=64256 Len=0 TSval=3517413173 TSecr=1765863336
   59	212.168371	   10.0.2.15	→	10.0.2.4    	TCP	74	57876 → 9001 [PSH, ACK] Seq=188 Ack=193 Win=64256 Len=8 TSval=3517427397 TSecr=1765863336
   65	227.004032	   10.0.2.15	→	10.0.2.4    	TCP	66	57876 → 9001 [ACK] Seq=196 Ack=201 Win=64256 Len=0 TSval=3517442233 TSecr=1765892395
   72	239.414765	   10.0.2.15	→	10.0.2.4    	TCP	86	57876 → 9001 [PSH, ACK] Seq=196 Ack=201 Win=64256 Len=20 TSval=3517454644 TSecr=1765892395
```

The most interesting frames are the \[`PSH, ACK`\] ones. Let's look at the
payload for each of these:

``` console
$ tshark \
    -r capture.flag.pcap \
    -T fields \
    -e tcp.payload \
    -- ip.addr == 10.0.2.15 and tcp.port == 9001 and tcp.flags.push == "1"  \
    | xxd -revert -plain
Hey, how do you decrypt this file again?
You're serious?
Yeah, I'm serious
*sigh* openssl des3 -d -salt -in file.des3 -out file.txt -k supersecretpassword123
Ok, great, thanks.
Let's use Discord next time, it's more secure.
C'mon, no one knows we use this program like this!
Whatever.
Hey.
Yeah?
Could you transfer the file to me again?
Oh great. Ok, over 9002?
Yeah, listening.
Sent it
Got it.
You're unbelievable
```

So it looks like the exchange on port `9002` was a file transfer, let's check
that:

``` console
$ tshark \
    -r capture.flag.pcap \
    -T fields \
    -e tcp.payload \
    -- ip.addr == 10.0.2.15 and tcp.port == 9002 and tcp.flags.push == "1"  \
    | xxd -revert -plain | file -
/dev/stdin: openssl enc'd data with salted password
```

So it's an encoded file, but from the conversation above we are able to decrypt
this via:

``` 
tshark \
    -r capture.flag.pcap \
    -T fields \
    -e tcp.payload \
    -- ip.addr == 10.0.2.15 and tcp.port == 9002 and tcp.flags.push == "1"  \
    | xxd -revert -plain \
    | openssl des3 -d -salt -in /dev/stdin -out /dev/stdout -k supersecretpassword123
```
