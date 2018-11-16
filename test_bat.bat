@echo off
start /B python calculateStaticRes.py --begin 0 --end 10
start /B python calculateStaticRes.py --begin 10 --end 20
start /B python calculateStaticRes.py --begin 20 --end 30
start /B python calculateStaticRes.py --begin 30 --end 40
start /B python calculateStaticRes.py --begin 40 --end 50
start /B python calculateStaticRes.py --begin 50 --end 60
start /B python calculateStaticRes.py --begin 60 --end 80
start /B python calculateStaticRes.py --begin 80 --end 100
start /B python calculateStaticRes.py --begin 100 --end 120
start /B python calculateStaticRes.py --begin 120 --end 140
pause