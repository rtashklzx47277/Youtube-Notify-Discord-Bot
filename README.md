# Discord Youtube 影片/直播通知機器人
這是一個簡單的機器人，可以追蹤特定Youtube頻道的動態，隨時傳送該頻道的新影片或新直播通知至Discord頻道
<br><br>

設定方法：
1. 填入`.env.example`中的所有欄位並重新命名為`.env`
    * DISCORD_TOKEN: `Discord Bot Token`
    * YOUTUBE_API_KEY: `Youtube API key`
<br><br>

2. 創建並啟動容器
    1. 開啟終端機或命令提示字元
    2. 移動至包含`docker-compose.yml`檔案的目錄
    3. 輸入`docker-compose up -d`指令
    4. 完成建置
<br><br>

3. 在Discord頻道中輸入
    * `!add <Youtube頻道ID>`: 新增追隨頻道
    * `!remove <Youtube頻道ID>`: 取消追隨頻道
    * `!help`: 顯示可用指令
<br><br>
