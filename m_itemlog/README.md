# m_itemlog


## Required Stored Procedure
`m_itemlog` interacts with the database using the stored procedure below.  You must create this stored procedure within your database, and provide `m_itemlog` a mssql account with related permissions, prior to running the monitor.
```
# rocp_admin_itemlog_db
SELECT srcCharName,
  srcCharID,
  srcAccountID,
  Action FROM itemLog.dbo.ItemLog where logtime > DATEADD(minute, -12, GETDATE())
```
