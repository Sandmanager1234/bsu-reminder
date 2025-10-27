# Telegram bot for notify about lessons

@bsu_reminder_bot

## Usage

1. Enter /start in bot
   ![1761590105532](image/README/1761590105532.png)
2. Chose your group
   ![1761590178544](image/README/1761590178544.png)
3. Set notification settings
   ![1761590198940](image/README/1761590198940.png)
4. Enjoy

## Deploy

1. Clone repository

   ```
   git clone https://github.com/Sandmanager1234/bsu-reminder
   ```
2. Build project

   ```
   docker compose build
   ```
3. Create db with migrations

   ```
   docker compose run --rm bot alembic upgrade head
   ```
4. Up project

   ```
   docker compose up -d
   ```
