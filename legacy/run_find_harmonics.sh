#!/bin/tcsh -f

set pwd_dir = `pwd`

#set pydir = "/data/seis01/taira/Anaconda_x86_linux_py3_rev/envs/ssaf_rec"
#set pydir = "/data/seis01/taira/miniconda3/envs/netops"
set pydir = "/ref/bsl/taira/Operations/miniconda3/envs/wqc" 

# URAP
#set pydir = "/work/suture/taira/URAP/repeating-earthquake/miniconda3/envs/repeating-earthquake"

setenv PYTHONPATH $pydir
alias python $pydir'/bin/python'
which python



#swc -S dart -o test.ms -f 2025.198,00:00 -s 1d WTWN.BK.BHN.00
#swc -S dart -o test.ms -f 2025.198,00:00 -s 1d BKS.BK.BHZ.00
#swc -S dart -o test.ms -f 2025.198,00:00 -s 1d WTWN.BK.BHE.00
#swc -S dart -o test.ms -f 2025.198,00:00 -s 1d WTWN.BK.BHZ.00


foreach year (2025)
#foreach year (2004)
#foreach year (2024)
#foreach year (2015)
#foreach year (2020) # 4E
#foreach year (2020)

#foreach doy (238)
#foreach doy (239)
#foreach doy (247)
#foreach doy (252)
#foreach doy (260)
#foreach doy (259 261)
#foreach doy (261)
#foreach doy (259 260 261)
#foreach doy (255 256 257 258)
#foreach doy (269)
#foreach doy (281)
#foreach doy (282)
#foreach doy (283)
#foreach doy (314)
#foreach doy (313)
#foreach doy (314 290)

#foreach doy (270)
#foreach doy (324)
#foreach doy (324)

#foreach doy (356 357 358 359)
foreach doy (357)
#foreach doy (358)

#foreach doy (006 007 008 009 010 011 012)

#[noise:/home/bsl/taira/hydro/Instrumentation/python_work 63] caldate 2004/09/28
#2004.272,00:00:00.0000
#foreach doy (272)


#VALB  BK LP1 40 2020.309 00:00:00.0695 2020.309 23:59:59.0695
#foreach doy (309)

#foreach doy (211 212)

#foreach doy (199)
#foreach doy (198)
#foreach doy (197 199 200)

#[suture:/data/seis01/taira/Instrumentation/python_work/harmonics/work/Spectrograms 53] caldate 2025/02/25
#2025.056,00:00:00.0000
#foreach doy (056)

#[suture:/data/seis01/taira/Instrumentation/python_work 43] caldate  2024/12/05
#2024.340,00:00:00.0000
#foreach doy (340) # 1R
#foreach doy (364) # 4E
#foreach sta (WTWN)
#foreach sta (BKS)

#foreach sta (JCC)
#foreach sta (BUCR)
#foreach sta (RCAN)
#foreach sta (PACP)
#foreach sta (KETL)
#foreach sta (BUCR)
#foreach sta (MKOF)
#foreach sta (VALB)
#foreach sta (CMSB)
#foreach sta (CCRB SCYB)

#foreach sta (PORGT)
#foreach sta (PORG)
#foreach sta (BDM)
#foreach sta (SM2B)
#foreach sta (PKD)

#foreach sta (CCRB)

#foreach sta (KETL)
#foreach sta (SCYB)
#foreach sta (BKS)
#foreach sta (MBARI)

#foreach sta (CMB GASB HOPS MHC MNRC SAO YBH)
#[suture:/home/bsl/taira/hydro/Instrumentation/python_work/harmonics/work/Spectrograms 115] cat ~/dc6_doc/BK.info/BK.channel.summary.day  | grep HHZ | grep 3000 | awk '{printf("%s ",$1);}'
#AASB ADAM ALVW AONC ATP AUSC AVSP AZUL BABI BAKR BARR BAYL BCCR BDM BEVN BIGM BIGV BITR BJES BKFS BKS BL67 BLAS BLCR BLUE BONV BOYR BRAD BRIB BRIC BRIT BRK BTVR BUCI BUCR CCOR CGRV CLRV CMB DCMP DIAZ DLIK DMOR DRDG DRYC EAGL ETSL FARB FORD GALB GASB GCKB GHOP GRPK GTSB GUMB HALS HAPY HAS2 HATC HAYF HELL HOPS HRCH HULI HULL HUNT JASP JCC JEPS JEWT KARE KETL KNEE KRUG LAKN LAND LCOS LCOW LCUV LEGD LGMB LIND LITV LLNL LSIB LTIB MBARI MCCM MERC MHC MILL MKOF MLKN MMI MNDO MNLT MNRC MOD MOGU MORK MTOS MZTA OAKV ORRS ORV OVRO PABC PACP PATT PBDB PESC PETL PETY PINL PKD PORC PORG PRDS PVSP PVSP PWAY PWOD QRDG RAMR RAVE RBOW RCAN RIMR ROMB RUSS RVIT RVRP SAGE SANG SAO SBAR SCOT SCZ SEIA SFRE SHEP SHWD SIGP SKGS SNCR SPAN SPRL STRA SUGR SUTB SWNM TCHL TESL THIS THOM TOLH TRIN TSCN TULE TUMY TWIT UKON UMUN USAL VAK WEAV WEBR WELL WENL WHCL WHMT WINE WLKR WROK WSRE WTWN YBH YBH YUBA [suture:/home/bsl/taira/hydro/Instrumentation/python_work/harmonics/work/Spectrograms 116] 
# all sta
#foreach sta (AASB ADAM ALVW AONC ATP AUSC AVSP AZUL BABI BAKR BARR BAYL BCCR BDM BEVN BIGM BIGV BITR BJES BKFS BKS BL67 BLAS BLCR BLUE BONV BOYR BRAD BRIB BRIC BRIT BRK BTVR BUCI BUCR CCOR CGRV CLRV CMB DCMP DIAZ DLIK DMOR DRDG DRYC EAGL ETSL FARB FORD GALB GASB GCKB GHOP GRPK GTSB GUMB HALS HAPY HAS2 HATC HAYF HELL HOPS HRCH HULI HULL HUNT JASP JCC JEPS JEWT KARE KETL KNEE KRUG LAKN LAND LCOS LCOW LCUV LEGD LGMB LIND LITV LLNL LSIB LTIB MBARI MCCM MERC MHC MILL MKOF MLKN MMI MNDO MNLT MNRC MOD MOGU MORK MTOS MZTA OAKV ORRS ORV OVRO PABC PACP PATT PBDB PESC PETL PETY PINL PKD PORC PORG PRDS PVSP PVSP PWAY PWOD QRDG RAMR RAVE RBOW RCAN RIMR ROMB RUSS RVIT RVRP SAGE SANG SAO SBAR SCOT SCZ SEIA SFRE SHEP SHWD SIGP SKGS SNCR SPAN SPRL STRA SUGR SUTB SWNM TCHL TESL THIS THOM TOLH TRIN TSCN TULE TUMY TWIT UKON UMUN USAL VAK WEAV WEBR WELL WENL WHCL WHMT WINE WLKR WROK WSRE WTWN YBH YUBA )
#foreach sta (BKS)
#foreach sta (FARB)
foreach sta (PORG RCAN)
#foreach sta (MBARI FORD )

#foreach sta (AASB ADAM ALVW AONC ATP AUSC AVSP AZUL BABI BAKR BARR BAYL BCCR BDM BEVN BIGM BIGV BJES BKS BL67 BLAS BLCR BLUE BONV BOYR BRAD BRIB BRIC BRIT BRK BUCI BUCR CCOR CGRV CLRV CMB DCMP DIAZ DLIK DMOR DRDG DRYC EAGL ETSL FARB FORD GALB GASB GCKB GHOP GRPK GTSB GUMB HALS HAPY HAS2 HATC HAYF HELL HOPS HRCH HULI HULL HUNT JASP JCC JEPS JEWT KARE KETL KNEE KRUG LAKN LAND LCOS LCOW LCUV LEGD LGMB LIND LITV LLNL LSIB LTIB MBARI MCCM MERC MHC MILL MKOF MLKN MMI MNDO MNLT MNRC MOD MOGU MTOS MZTA OAKV ORRS ORV OVRO PABC PACP PATT PBDB PESC PETL PETY PINL PKD PORC PRDS PVSP PVSP PWAY PWOD QRDG RAMR RAVE RBOW RIMR ROMB RUSS RVIT RVRP SAGE SANG SAO SBAR SCOT SCZ SEIA SFRE SHEP SHWD SIGP SKGS SNCR SPAN SPRL SUGR SUTB SWNM TCHL TESL THIS THOM TOLH TRAM TRIN TSCN TULE TUMY TWIT UKON UMUN USAL VAK WEAV WEBR WELL WENL WHCL WHMT WINE WLKR WROK WSRE YBH YUBA )


#foreach sta (MONT)
#foreach sta (9410)
#foreach sta (9410 MONT)

#foreach sta (P100 WTWN)
#foreach sta (P100)
#foreach sta (WTWN)
#foreach sta (FARB)
#foreach sta (MHC MBARI FORD)
#foreach sta (MB01)
#foreach sta (MB02 MB03 MB04)
#foreach sta (MB01 MB02 MB03 MB04)
#foreach sta (BH05)
#foreach sta (BH05 BH06)
#foreach sta (BH15)
#foreach sta (L013)
#foreach sta (L014 L015 L016)
#foreach sta (MBARI)


#foreach com (BHZ BHN BHE)

#foreach com ( HHZ HHN HHE)
#foreach com (HNZ HNN HNE)

# def
#foreach com ( HHZ HHN HHE HNZ HNN HNE)

foreach com (HHZ)
#foreach com (LHZ)
#foreach com ( EP1 HN1 HN2 HN3)

#foreach com ( DP1 DP2 DP3)
#foreach com (DP1)
#foreach com ( CN1 CN2 CN3)
#foreach com ( DP1 CN1 CN2 CN3)

#foreach com (HHZ)
#foreach com (HHE)
#foreach com (RES)
#foreach com (DPZ DPN DPE)
#foreach com (DPZ)
#foreach com (DPN DPE)

set winlen = 600
# def
set winlen = 1200 # 20min

#set stw = "1d"
set stw = "3d"
set stw = "5d"

# storm
#set winlen = 10800 # 3 hour
#set winlen = 21600 # 6 hour


set vmin = -200
set vmax = -100

#set vmin = -160
#set vmax = -140

set net = "BK"
set loc = "00"

if ($com == "HN1" || $com == "HN2"  | $com == "HN3" ) then
set vmin = -160
set vmax = -60
endif # if  ($com == "HN1" || $com == "HN2"  | $com == "HN3" ) then


if ($com == "EP1" || $com == "EP2"  | $com == "EP3" ) then
set vmin = -160
set vmax = -60
endif # if ($com == "EP1" || $com == "EP2"  | $com == "EP3" ) then

if ($com == "DP1" || $com == "DP2"  | $com == "DP3" ) then
set vmin = -160
set vmax = -60
endif

endif #if ($com == "DP1" || $com == "DP2"  | $com == "DP3" ) then

if ($com == "HNZ" || $com == "HNN"  | $com == "HNE" ) then
set vmin = -160
set vmax = -60
endif #  if  ($com == "HNZ" || $com == "HNN"  | $com == "HNE" ) then


if($sta == "PKD") then
if($year == "2004") then
set loc = ""
endif 
endif


if ($sta == "FARB"  ) then
# 15min =  900 sec, 1.111111e-03 Hz -> 1.11 mHz
# 90min = 5400 sec 1.851852e-04 Hz -> 0.18 mHz
set winlen =  6000 #sec 100min 1h40min
set winlen = 12000 #sec 200min 3h20min
endif

if ($sta == "L013" || $sta == "L014"  | $sta == "L015"  | $sta == "L016" ) then
set net = "4E"

set vmin = -160
set vmax = -80

set winlen = 120
endif # if ($sta == "MB01") then




if ($sta == "MB01" || $sta == "MB02" || $sta == "MB03" || $sta == "MB04") then
set net = "1R"

set vmin = -160
set vmax = -80

set winlen = 120

endif # if ($sta == "MB01") then


if ($sta == "BH04" || $sta == "BH05" || $sta == "BH06" || $sta == "BH15"  ) then
set net = "1R"

set vmin = -160
set vmax = -80

set winlen = 120

endif # if ($sta == "MB01") then

 
if ($sta == "TRIN" || $sta == "SUTB" || $sta == "SHEP"  || $sta == "SCOT" || $sta == "DCMP" || $sta == "BRIB"  || $sta == "RAMR"  || $sta == "MTOS" ) then
set loc = "01" # location    
endif


 
if ($sta == "VALB" ) then
set loc = "40" # location    
endif

 
if ($sta == "CCRB" ) then
set loc = "40" # location   
set net = "BP"
endif

if ($sta == "SCYB" ) then
set loc = "40" # location   
set net = "BP"
endif
 
if ($sta == "SMNB" ) then
set loc = "40" # location   
set net = "BP"
endif



if ($sta == "CMSB" ) then
if ($com == "DP1" || $com == "DP2"  | $com == "DP3" ) then
set loc = "40" # location    
endif
endif

if ($sta == "SM2B" ) then
set loc = "40" # location    
endif


if ($net == "BP") then
set vmin = -180
set vmax = -80
endif

echo "# sta = "$sta" net = "$net" com = "$com" loc = "$loc

#pwd
#exit

# dart first
swc -S dart -o test.ms -f $year"."$doy",00:00" -s $stw $sta"."$net"."$com"."$loc
set ms_wc = `wc test.ms | awk '{print $1}'`

if($ms_wc == 0) then
echo "# "swc -o test.ms -f $year"."$doy",00:00" -s $stw $sta"."$net"."$com"."$loc
swc -o test.ms -f $year"."$doy",00:00" -s $stw $sta"."$net"."$com"."$loc
endif

if ($sta == "SM2B" ) then
set loc = "40" # location    
swc -S dart -o test.ms -f $year"."$doy",19:00" -s $stw $sta"."$net"."$com"."$loc

endif



if($sta == "P100") then
set loc = ""
set net = "HM"
#cp -f "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/HM."$sta".."$com".D.2025.198" test.ms

#set org_ms = "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/"$sta".HM."$com"..D.2025.198.001931"
set org_ms = "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/cut.ms"
#set org_ms = "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/cut.lp20.40sps.ms"

#qmerge -f 2025.198,00:19:40.0000 -t 2025.198,14:15:00.0000 -o test.ms $org_ms
cp -f $org_ms test.ms
endif

if($sta == "PORGT") then
set loc = "01" # location    

#7048 -rw-r--r-- 1 taira users  7217152 Oct  8 14:56 PORGT.BK.HHE.01.D.2025.281.004710
#5888 -rw-r--r-- 1 taira users  6029312 Oct  8 14:57 PORGT.BK.HHZ.01.D.2025.281.004710
#6636 -rw-r--r-- 1 taira users  6795264 Oct  8 14:57 PORGT.BK.HHN.01.D.2025.281.004710

#set org_ms = "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/cut.ms"
set org_ms = "/home/bsl/taira/hydro/Instrumentation/python_work/PORG/PORGT.BK."$com".01.D.2025.281.004710"
cp -f $org_ms test.ms

#pwd
#exit
endif

if($sta == "PORGX") then


#23416 -rw-r--r-- 1 taira users 23977984 Oct  8 18:21 PORG.BK.HHE.00.D.2025.281.011000
#23416 -rw-r--r-- 1 taira users 23977984 Oct  8 18:21 PORG.BK.HHN.00.D.2025.281.011000
#23416 -rw-r--r-- 1 taira users 23977984 Oct  8 18:21 PORG.BK.HHZ.00.D.2025.281.011000

#set org_ms = "/data/seis01/taira/Instrumentation/python_work/WTWN/2025/HM/"$sta"/"$com".D/cut.ms"
set org_ms = "/home/bsl/taira/hydro/Instrumentation/python_work/PORG/PORG.BK."$com".00.D.2025.281.011000"
cp -f $org_ms test.ms

#pwd
#exit
endif



#pwd
#exit

if($net == "1R") then
# MB nodal
#set msdir = "/ref/noise01/taira/MBNodal/20250205_MBARI_nodel_miniseed"
# BH nodal
set msdir = "/work/seis03/taira/BHNodal"




# Feb25
#[suture:/ref/noise01/taira/MBNodal/20250205_MBARI_nodel_miniseed 44] ls *2025.02.25*
#453012166.0021.2025.02.25.00.00.00.000.E.miniseed  453012446.0021.2025.02.25.00.00.00.000.E.miniseed  453014020.0021.2025.02.25.00.00.00.000.E.miniseed  453019453.0021.2025.02.25.00.00.00.000.E.miniseed
#453012166.0021.2025.02.25.00.00.00.000.N.miniseed  453012446.0021.2025.02.25.00.00.00.000.N.miniseed  453014020.0021.2025.02.25.00.00.00.000.N.miniseed  453019453.0021.2025.02.25.00.00.00.000.N.miniseed
#453012166.0021.2025.02.25.00.00.00.000.Z.miniseed  453012446.0021.2025.02.25.00.00.00.000.Z.miniseed  453014020.0021.2025.02.25.00.00.00.000.Z.miniseed  453019453.0021.2025.02.25.00.00.00.000.Z.miniseed
#MB01	36.585833	-121.910556	129.17	2025-02-05 16:50	453012166
#MB02	36.816944	-121.660000	129.84	2025-02-05 17:50	453014020
#MB03	36.994444	-121.851111	124.09	2025-02-05 18:50	453019453
#MB04	36.951111	-122.051111	15.00	2025-02-05 19:40	453012446

echo "# sta = "$sta" com = "$com
if($sta == "MB01" && $com == "DPZ") then
set fi = "453012166.0021.2025.02.25.00.00.00.000.Z.miniseed"
endif

if($sta == "MB01" && $com == "DPN") then
set fi = "453012166.0021.2025.02.25.00.00.00.000.N.miniseed"
endif

if($sta == "MB01" && $com == "DPE") then
set fi = "453012166.0021.2025.02.25.00.00.00.000.E.miniseed"
endif

if($sta == "MB02" && $com == "DPZ") then
set fi = "453014020.0021.2025.02.25.00.00.00.000.Z.miniseed"
endif

if($sta == "MB02" && $com == "DPN") then
set fi = "453014020.0021.2025.02.25.00.00.00.000.N.miniseed"
endif

if($sta == "MB02" && $com == "DPE") then
set fi = "453014020.0021.2025.02.25.00.00.00.000.E.miniseed"
endif


if($sta == "MB03" && $com == "DPZ") then
set fi = "453019453.0021.2025.02.25.00.00.00.000.Z.miniseed"
endif

if($sta == "MB03" && $com == "DPN") then
set fi = "453019453.0021.2025.02.25.00.00.00.000.N.miniseed"
endif

if($sta == "MB03" && $com == "DPE") then
set fi = "453019453.0021.2025.02.25.00.00.00.000.E.miniseed"
endif


if($sta == "MB04" && $com == "DPZ") then
set fi = "453012446.0021.2025.02.25.00.00.00.000.Z.miniseed"
endif

if($sta == "MB04" && $com == "DPN") then
set fi = "453012446.0021.2025.02.25.00.00.00.000.N.miniseed"
endif

if($sta == "MB04" && $com == "DPE") then
set fi = "453012446.0021.2025.02.25.00.00.00.000.E.miniseed"
endif


#BH04 453014086.0018.2024.12.05.00.00.00.000.Z.miniseed  
#BH06 453020430.0018.2024.12.05.00.00.00.000.Z.miniseed
#453019351.0018.2024.12.05.00.00.00.000.Z.miniseed
if($sta == "BH04" && $com == "DPZ") then
set fi = "453014086.0018.2024.12.05.00.00.00.000.Z.miniseed"
endif
if($sta == "BH06" && $com == "DPZ") then
set fi = "453020430.0018.2024.12.05.00.00.00.000.Z.miniseed"
endif
if($sta == "BH05" && $com == "DPZ") then
set fi = "453019351.0018.2024.12.05.00.00.00.000.Z.miniseed"

# active source 
set fi = "453012668.0010.2025.04.14.00.00.00.000.Z.miniseed"

endif

# 
if($sta == "BH15" && $com == "DPZ") then
# when active sourc experiment
#BH15	N37° 52′ 33″	W122° 14′ 27″	860	04/04/2025 17:25:00	453012667	15/4/2025 17:28:00	
set fi = "453012667.0010.2025.04.14.00.00.00.000.Z.miniseed"
endif

set org_ms = $msdir"/"$fi
echo "# org_ms = "$org_ms
cp -f $org_ms test.ms

##Feb 25 2025 13:30 18:30
#qmerge -f 2025/02/25,13:30 -t 2025/02/25,18:30 -o test.ms $org_ms
#endif

endif # if($net == "1R") then


if($sta == "MONT") then
qmerge -T -f 2025.211,00:00:00 -t 2025.212,00:00:00 -o test.ms /data/seis01/taira/Instrumentation/python_work/Kamchatka_tsunami/mont_water_table/mont.ms

set vmin = -20
set vmax = 20

# 15min =  900 sec, 1.111111e-03 Hz -> 1.11 mHz
# 90min = 5400 sec 1.851852e-04 Hz -> 0.18 mHz
#set winlen =  6000 #sec 100min 1h40min
set winlen = 12000 #sec 200min 3h20min

# def for seismic
#set winlen = 1200 # 20min

set winlen = 3000 # 50min

endif

if($sta == "9410") then

cp -f /work/suture/taira/SeaFOAM/2025_Kamchatka_M8.33/strain_rate.cut.sac ./test.ms
#cp -f /work/suture/taira/SeaFOAM/2025_Kamchatka_M8.33/strain.cut.sac ./test.ms

set vmin = -190
set vmax = -160
set vmax = -170


# strain
#set vmin = -150
#set vmax = -130

# 15min =  900 sec, 1.111111e-03 Hz -> 1.11 mHz
# 90min = 5400 sec 1.851852e-04 Hz -> 0.18 mHz
#set winlen =  6000 #sec 100min 1h40min
set winlen = 12000 #sec 200min 3h20min

# def for seismic
#set winlen = 1200 # 20min

set winlen = 3000 # 50min

endif



#pwd
#exit

#python ./find_harmonics.py doc/testdata.mseed --winlen 600 --kind peak --fmin 0.1 --fmax 0.3
#python ./find_harmonics.py doc/WTWN.BK.BHZ.00.D.2025.199.000000 --vmin -200 --vmax -120 --winlen 600 --kind peak --fmin 3 --fmax 6


# --skip_hf
# storm
set fmin = 0.001
set fmin_plot = 0.1
set fmax_plot = 1.0

qmerge -nm ./test.ms

#pwd
#exit

set noCalc = 1
set noCalc = 0

if($noCalc) then
else
python ./find_harmonics.py ./test.ms --vmin $vmin --vmax $vmax --winlen $winlen --fmin $fmin  --fmin_plot $fmin_plot --fmax_plot $fmax_plot --skip_hf
endif # if($noCalc) then

end # com
end # sta
end # doy
end # year
