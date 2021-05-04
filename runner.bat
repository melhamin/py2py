
@echo off
FOR /L %%A IN (1, 1, 3) DO (    
    start cmd /k python Peer.py %%A    
)
pause