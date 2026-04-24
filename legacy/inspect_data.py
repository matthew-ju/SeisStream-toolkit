import obspy
data_file = "RVIT.BK.HHZ.00.D.2026.001"
st = obspy.read(data_file)
print(st)
for tr in st:
    print(tr.stats)
