# m_itemlog
`m_itemlog` monitors how characters interact with items, specifically the frequency of actions/time.  This monitor may be used to detect item injection exploits such as NPC quest rewards, mail, trade, cart:storage:inventory, etc.

## Required Stored Procedure
`m_itemlog` interacts with the database using the stored procedure below.  You must create this stored procedure within your database, and provide `m_itemlog` a mssql account with related permissions, prior to running the monitor.  In the event your zone:database update frequency is not 12 minutes, it must be updated within the stored procedure prior to running the monitor.
```
# rocp_admin_itemlog_db
SELECT srcCharName,
  srcCharID,
  srcAccountID,
  Action FROM itemLog.dbo.ItemLog where logtime > DATEADD(minute, -@pollinterval, GETDATE())
```

## Example m_itemlog Logs
```
2020-05-29 23:07:31,360 Iteration complete, sleeping 720 seconds
2020-05-29 23:19:31,505 Character Koko is new, adding to itemlog_active
2020-05-29 23:19:31,506 Zodis                     item_drop            c:  1 h:  0 d:  1 w:  1
2020-05-29 23:19:31,506 Zodis                     item_pickup          c:  1 h:  0 d:  1 w:  1
2020-05-29 23:19:31,506 Zodis                     item_sold_npc        c:  1 h:  1 d:  1 w:  1
2020-05-29 23:19:31,507 Zodis                     zeny_npc             c:  2 h:  1 d:  2 w:  2
2020-05-29 23:19:31,508 Daisy                     item_consumed        c:  1 h:  1 d:  2 w:  2
2020-05-29 23:19:31,511 Koko                      item_pickup          c:  2 h:  2 d:  2 w:  2
```
