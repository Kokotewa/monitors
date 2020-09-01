# m_active
`m_active` monitors how frequency characters are active by comparing their last recorded (experience, zeny, map_position) against their previously recorded (experience, zeny, map_position).  In the event that these values differ, the character is considered active.  In the event that they are the same, the character is considered inactive.  This monitor may be used to detect automated characters which are active for prolonged periods of time.

## Required Stored Procedure
`m_active` interacts with the database using the stored procedure below.  You must create this stored procedure within your database, and provide `m_active` a mssql account with related permissions, prior to running the monitor.
```
# rocp_admin_charinfo_db
SELECT CharName,
  mapname,
  xPos,
  yPos,
  GID,
  character.AID,
  character.job,
  clevel,
  joblevel,
  jobpoint,
  sppoint,
  exp,
  jobexp,
  money FROM character.dbo.charinfo character INNER JOIN nLogin.dbo.account
  ON nLogin.dbo.account.AID=character.AID
```

## Example m_active Logs
```
2020-05-29 23:18:48,380 Iteration complete, sleeping 720 seconds
2020-05-29 23:30:48,519 Artea                     High Priest     cmd_fild01.gat (301,218)  blv: 91 jlv: 59 bpts:  9 jpts:  5 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,520 Koko                      Alchemist       prt_maze01.gat (18,57)    blv: 82 jlv: 31 bpts:  3 jpts:  0 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,523 Zodis                     Magician        geffen.gat (120,60)       blv: 65 jlv: 50 bpts:  1 jpts:  0 c:  3 h:  2 d:  3 w:  3
2020-05-29 23:30:48,524 Daisy                     Merchant        cmd_fild01.gat (132,269)  blv: 57 jlv: 42 bpts:  7 jpts:  6 c:  3 h:  2 d:  3 w:  3
```
