
@echo off
FOR /L %%A IN (1, 1, 6) DO (    
    start cmd /k python Peer.py 127.0.1.1 %%A    
)
pause