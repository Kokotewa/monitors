# m_itemlog

```
# rocp_admin_itemlog_db
SELECT srcCharName,
  srcCharID,
  srcAccountID,
  Action FROM itemLog.dbo.ItemLog where logtime > DATEADD(minute, -12, GETDATE())
```
