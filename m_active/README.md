# m_active

## Required Stored Procedure
`m_active` interacts with the database using the stored procedure below.  You must create this stored procedure within your database, and provide `m_active` a mssql account with related permissions, prior to running the monitor.
```
# Stored Procedure rocp_admin_charinfo_db
SELECT CharName,
  mapname,
  xPos,
  yPos,
  GID,
  AID,
  job,
  clevel,
  joblevel,
  jobpoint,
  sppoint,
  exp,
  jobexp,
  money from character.dbo.charinfo
```

## Example m_active output
```
2020-05-29 23:18:48,380 Iteration complete, sleeping 720 seconds
2020-05-29 23:30:48,519 Artea                     High Priest     cmd_fild01.gat (301,218)  blv: 91 jlv: 59 bpts:  9 jpts:  5 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,520 Koko                      Alchemist       prt_maze01.gat (18,57)    blv: 82 jlv: 31 bpts:  3 jpts:  0 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,523 Zodis                     Magician        geffen.gat (120,60)       blv: 65 jlv: 50 bpts:  1 jpts:  0 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,524 Daisy                     Merchant        cmd_fild01.gat (132,269)  blv: 57 jlv: 42 bpts:  7 jpts:  6 c:  3 h:  2 d:  3 w:  3
```
