#!/bin/csh -f 
#
if( $#argv < 1 ) then
echo {$0}': wrong arguments' $#argv
exit 1
endif
set ft4=$1
set xphase=0

echo '##########' conversion from spectrometer format to nmrPipe format $FID to $ft4
set range=`echo | gawk 'BEGIN{printf "-x1 %gppm -xn %gppm ",'{$FST_PNT_PPM}','{$FST_PNT_PPM}'-'{$ROISW}';   }'`

set fid=${FID}/ser
if( ! -f $fid ) set fid=${FID}
if( ! -f $fid ) then
 echo 'No fid file' $fid
 exit 1
endif

bruk2pipe -in $fid -bad 0.0 -noswap -DMX -decim 2560 -dspfvs 20 -grpdly 67.9842376708984 \
-xN       	1024      	-yN       	1024      	 \
-xT       	512       	-yT       	512       	 \
-xMODE    	Complex   	-yMODE    	Echo-AntiEcho	 \
-xSW      	7812.500  	-ySW      	24154.589 	 \
-xOBS     	600.130   	-yOBS     	150.902   	 \
-xCAR     	4.703     	-yCAR     	80.000    	 \
-xP0      	216.5     	-yP0      	 90.0     	 \
-xP1      	-90.0     	-yP1      	  0.0     	 \
-xLAB     	1H        	-yLAB     	13C       	 \
-ndim 2	-aq2D States \
| nmrPipe -fn POLY -time                               \
| nmrPipe -fn SP -off 0.48 -end 0.95 -pow 2 -c 0.5     \
| nmrPipe -fn ZF -auto                                 \
| nmrPipe -fn FT -auto                                 \
| nmrPipe -fn PS -hdr                                  \
| nmrPipe -fn PS -p0 0 -p1 0 -di                       \
| nmrPipe -fn POLY -auto -xn 5.0ppm -ord 1              \
| nmrPipe  -fn EXT $range  -sw \
# | pipe2xyz -z -out ft/data%03d.DAT -ov -nofs -verb \
# catching pipe into file \
> $ft4

echo Pipe streem '(XYZA)' $ft4 is ready
exit 0
